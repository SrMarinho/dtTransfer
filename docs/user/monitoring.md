# Monitoramento & Alertas

## Logging Estruturado

Cada execução gera logs em `logs/YYYY/MM/YYYYMMDD.log`.

### Formato

```
2026-04-28 10:30:45 - INFO - [a1b2c3] run=a1b2c3 table=cliente process=regular
2026-04-28 10:30:46 - INFO - [a1b2c3] cliente - Processo iniciado!
2026-04-28 10:31:02 - INFO - [a1b2c3] cliente - Inserindo dados...
2026-04-28 10:31:12 - INFO - [a1b2c3] cliente - Processo finalizado com sucesso!
2026-04-28 10:31:12 - INFO - [a1b2c3] cliente - Foram inseridas 5430 em 26.15 segundo(s).
```

- **run hash** (`[a1b2c3]`): identifica a execução inteira
- **timestamp**: marca exato de cada evento
- **level**: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Configurar Log Level

Em `.env`:

```env
LOG_LEVEL=INFO  # DEBUG (verboso) → INFO (padrão) → ERROR (só falhas)
```

## Erros em Tempo Real

### Detecção Automática via Telegram

Erros são capturados e enviados ao seu chat Telegram **automaticamente** via `TelegramHandler`:

```
❌ dataReplicator — 2 erro(s) em 28/04/2026 10:00:02

• [9a8b5f] cliente - Erro ao conectar: timeout em SQL Server
• [9a8b5f] venda - ERRO:  nulo na coluna "data" viola NOT NULL
```

**Configurar:**

1. Crie bot no BotFather (@BotFather)
2. Obtenha `TELEGRAM_BOT_TOKEN`
3. Crie grupo privado ou canal
4. Envie mensagem e obtenha `TELEGRAM_CHAT_ID`:

```bash
curl "https://api.telegram.org/bot{TOKEN}/getUpdates" | jq '.result[0].message.chat.id'
```

5. Adicione em `.env`:

```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=-1001234567890
```

6. Teste:

```bash
python scripts/check_telegram.py
```

## Relatório Periódico de Erros

### Script: `bot/error_check.py`

Roda a cada 30 min (configurável em cron) e manda **resumo** de todos os erros do período:

```bash
*/30 * * * * python bot/error_check.py
```

### Exemplo de Relatório

```
❌ dataReplicator — 11 erro(s)
🕐 início → 10:00

🟡 apontadores — 2x
  ↳ Erro ao inserir dados: ERRO:  o valor nulo na coluna "descricao" viola a restrição...

🟡 aprovacoes_apuracoes — 2x
  ↳ Erro ao inserir dados: ERRO:  o valor nulo na coluna "status_controladoria" viola...

⚪ base_segregado — 1x
  ↳ Entidade não encontrada!
```

**Cores:**
- 🟡 Erro SQL (constraint, tipo, etc.)
- ⚪ Erro lógico (entidade, conexão)

## Verificar Erros Manualmente

### Hoje (Completo)

```bash
python scripts/check_errors.py
```

Output:
```
[28/04/2026 00:00→16:35] 8 erro(s)

🟡 cliente — 1x
  ↳ Connection timeout
🟡 venda — 7x
  ↳ Constraint violation
```

### Intervalo Específico

```bash
python scripts/check_errors.py --since 10:00 --until 12:00
```

Mostra erros entre 10:00 e 12:00 de hoje.

### Outro Dia

```bash
python scripts/check_errors.py --date 2026-04-27
```

## SLA — Service Level Agreement

Monitora se as tabelas estão sendo atualizadas no tempo esperado.

### Relatório Periódico (a cada 30 min)

```bash
*/30 * * * * python bot/sla_check.py
```

### Exemplo de Alerta SLA

```
⚠️ SLA violations detected

🔴 cliente - FRESHNESS VIOLATED
  Last update: 48 horas atrás
  Expected: max 24h
  Status: ⛔ CRITICAL

🟡 venda - DURATION WARNING
  Avg duration: 45 seg
  Expected: max 30s
  Status: ⚠️  WARNING

📊 Failure rate: 15% (expected: max 20%)
  Status: ✅ OK
```

### Configurar SLA Esperado

Edite `sla_config.yaml`:

```yaml
defaults:
  max_freshness_minutes: 1440   # 24h
  max_duration_seconds: 1800    # 30min
  max_failure_rate_pct: 20
  failure_window_hours: 24

tables:
  cliente:
    max_freshness_minutes: 1500  # 25h (cron 05:00)
  venda:
    max_freshness_minutes: 360   # 6h (cron a cada 3h)
    max_duration_seconds: 1800
  pedidos_vendas:
    max_freshness_minutes: 240   # 4h
  # demais tabelas herdam defaults
```

## Métodos de Alertas Combinados

| Método | Quando | Tipo |
|--------|--------|------|
| **TelegramHandler** | Erro durante execução | Real-time |
| **error_check.py** | Resumo periódico | 30 min |
| **sla_check.py** | SLA violado | 30 min |

**Fluxo recomendado:**
1. Erro acontece → TelegramHandler manda immediately
2. A cada 30 min → error_check e sla_check revisam e mandam resumo

## Arquivos de Log

### Estrutura

```
logs/
├── 2026/
│   ├── 04/
│   │   ├── 20260427.log
│   │   ├── 20260428.log  ← hoje
│   │   └── 20260429.log
│   └── 05/
│       └── 20260501.log
```

**Retenção**: mantém indefinidamente (considere cleanup anual).

### Pesquisa Rápida

```bash
# Última tabela processada com sucesso
grep "Processo finalizado" logs/2026/04/20260428.log | tail -1

# Tabela mais lenta
grep "Foram inseridas" logs/2026/04/20260428.log | sort -k3 -n | tail -1

# Todas as falhas (ERRORs)
grep "ERROR" logs/2026/04/20260428.log

# Falhas de uma tabela específica
grep "ERROR" logs/2026/04/20260428.log | grep "venda"

# Visualizar log em tempo real
tail -f logs/2026/04/20260428.log

# Contar linhas (execuções aproximadas)
wc -l logs/2026/04/20260428.log
```

## Dashboards & Métricas (Futuro)

Possíveis integrações:

- **Grafana**: pull de métricas via prometheus exporter
- **DataDog**: envio de eventos via API
- **ELK Stack**: ingestão de logs estruturados
- **InfluxDB**: histórico de timestamps/duração/rows

Por enquanto, todos os dados estão em:
- **Logs textuais** (`logs/YYYY/MM/YYYYMMDD.log`)
- **SQLite** (`.local/bot.db` — `etl_runs` table)
- **Telegram** (histórico de mensagens)

## Troubleshooting Alertas

### Telegram não recebe notificações

```bash
# 1. Verificar token e chat_id
cat .env | grep TELEGRAM

# 2. Testar manualmente
python scripts/check_telegram.py
# Se falhar: token/chat_id inválidos ou network issue

# 3. Ver logs de erro
grep "ERROR" logs/2026/04/20260428.log | grep -i "telegram"
```

### error_check.py não roda

```bash
# 1. Verificar cron
crontab -l | grep error_check

# 2. Ver se está no PATH
which python

# 3. Testar manualmente
python -m src.interfaces.bot.error_check

# 4. Ver se há erros de import
python -c "from src.interfaces.bot import error_check"
```

### SLA check falha

```bash
# 1. Verificar YAML válido
python -c "import yaml; yaml.safe_load(open('sla_config.yaml'))"

# 2. Ver se há rows em etl_runs
sqlite3 .local/bot.db "SELECT COUNT(*) FROM etl_runs;"

# 3. Testar manualmente
python bot/sla_check.py

# 4. Ver logs
grep "ERROR" logs/2026/04/20260428.log | grep -i "sla"
```
