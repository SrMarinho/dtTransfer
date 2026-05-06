# Plano: Migração para Dagster

> **Status:** ✔️ Concluído — código implementado na branch `feat/dagster-orchestration`.
> Pendente deploy no servidor (Parte 1) e migração gradual (Parte 3). 
> O plano abaixo reflete o estado atual do código.

## Context

Hoje o pipeline é orquestrado por ~130 linhas de crontab (`docs/agendamentos_ETL.txt`) chamando `run.py` individualmente para cada tabela. Problemas:

- **Visibilidade zero**: sem UI, sem histórico de execuções, sem linha de tempo
- **Sem dependências entre tabelas**: `nf_compra` e `nf_compra_produtos` rodam no mesmo horário sem garantia de ordem
- **Sem backfill**: reprocessar um intervalo exige comandos manuais no servidor
- **Sem retry de job**: falha → silêncio. Só `error_check.py` percebe depois
- **Sem catálogo**: não existe registro de quando cada tabela foi atualizada pela última vez
- **Difícil de operar**: adicionar/remover tabela = editar crontab no servidor via SSH

**Solução**: Dagster OSS. O modelo de **software-defined assets** mapeia 1:1 com o projeto — cada entrada do `EntityRegistry._entities` vira um asset com linhagem, schedule e freshness policy. O `run.py` atual é preservado como executor; Dagster só decide quando e com que parâmetros chamá-lo.

### Constraints

- Servidor de produção: `/opt/nzretlconnect/biMktNaz`, usuário `nzretlconnect`, venv em `bimktnaz/`
- Dagster roda **embutido (SQLite)** — sem PostgreSQL de metadados como requisito inicial
- Migração **incremental e reversível**: crontab continua em paralelo até validação completa
- `run.py` e todos os processos ETL existentes **não são alterados**

---

## PARTE 1 — INFRAESTRUTURA

### 1.1 Pré-requisitos do servidor

**Python:** Dagster 1.9.x exige Python ≥ 3.9. O venv atual (`bimktnaz/`) já usa Python 3.9 (confirmado pelo `Dockerfile`). ✅

**Verificar na máquina:**
```bash
/opt/nzretlconnect/biMktNaz/bimktnaz/bin/python --version
# Esperado: Python 3.9.x ou superior

df -h /opt/nzretlconnect   # mínimo 2 GB livres para SQLite do Dagster + logs
free -h                    # mínimo 1 GB RAM disponível para daemon + webserver
```

**RAM estimada em uso:**
| Processo | RAM típica |
|----------|-----------|
| dagster-daemon | ~150–300 MB |
| dagster-webserver | ~200–400 MB |
| run ETL (subprocess) | ~50–150 MB por job ativo |
| **Total adicional** | **~500 MB–1 GB** |

Se o servidor tiver menos de 2 GB RAM disponível, rodar apenas o `dagster-daemon` (sem webserver permanente — subir webserver só quando precisar operar).

---

### 1.2 Firewall e acesso à UI

O webserver sobe na porta **3000**. Decidir a política de acesso antes de subir:

**Opção A — Acesso direto (rede interna):**
```bash
# Liberar porta 3000 apenas para a rede interna (ex: 192.168.1.0/24)
sudo ufw allow from 192.168.1.0/24 to any port 3000
# ou via iptables:
sudo iptables -A INPUT -p tcp --dport 3000 -s 192.168.1.0/24 -j ACCEPT
```

**Opção B — Nginx reverse proxy (recomendada para acesso externo):**

Instalar nginx e criar config em `/etc/nginx/sites-available/dagster`:

```nginx
server {
    listen 80;
    server_name dagster.suaempresa.com.br;   # ou IP do servidor

    # Redirecionar para HTTPS se tiver certificado
    # return 301 https://$host$request_uri;

    location / {
        proxy_pass         http://127.0.0.1:3000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";   # necessário para WebSocket (logs em tempo real)
        proxy_read_timeout 300s;
    }
}
```

```bash
sudo apt install nginx -y
sudo ln -s /etc/nginx/sites-available/dagster /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

**Autenticação básica (opcional mas recomendada):**

A UI do Dagster OSS não tem auth nativa. Adicionar HTTP Basic Auth via nginx:

```bash
sudo apt install apache2-utils -y
sudo htpasswd -c /etc/nginx/.dagster_htpasswd admin
```

Adicionar ao bloco `location /` do nginx:
```nginx
auth_basic "Dagster";
auth_basic_user_file /etc/nginx/.dagster_htpasswd;
```

> **Nota:** O webserver pode ficar inacessível externamente e ser acessado via **SSH tunnel** sem nginx, que é a opção mais simples e segura:
> ```bash
> ssh -L 3000:localhost:3000 usuario@servidor
> # Acesse http://localhost:3000 no seu navegador local
> ```

---

### 1.3 Variáveis de ambiente no contexto do systemd

**Problema crítico:** O crontab atual usa `source ~/.bashrc` antes de cada comando, carregando Oracle Instant Client (`LD_LIBRARY_PATH`, `NLS_LANG`), credenciais e outras envs. O **systemd não carrega `~/.bashrc`** — as variáveis precisam ser declaradas explicitamente no service.

O `python-dotenv` carrega o `.env` do projeto, cobrindo as credenciais dos bancos e `TELEGRAM_*`. Mas variáveis de sistema (Oracle, ODBC) precisam estar no service.

**Solução:** Usar `EnvironmentFile` no service apontando para o `.env` do projeto + declarar as variáveis de sistema:

```ini
[Service]
EnvironmentFile=/opt/nzretlconnect/biMktNaz/.env

# Oracle Instant Client — ajustar o path conforme instalação no servidor
Environment=LD_LIBRARY_PATH=/opt/oracle/instantclient_21_12
Environment=NLS_LANG=AMERICAN_AMERICA.AL32UTF8
Environment=TNS_ADMIN=/opt/oracle/instantclient_21_12/network/admin

# Dagster home
Environment=DAGSTER_HOME=/opt/nzretlconnect/biMktNaz/.local/dagster

# Timezone
Environment=TZ=America/Fortaleza
```

**Verificar quais envs o crontab carrega:**
```bash
# No servidor, inspecionar o que o ~/.bashrc exporta
grep -E "^export" ~/.bashrc
```

Tudo que aparecer com `export` e for usado pelo ETL deve estar no `EnvironmentFile` ou no bloco `Environment=` do service.

---

### 1.4 Oracle Instant Client

O subprocess chamado pelo Dagster precisa encontrar as libs do Oracle. Verificar se estão acessíveis sem `~/.bashrc`:

```bash
# Testar como o dagster-daemon chamaria o processo (sem .bashrc)
env -i HOME=/root PATH=/usr/bin:/bin \
  LD_LIBRARY_PATH=/opt/oracle/instantclient_21_12 \
  /opt/nzretlconnect/biMktNaz/bimktnaz/bin/python -c "import oracledb; print('ok')"
```

Se falhar, o `LD_LIBRARY_PATH` no service está errado. Ajustar o path até passar.

---

### 1.5 Estrutura de diretórios

Criar antes de subir os serviços:

```bash
# DAGSTER_HOME
mkdir -p /opt/nzretlconnect/biMktNaz/.local/dagster

# Confirmar permissões
chown -R nzretlconnect:nzretlconnect /opt/nzretlconnect/biMktNaz/.local/
```

O Dagster criará automaticamente dentro de `$DAGSTER_HOME`:
```
.local/dagster/
├── storage/              # SQLite com histórico de runs e eventos
│   ├── runs/
│   ├── event_log/
│   └── schedules/
└── dagster.yaml          # gerado automaticamente se não existir
```

---

### 1.6 Crescimento do SQLite e manutenção

O SQLite do Dagster acumula logs de eventos de cada run. Com 130+ assets rodando diariamente, cresce ~5–20 MB/dia. Sem manutenção, pode chegar a vários GB em meses.

**Configurar purge automático** em `dagster.yaml` (na raiz do projeto):

```yaml
telemetry:
  enabled: false

retention:
  schedule:
    purge_after_days: 90    # manter histórico de 90 dias
  sensor:
    purge_after_days: 90
  auto_materialize:
    purge_after_days: 90
```

**Backup do SQLite** (adicionar ao crontab existente):

```cron
# Backup do estado do Dagster — diário às 03h30
30 3 * * * sqlite3 /opt/nzretlconnect/biMktNaz/.local/dagster/storage/runs/runs.db ".backup /opt/nzretlconnect/biMktNaz/.local/backups/dagster-$(date +\%F).db" 2>/dev/null
# Limpar backups com mais de 30 dias
35 3 * * * find /opt/nzretlconnect/biMktNaz/.local/backups/ -name "dagster-*.db" -mtime +30 -delete
```

---

### 1.7 Concorrência e limites de execução

Sem configuração, o Dagster pode tentar materializar centenas de assets em paralelo, sobrecarregando os bancos de dados.

**Definir limite de concorrência** em `dagster.yaml`:

```yaml
telemetry:
  enabled: false

concurrency:
  default_op_concurrency_limit: 4    # máx 4 assets rodando simultaneamente
```

Ou por pool, no `definitions.py`:

```python
from dagster import Definitions, ConcurrencyLimitConfig

defs = Definitions(
    assets=all_assets,
    schedules=schedules,
    # Limitar concorrência por tipo de origem
    # (requer dagster >= 1.7)
)
```

A abordagem mais simples é o `default_op_concurrency_limit: 4` no `dagster.yaml`, que garante no máximo 4 subprocessos ETL simultâneos — compatível com o servidor atual.

---

### 1.8 Systemd services (completo)

**`/etc/systemd/system/dagster-daemon.service`:**

```ini
[Unit]
Description=Dagster Daemon — DataReplicator ETL
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=nzretlconnect
Group=nzretlconnect
WorkingDirectory=/opt/nzretlconnect/biMktNaz

# Variáveis de sistema obrigatórias
Environment=DAGSTER_HOME=/opt/nzretlconnect/biMktNaz/.local/dagster
Environment=LD_LIBRARY_PATH=/opt/oracle/instantclient_21_12
Environment=NLS_LANG=AMERICAN_AMERICA.AL32UTF8
Environment=TZ=America/Fortaleza
Environment=PATH=/opt/nzretlconnect/biMktNaz/bimktnaz/bin:/usr/local/bin:/usr/bin:/bin

# Credenciais do projeto (.env)
EnvironmentFile=/opt/nzretlconnect/biMktNaz/.env

ExecStart=/opt/nzretlconnect/biMktNaz/bimktnaz/bin/dagster-daemon run
Restart=on-failure
RestartSec=15
StartLimitIntervalSec=300
StartLimitBurst=5

# Logs via journald
StandardOutput=journal
StandardError=journal
SyslogIdentifier=dagster-daemon

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/dagster-webserver.service`:**

```ini
[Unit]
Description=Dagster Webserver — DataReplicator ETL
After=network.target dagster-daemon.service
Wants=dagster-daemon.service

[Service]
Type=simple
User=nzretlconnect
Group=nzretlconnect
WorkingDirectory=/opt/nzretlconnect/biMktNaz

Environment=DAGSTER_HOME=/opt/nzretlconnect/biMktNaz/.local/dagster
Environment=TZ=America/Fortaleza
Environment=PATH=/opt/nzretlconnect/biMktNaz/bimktnaz/bin:/usr/local/bin:/usr/bin:/bin
EnvironmentFile=/opt/nzretlconnect/biMktNaz/.env

# Escutar apenas localhost se usar nginx como proxy
# Trocar por -h 0.0.0.0 para acesso direto na rede
ExecStart=/opt/nzretlconnect/biMktNaz/bimktnaz/bin/dagster-webserver -h 127.0.0.1 -p 3000
Restart=on-failure
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=dagster-webserver

[Install]
WantedBy=multi-user.target
```

**Ativar e iniciar:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable dagster-daemon dagster-webserver
sudo systemctl start dagster-daemon
sudo systemctl start dagster-webserver
```

**Comandos de operação:**
```bash
# Status
sudo systemctl status dagster-daemon dagster-webserver

# Logs em tempo real
journalctl -u dagster-daemon -f
journalctl -u dagster-webserver -f

# Reiniciar após git pull (novo deploy)
sudo systemctl restart dagster-daemon dagster-webserver
```

---

### 1.9 Monitoramento dos próprios serviços

O Dagster monitora os jobs ETL, mas quem monitora o Dagster? Adicionar verificação simples ao crontab:

```cron
# Verificar se dagster-daemon está ativo — notifica Telegram se não estiver
*/10 * * * * systemctl is-active --quiet dagster-daemon || \
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}&text=⚠️ dagster-daemon parou! Servidor: $(hostname)"
```

Ou via sensor interno do próprio Dagster (ver Parte 2, seção `sensors.py`).

---

### 1.10 Checklist pré-go-live

Executar no servidor antes de remover o crontab:

```bash
# 1. Python e venv OK
/opt/nzretlconnect/biMktNaz/bimktnaz/bin/python --version

# 2. Dagster instalado
/opt/nzretlconnect/biMktNaz/bimktnaz/bin/dagster --version

# 3. DAGSTER_HOME configurado
echo $DAGSTER_HOME   # deve mostrar .local/dagster

# 4. Definições carregam sem erro
DAGSTER_HOME=.local/dagster \
  /opt/nzretlconnect/biMktNaz/bimktnaz/bin/dagster definitions validate \
  -f dagster/definitions.py

# 5. Oracle acessível sem .bashrc
env -i LD_LIBRARY_PATH=/opt/oracle/instantclient_21_12 \
  /opt/nzretlconnect/biMktNaz/bimktnaz/bin/python -c "import oracledb; print('oracle ok')"

# 6. SQL Server acessível
/opt/nzretlconnect/biMktNaz/bimktnaz/bin/python -c "import pyodbc; print('odbc ok')"

# 7. Materializar 1 asset de cada sistema de forma manual
DAGSTER_HOME=.local/dagster \
  /opt/nzretlconnect/biMktNaz/bimktnaz/bin/dagster asset materialize \
  --select cliente -f dagster/definitions.py

DAGSTER_HOME=.local/dagster \
  /opt/nzretlconnect/biMktNaz/bimktnaz/bin/dagster asset materialize \
  --select "biNazaria/produtos" -f dagster/definitions.py

DAGSTER_HOME=.local/dagster \
  /opt/nzretlconnect/biMktNaz/bimktnaz/bin/dagster asset materialize \
  --select "biSenior/filiais" -f dagster/definitions.py

# 8. Webserver sobe e responde
curl -s http://127.0.0.1:3000/server_info | python3 -m json.tool

# 9. Daemon registra schedules
journalctl -u dagster-daemon --since "5 minutes ago" | grep -i schedule
```

---

## PARTE 2 — CÓDIGO

### 2.1 Dependências (`requirements.txt`)

```
cryptography==46.0.5
dagster==1.9.*
dagster-webserver==1.9.*
oracledb==1.2.2
psycopg2-binary==2.9.10
pyodbc==5.1.0
python-dotenv==1.0.1
python-dateutil==2.9.0.post0
pyyaml==6.0.2
```

---

### 2.2 `dagster.yaml` (raiz do projeto)

```yaml
telemetry:
  enabled: false

retention:
  schedule:
    purge_after_days: 90
  sensor:
    purge_after_days: 90

concurrency:
  default_op_concurrency_limit: 4
```

---

### 2.3 `dagster_workspace.yaml` (raiz do projeto)

```yaml
load_from:
  - python_file:
      relative_path: dagster/definitions.py
      working_directory: .
```

---

### 2.4 Estrutura de arquivos

```
dagster/
├── __init__.py
├── assets/
│   ├── __init__.py
│   ├── _runner.py         # helper subprocess compartilhado
│   ├── bimktnaz.py        # 80+ assets biMktNaz (SQL Server → Postgres)
│   ├── bisenior.py        # assets biSenior (Oracle → Postgres)
│   └── binazaria.py       # assets biNazaria (SQL Server → Postgres)
├── schedules.py           # schedules traduzidas do crontab
├── sensors.py             # sensor de saúde dos serviços
└── definitions.py         # Definitions object (entry point)
```

---

### 2.5 `dagster/assets/_runner.py`

```python
import os
import subprocess
import sys

_PYTHON = sys.executable
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_etl(context, table: str, process: str = "regular", **kwargs) -> None:
    params = ["+table", table, "+process", process]
    for k, v in kwargs.items():
        params += [f"+{k}", str(v)]

    cmd = [_PYTHON, "run.py", "--params"] + params
    context.log.info(f"cmd: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=_ROOT, capture_output=True, text=True)

    if result.stdout:
        context.log.info(result.stdout.strip())
    if result.stderr:
        context.log.warning(result.stderr.strip())
    if result.returncode != 0:
        raise Exception(f"ETL falhou (exit {result.returncode}): {result.stderr[:500]}")
```

---

### 2.6 `dagster/assets/bimktnaz.py` (estrutura completa)

```python
from dagster import asset, AssetExecutionContext
from dagster.assets._runner import run_etl


# ─── Dimensões diárias ────────────────────────────────────────────────────────

@asset(group_name="biMktNaz", compute_kind="sql_server")
def cliente(context: AssetExecutionContext):
    run_etl(context, table="cliente", truncate="True")

@asset(group_name="biMktNaz", compute_kind="sql_server")
def cliente_vendedor(context: AssetExecutionContext):
    run_etl(context, table="cliente_vendedor", truncate="True")

@asset(group_name="biMktNaz", compute_kind="sql_server")
def produto(context: AssetExecutionContext):
    run_etl(context, table="produto", truncate="True")

# ... (1 @asset por tabela, seguindo o mesmo padrão)


# ─── Fatos incrementais com dependências ─────────────────────────────────────

@asset(group_name="biMktNaz", compute_kind="sql_server")
def venda(context: AssetExecutionContext):
    run_etl(context, table="venda", process="nDaysAgo", days="10", threads="10")

@asset(group_name="biMktNaz", compute_kind="sql_server",
       deps=["nf_compra"])
def nf_compra_produtos(context: AssetExecutionContext):
    run_etl(context, table="nf_compra_produtos", truncate="True")

@asset(group_name="biMktNaz", compute_kind="sql_server",
       deps=["venda"])
def pedidos_vendas(context: AssetExecutionContext):
    run_etl(context, table="pedidos_vendas", process="nDaysAgo", days="11", currentDay="True")

@asset(group_name="biMktNaz", compute_kind="sql_server",
       deps=["pedidos_vendas"])
def pedidos_vendas_produtos(context: AssetExecutionContext):
    run_etl(context, table="pedidos_vendas_produtos", process="nDaysAgo",
            days="10", currentDay="True", truncate="True")


# ─── Estoque perUnit (factory) ────────────────────────────────────────────────

def _estoque_asset(unit: int):
    @asset(name=f"estoque_unit_{unit}", group_name="biMktNaz_estoque", compute_kind="sql_server")
    def _asset(context: AssetExecutionContext):
        run_etl(context, table="estoque", process="perUnit", unit=str(unit))
    return _asset

estoque_assets = [_estoque_asset(u) for u in [2,3,4,5,6,7,8,9,10,11,13,14,15,16,17,18,19]]


# ─── AC / Aprovações / Apurações (4x por dia: 00h, 10h, 13h, 16h) ────────────
# Essas tabelas rodam em múltiplos horários — no Dagster, o asset é único,
# a schedule chama o mesmo asset várias vezes por dia.

AC_TABLES = [
    "biMktNaz/ac_encontros_contas", "biMktNaz/ac_encontros_contas_notas_debitos",
    "biMktNaz/ac_provisoes_receber", "biMktNaz/ac_provisoes_receber_saldo",
    "biMktNaz/ac_provisoes_receber_transacoes", "biMktNaz/ac_recebimentos",
    "biMktNaz/ac_recebimentos_manuais", "biMktNaz/ac_recebimentos_saldo",
    "biMktNaz/ac_recebimentos_transacoes", "biMktNaz/aprovacoes",
    "biMktNaz/aprovacoes_apuracoes", "biMktNaz/apuracoes_antecipacoes_icms",
    "biMktNaz/apuracoes_sellin_bonificados", "biMktNaz/desconto_adicional_apuracoes",
    "biMktNaz/estoques_excedentes_apuracoes", "biMktNaz/grupos_economicos_contas",
    "biMktNaz/modalidades_acordos_comerciais", "biMktNaz/modalidades_creditos",
    "biMktNaz/objetos_controle", "biMktNaz/rebaixas_apuracoes_ciclos",
    "biMktNaz/rebate_apuracoes", "biMktNaz/remanejamentos_cds_apuracoes",
    "biMktNaz/sellin_apuracoes", "biMktNaz/sellin_avulsos_apuracoes",
    "biMktNaz/tipos_acordo_comercial",
]

def _ac_asset(table: str):
    safe_name = table.replace("/", "__").replace("-", "_")
    @asset(name=safe_name, group_name="biMktNaz_ac", compute_kind="sql_server")
    def _asset(context: AssetExecutionContext):
        run_etl(context, table=table, truncate="True")
    return _asset

ac_assets = [_ac_asset(t) for t in AC_TABLES]
```

---

### 2.7 `dagster/schedules.py`

```python
from dagster import ScheduleDefinition, define_asset_job, AssetSelection

TZ = "America/Fortaleza"

# ─── Jobs por grupo horário ───────────────────────────────────────────────────

job_5h = define_asset_job("job_5h", selection=AssetSelection.assets(
    "cliente", "cliente_vendedor", "campanhas", "campanhas_empresas",
    "campanhas_participantes", "vendedores_procfit", "recebimentos_volumes",
    "titulos_edocs",
))

job_venda_noturno = define_asset_job("job_venda_noturno", selection=AssetSelection.assets(
    "venda", "notas_canceladas",
))

job_venda_diurno = define_asset_job("job_venda_diurno", selection=AssetSelection.assets(
    "venda", "notas_canceladas",
))

job_pedidos_vendas = define_asset_job("job_pedidos_vendas", selection=AssetSelection.assets(
    "pedidos_vendas", "pedidos_vendas_produtos",
))

job_produtos_endereco = define_asset_job("job_produtos_endereco",
    selection=AssetSelection.assets("produtos_endereco"))

job_6h = define_asset_job("job_6h", selection=AssetSelection.assets(
    "nf_compra", "nf_compra_produtos",
))

job_2h = define_asset_job("job_2h", selection=AssetSelection.assets(
    "pedidos_compras_produtos",
))

job_3h_misc = define_asset_job("job_3h_misc", selection=AssetSelection.assets(
    "gerentes_vendas_procfit", "supervisores_vendas_procfit", "produto_curva",
    "temp_grupo_prod", "pedidos_compras", "pedidos_compras_encerramento",
    "pedidos_compras_encerramento_produtos", "aprovacoes_receb_volumes",
    "paletes_alocacoes", "restricoes_pedidos_vendas", "apontadores",
    "apontadores_tipos", "apontadores_produtos", "nf_compra_devolucoes",
    "nf_compra_devolucoes_produtos", "vendas_parcelas", "banco_horas",
    "ajuste_ponto", "marcacoes_ponto",
))

job_1h_misc = define_asset_job("job_1h_misc", selection=AssetSelection.assets(
    "configuracoes_ol", "configuracoes_ol_marcas", "configuracoes_ol_excecoes",
    "configuracoes_ol_excecoes_clientes", "configuracoes_ol_excecoes_descontos",
    "configuracoes_ol_excecoes_marcas", "configuracoes_ol_excecoes_ols",
    "configuracoes_ol_excecoes_produtos", "configuracoes_ol_excecoes_unidades",
    "grupos_clientes", "identificadores", "tipos_acoes_descontos_ol",
    "vans_projetos", "clientes_redes", "grupos_tributarios_entrada",
    "grupos_tributarios_entrada_parametros", "grupos_tributarios",
    "grupos_tributarios_parametros", "grupos_compras", "cfop_fiscal",
    "titulos_contas_pagar", "titulos_contas_receber",
    "biMktNaz__pedidos_vendas_validacoes_produtos",
    "biMktNaz__grupos_economicos",
))

job_4h = define_asset_job("job_4h", selection=AssetSelection.assets(
    "metas_vendas", "metas_vendas_empresas", "metas_vendas_vendedores",
    "laboratorios", "fornecedores_descontos", "fornecedores_descontos_empresas",
    "fornecedores_descontos_grupos", "fornecedores_descontos_importacoes",
    "fornecedores_descontos_marcas", "fornecedores_descontos_produtos",
    "fornecedores_descontos_secoes", "vendas_feira", "rescisoes",
    "f_folha_visao_dp", "tempo_selecao",
    "biMktNaz__pedidos_vendas_validacoes_produtos_historicos",
    "biMktNaz__motivos_validacoes_pedidos_vendas",
    "biMktNaz__produtos_parametros_empresas", "biMktNaz__produtos_vendas",
    "biMktNaz__grupos_precos_empresas",
))

job_ac_intraday = define_asset_job("job_ac_intraday",
    selection=AssetSelection.groups("biMktNaz_ac"))

job_bisenior_2h = define_asset_job("job_bisenior_2h", selection=AssetSelection.groups("biSenior"))

job_binazaria_2h = define_asset_job("job_binazaria_2h", selection=AssetSelection.groups("biNazaria"))

job_estoque_3h = define_asset_job("job_estoque_3h", selection=AssetSelection.groups("biMktNaz_estoque"))


# ─── Schedules ────────────────────────────────────────────────────────────────

schedules = [
    # Cada hora
    ScheduleDefinition(job=job_produtos_endereco, cron_schedule="0 * * * *", execution_timezone=TZ),

    # A cada 3h — venda noturno (10 dias) e diurno (1 dia)
    ScheduleDefinition(job=job_venda_noturno,  cron_schedule="0 0-7/3 * * *",   execution_timezone=TZ),
    ScheduleDefinition(job=job_venda_noturno,  cron_schedule="30 1-7/3 * * *",  execution_timezone=TZ),
    ScheduleDefinition(job=job_venda_diurno,   cron_schedule="30 7-23/3 * * *", execution_timezone=TZ),
    ScheduleDefinition(job=job_venda_diurno,   cron_schedule="0 9-23/3 * * *",  execution_timezone=TZ),

    # Pedidos vendas — a cada 3h
    ScheduleDefinition(job=job_pedidos_vendas, cron_schedule="0 0-23/3 * * *",  execution_timezone=TZ),
    ScheduleDefinition(job=job_pedidos_vendas, cron_schedule="30 1-23/3 * * *", execution_timezone=TZ),

    # titulos_contas_receber_por_geracao — a cada 3h
    ScheduleDefinition(job=define_asset_job("job_tcr_geracao",
        selection=AssetSelection.assets("titulos_contas_receber_por_geracao")),
        cron_schedule="0 */3 * * *", execution_timezone=TZ),

    # Diários por horário
    ScheduleDefinition(job=job_1h_misc,     cron_schedule="0 1 * * *", execution_timezone=TZ),
    ScheduleDefinition(job=job_2h,          cron_schedule="0 2 * * *", execution_timezone=TZ),
    ScheduleDefinition(job=job_bisenior_2h, cron_schedule="0 2 * * *", execution_timezone=TZ),
    ScheduleDefinition(job=job_binazaria_2h,cron_schedule="0 2 * * *", execution_timezone=TZ),
    ScheduleDefinition(job=job_3h_misc,     cron_schedule="0 3 * * *", execution_timezone=TZ),
    ScheduleDefinition(job=job_estoque_3h,  cron_schedule="0 3 * * *", execution_timezone=TZ),
    ScheduleDefinition(job=job_4h,          cron_schedule="0 4 * * *", execution_timezone=TZ),
    ScheduleDefinition(job=job_5h,          cron_schedule="0 5 * * *", execution_timezone=TZ),
    ScheduleDefinition(job=job_6h,          cron_schedule="0 6 * * *", execution_timezone=TZ),

    # AC/Apurações — 4x por dia
    ScheduleDefinition(job=job_ac_intraday, cron_schedule="0 0 * * *",  execution_timezone=TZ),
    ScheduleDefinition(job=job_ac_intraday, cron_schedule="0 10 * * *", execution_timezone=TZ),
    ScheduleDefinition(job=job_ac_intraday, cron_schedule="0 13 * * *", execution_timezone=TZ),
    ScheduleDefinition(job=job_ac_intraday, cron_schedule="0 16 * * *", execution_timezone=TZ),

    # Semanais (segunda-feira)
    ScheduleDefinition(job=define_asset_job("job_semanal_titulos",
        selection=AssetSelection.assets("titulos_sem_notas", "f_titulos_com_notas_servicos",
                                        "f_titulos_com_notas_produtos")),
        cron_schedule="0 3 * * 1", execution_timezone=TZ),
]
```

---

### 2.8 `dagster/sensors.py`

Sensor que notifica no Telegram se o próprio daemon parar de processar schedules (caso extremo onde o daemon roda mas não dispara):

```python
from dagster import sensor, RunRequest, SensorEvaluationContext
from datetime import datetime, timezone, timedelta
import os, urllib.request, json


@sensor(job_name="__dagster_health__", minimum_interval_seconds=600)
def dagster_health_sensor(context: SensorEvaluationContext):
    # Verifica se houve algum run nos últimos 30 min em horários de pico
    # Implementação simples: apenas log — alertas via Telegram ficam no crontab (seção 1.9)
    context.log.info(f"health check at {datetime.now(timezone.utc).isoformat()}")
```

---

### 2.9 `dagster/definitions.py`

```python
from dagster import Definitions, load_assets_from_modules
from dagster.assets import bimktnaz, bisenior, binazaria
from dagster.schedules import schedules

all_assets = (
    load_assets_from_modules([bimktnaz, bisenior, binazaria])
    + bimktnaz.estoque_assets
    + bimktnaz.ac_assets
)

defs = Definitions(
    assets=all_assets,
    schedules=schedules,
)
```

---

## PARTE 3 — MIGRAÇÃO

### 3.1 Estratégia (zero downtime)

```
Semana 1: Dagster em paralelo com crontab (ambos rodando)
Semana 2: Desativar 50% do crontab (tabelas já validadas)
Semana 3: Desativar restante do crontab
Semana 4+: crontab removido, somente Dagster
```

Durante a semana 1, **o mesmo job ETL roda duas vezes** (crontab + Dagster). Isso é seguro porque todos os processos são idempotentes (truncate + insert ou delete-day + insert). O risco é apenas carga duplicada no banco de origem — aceitável por 1 semana.

Para evitar carga duplicada se preferir: na semana 1, habilitar schedules no Dagster **apenas para as tabelas que NÃO estão no crontab** — não há nenhuma atualmente, mas é uma opção.

---

### 3.2 Checklist de migração (por tabela)

Para cada tabela migrada, verificar:

- [ ] Asset definido em `dagster/assets/*.py`
- [ ] Schedule correspondente em `dagster/schedules.py` com mesmo horário do crontab
- [ ] Asset materializado manualmente com sucesso (`dagster asset materialize --select <tabela>`)
- [ ] Linha do crontab comentada
- [ ] 24h após comentar: verificar que tabela foi atualizada via Dagster (UI ou log)
- [ ] Linha do crontab removida

---

### 3.3 Rollback

Se algo der errado, reverter em 2 minutos:

```bash
# 1. Parar Dagster
sudo systemctl stop dagster-daemon dagster-webserver

# 2. Descomentar o crontab original
crontab -e
# Remover '#' das linhas comentadas

# 3. Confirmar que cron voltou a rodar
grep CRON /var/log/syslog | tail -20
```

O código ETL (`run.py`) nunca foi alterado, então não há nada para reverter no repositório.

---

## Critical files

| Arquivo | Papel | Ação |
|---------|-------|------|
| `docs/agendamentos_ETL.txt` | fonte de verdade dos schedules | leitura, não alterar |
| `run.py` | executor ETL | **nenhuma alteração** |
| `factories/entity_registry.py` | lista de 130+ entidades | leitura |
| `requirements.txt` | dependências Python | adicionar `dagster`, `dagster-webserver` |
| `dagster.yaml` | config concorrência, retenção, telemetria | **criar** |
| `dagster_workspace.yaml` | aponta entry point para o daemon | **criar** |
| `dagster/__init__.py` | torna dagster/ um pacote Python | **criar** (vazio) |
| `dagster/assets/_runner.py` | helper subprocess compartilhado | **criar** |
| `dagster/assets/bimktnaz.py` | 80+ assets biMktNaz | **criar** |
| `dagster/assets/bisenior.py` | assets biSenior | **criar** |
| `dagster/assets/binazaria.py` | assets biNazaria | **criar** |
| `dagster/schedules.py` | schedules traduzidas do crontab | **criar** |
| `dagster/definitions.py` | entry point Definitions | **criar** |
| `/etc/systemd/system/dagster-daemon.service` | serviço daemon | **criar no servidor** |
| `/etc/systemd/system/dagster-webserver.service` | serviço webserver | **criar no servidor** |
| `/etc/nginx/sites-available/dagster` | reverse proxy (opcional) | **criar no servidor** |

---

## Order of implementation

**Fase 0 — Preparação (local, sem afetar produção):**
1. Instalar `dagster` no venv local: `pip install dagster dagster-webserver`
2. Criar `dagster/` com estrutura mínima + `dagster.yaml` + `dagster_workspace.yaml`
3. Criar `_runner.py` e 1 asset de cada sistema (`cliente`, `biSenior/filiais`, `biNazaria/produtos`)
4. Testar localmente: `dagster asset materialize --select cliente`
5. Subir UI local: `dagster-webserver -f dagster/definitions.py`
6. Confirmar que o asset graph aparece e a materialização gera logs corretos

**Fase 1 — Todos os assets (local):**
7. Criar assets completos para biMktNaz, biSenior, biNazaria
8. Criar `schedules.py` com todos os schedules do crontab
9. Validar: `dagster definitions validate -f dagster/definitions.py`
10. Commit e push

**Fase 2 — Deploy no servidor:**
11. `git pull` no servidor
12. `pip install dagster dagster-webserver` no venv do servidor
13. Criar `$DAGSTER_HOME`: `mkdir -p .local/dagster`
14. Configurar `DAGSTER_HOME` no `~/.bashrc` do servidor
15. Executar checklist pré-go-live (seção 1.10)
16. Criar e ativar systemd services (seção 1.8)
17. Criar nginx config se necessário (seção 1.2)
18. Adicionar cron de backup do SQLite (seção 1.6)
19. Adicionar cron de health check do daemon (seção 1.9)

**Fase 3 — Migração gradual:**
20. Semana 1: Dagster e crontab em paralelo, monitorar duplicações
21. Semana 2: Comentar 50% do crontab (começar pelas tabelas simples de truncate)
22. Semana 3: Comentar restante
23. Semana 4: Remover crontab

---

## Verification

**Pós-deploy, verificações diárias na primeira semana:**

```bash
# Runs do dia — deve mostrar todos os jobs executados
journalctl -u dagster-daemon --since "today" | grep -E "COMPLETED|FAILED"

# Tabelas que falharam
journalctl -u dagster-daemon --since "today" | grep "FAILED"

# Confirmar que `venda` foi carregada nos horários esperados
journalctl -u dagster-daemon --since "today" | grep "venda"
```

**Na UI do Dagster (http://servidor:3000 ou SSH tunnel):**
- `Assets` → ver todas as tabelas com status de última materialização
- `Automation` → `Schedules` → confirmar que todos os schedules estão `RUNNING`
- `Runs` → ver histórico com duração e status de cada job

**Indicadores de sucesso:**
- Nenhuma tabela com `Last materialized` > 2x o intervalo esperado
- `bot/error_check.py` continua reportando zero erros (pipeline ETL não foi alterado)
- UI do Dagster acessível e responsiva
- `dagster-daemon` uptime > 99% (verificar via `systemctl status`)

