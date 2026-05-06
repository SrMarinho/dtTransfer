# Plano: SLA para ETL DataReplicator

## Context

Hoje o pipeline ETL não tem visibilidade de SLA. O único monitoramento é o `bot/error_check.py`, que vasculha logs e envia erros via Telegram a cada 30 min. Não sabemos:

- Se uma tabela parou de atualizar (freshness)
- Se um job está demorando mais que o normal (duração)
- Se há um padrão de falhas em uma janela (taxa de falha)

### Constraints

O autor do plano **não tem acesso ao servidor de produção nem ao Postgres da aplicação**. Isso descarta:

- Criar tabelas no Postgres da aplicação (`biMktNaz`, `biSenior`, `biNazaria`)
- Editar crontab manualmente / rodar `psql` no server
- Inspecionar arquivos locais do server diretamente

A solução precisa ser **autocontida no repositório**: alguém com acesso ao server faz deploy via `git pull` e edita o crontab, exatamente como aconteceu com `bot/error_check.py`.

### Design

- **Escopo**: freshness + duração + taxa de falha
- **Persistência**: SQLite local (`.local/bot.db`) — não toca o Postgres da aplicação
- **Detecção**: hook no `run.py` (primário) + fallback de parser de logs (caso o hook morra antes de gravar)
- **Config**: `sla_config.yaml` versionado no repo
- **Consumo**: relatório Telegram periódico (cron `*/30`). Sem comandos interativos no bot por ora — comandos ficam no roadmap futuro

---

## Schema SQLite (novo)

Adicionar em `bot/db.py:init_db` (linhas 17-22) ao `executescript`:

```sql
CREATE TABLE IF NOT EXISTS etl_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  table_name      TEXT NOT NULL,
  process         TEXT,
  run_hash        TEXT,
  started_at      TEXT NOT NULL,    -- ISO8601 (datetime.now().isoformat)
  ended_at        TEXT,
  duration_seconds REAL,
  status          TEXT NOT NULL,    -- 'running' | 'success' | 'fail'
  rows_inserted   INTEGER,
  error_message   TEXT
);
CREATE INDEX IF NOT EXISTS idx_etl_runs_table_started ON etl_runs(table_name, started_at);
CREATE INDEX IF NOT EXISTS idx_etl_runs_status_started ON etl_runs(status, started_at);
```

`init_db` é idempotente (CREATE IF NOT EXISTS) e já é chamado por `bot/error_check.py:40` — o schema sobe automaticamente no primeiro cron pós-deploy.

---

## Arquivos a criar

### 1. `bot/sla_repository.py`

Camada de acesso ao SQLite. Reusa `bot.db.get_connection()`. **Toda escrita é silenciosa em try/except — falha de SLA nunca derruba ETL.**

```python
def start_run(table_name, process, run_hash) -> int | None:
    # INSERT etl_runs (table_name, process, run_hash, started_at=now, status='running')
    # retorna lastrowid; None se SQLite indisponível
def finish_run(run_id, rows_inserted=None) -> None:
    # UPDATE ended_at=now, duration_seconds, status='success', rows_inserted
def fail_run(run_id, error_message) -> None:
    # UPDATE ended_at=now, duration_seconds, status='fail', error_message[:500]
def last_success_at(table_name) -> datetime | None
def avg_duration(table_name, window_hours) -> float | None
def failure_rate(table_name, window_hours) -> tuple[int, int]   # (fails, total)
```

### 2. `sla_config.yaml` (raiz do projeto)

```yaml
defaults:
  max_freshness_minutes: 1440   # 24h
  max_duration_seconds: 1800    # 30min
  max_failure_rate_pct: 20
  failure_window_hours: 24

tables:
  venda: { max_freshness_minutes: 360 }
  notas_canceladas: { max_freshness_minutes: 360 }
  pedidos_vendas: { max_freshness_minutes: 240 }
  pedidos_vendas_produtos: { max_freshness_minutes: 240 }
  cliente: { max_freshness_minutes: 1500 }
  campanhas: { max_freshness_minutes: 780 }
  produtos_endereco: { max_freshness_minutes: 90 }
  # demais tabelas herdam defaults; popular incrementalmente
```

### 3. `bot/sla_check.py`

Análogo a `bot/error_check.py`. Carrega YAML, varre `defaults` + `tables`, para cada uma:

- **Freshness**: `now - last_success_at(table)` → violado se > `max_freshness_minutes`
- **Duração**: `avg_duration(table, window)` → violado se > `max_duration_seconds`
- **Falha**: `failure_rate(table, window)` → violado se `pct > max_failure_rate_pct`

Antes de avaliar, chama `src.interfaces.bot.sla_log_parser.reconcile_today()` para preencher gaps. Se houver violações, monta mensagem HTML estilo `error_check.build_summary` e dispara `bot.telegram.send_long_message`. Persiste `last_sla_check_at` em `telegram_state` (mesma key-value já usada).

### 4. `src/interfaces/bot/sla_log_parser.py` (fallback)

Parser leve que escaneia o log do dia atual procurando os padrões já existentes em `src/processes/full_query.py`:

```
{table} - Processo finalizado com sucesso!
{table} - Foram inseridas {N} em {T} segundo(s).
```

Função `reconcile_today()` itera o log, extrai `(timestamp, table, run_hash, rows, duration)` e faz `INSERT OR IGNORE` em `etl_runs` usando `(run_hash, table_name, started_at)` como chave única lógica. Cobre o caso em que o hook em `run.py` morreu antes do `finish_run` (ex: kill -9, OOM, SQLite locked).

---

## Arquivos a modificar

### `src/interfaces/bot/db.py`
Adicionar o `CREATE TABLE etl_runs` + índices ao `executescript` em `init_db`.

### `run.py` (linhas 30-36)
Envolver `mode.run()` com hook de SLA:

```python
from src.interfaces.bot import sla_repository

def main():
    params = init_args()
    run_hash = set_run_hash()
    table_name = params.get('table', '-')
    process_name = params.get('process', 'regular')
    logger.info(f"run={run_hash} table={table_name} process={process_name}")

    run_id = sla_repository.start_run(table_name, process_name, run_hash)
    try:
        mode = ModeFactory.getInstance(params['mode'], params)
        result = mode.run()
        rows = result.get('rows_inserted') if isinstance(result, dict) else None
        sla_repository.finish_run(run_id, rows_inserted=rows)
    except Exception as e:
        sla_repository.fail_run(run_id, str(e)[:500])
        raise
```

### `src/processes/full_query.py`
Mudar `return True` para:

```python
return {'rows_inserted': numOfRows, 'duration_seconds': totalTime}
```

Aplicar mesma mudança em:
- `src/processes/incremental.py` (somar `numOfRows` entre threads)
- `src/processes/monthly.py`
- `src/processes/unit.py`

`src/core/modes/cli.py` propaga o retorno. Se algum process retornar `True`/`None`, `run.py` interpreta `rows=None` (não quebra).

### `agendamentos_ETL.txt` (final do arquivo)

```
# SLA — verificação a cada 30 min
*/30 * * * * source ~/.bashrc && cd /opt/nzretlconnect/DataReplicator && /opt/nzretlconnect/DataReplicator/.venv/bin/python -m src.interfaces.bot.sla_check
```

### `requirements.txt`
Adicionar `pyyaml==6.0.2`.

### `.gitignore`
`.local/` já está ignorado — `bot.db` continua fora do repo.

---

## Critical files reference

| Arquivo | Linhas | Papel |
|---------|--------|-------|
| `bot/db.py` | 17-23 | Schema SQLite — adicionar `etl_runs` |
| `bot/error_check.py` | inteiro | Modelo para `sla_check.py` (init_db, telegram_state, build_summary, send_long_message) |
| `bot/telegram.py` | — | Reusar `send_long_message` (já lida com chunks de 4096) |
| `src/core/logger/error_parser.py` | — | Modelo de regex para `sla_log_parser.py` |
| `run.py` | 30-36 | Onde injetar hook start/end |
| `src/processes/full_query.py` | — | Padrão `Foram inseridas N em T segundo(s)`; ajustar return |
| `src/core/logger/run_context.py` | — | `run_hash` reaproveitado, sem mudança |

---

## Verification

Tudo localmente, antes de PR:

1. **Schema sobe**: `python -c "from src.interfaces.bot.db import init_db; init_db()"` e `sqlite3 .local/bot.db ".schema etl_runs"` mostra tabela e índices.
2. **Hook de sucesso**: `python run.py load regular --table cliente --truncate` → `sqlite3 .local/bot.db "SELECT table_name, status, duration_seconds, rows_inserted FROM etl_runs ORDER BY id DESC LIMIT 1;"` mostra `cliente | success | >0 | >0`.
3. **Hook de falha**: `python run.py load regular --table tabela_inexistente` → última linha tem `status='fail'` e `error_message` populado.
4. **Freshness violado**: `UPDATE etl_runs SET started_at='2026-04-01T00:00:00' WHERE id=...`; rodar `python bot/sla_check.py`; conferir alerta Telegram.
5. **Duração violada**: forçar `max_duration_seconds: 1` no YAML para uma tabela com run gravado; rodar `bot/sla_check.py`; conferir alerta.
6. **Failure rate violado**: inserir 5 runs `status='fail'` na janela; rodar `bot/sla_check.py`; conferir alerta.
7. **Fallback parser**: deletar última linha de `etl_runs`; `python -c "from src.interfaces.bot.sla_log_parser import reconcile_today; reconcile_today()"`; verificar que linha foi recriada do log.

Pós-deploy, validação remota (via Telegram apenas):
- 30 min após PR mergeado, esperar primeiro relatório do `sla_check.py`. Se nenhuma violação, mensagem silenciosa (igual `error_check`).
- Forçar uma falha controlada (ex: rodar manualmente uma tabela inexistente via cron temporário) e confirmar que aparece alerta no Telegram em até 30 min.

---

## Order of implementation

1. Schema em `bot/db.py` + `bot/sla_repository.py`
2. Hook em `run.py` + ajuste de retorno nos 4 processes
3. Smoke test local (verifications 1-3)
4. `sla_config.yaml` + `bot/sla_check.py`
5. `bot/sla_log_parser.py` (fallback)
6. Cron + `requirements.txt` + commit + push direto na main (mesmo fluxo do error_check.py)
