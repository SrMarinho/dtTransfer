# Roadmap de Profissionalização — DataReplicator

## Context

O DataReplicator é um ETL Python maduro em partes (factories, retry exponencial, multithreading, bot Telegram com auto-recovery, logging estruturado, documentação). Mas opera em modelo **cron + execução manual** e tem lacunas que o impedem de escalar:

- Sem orquestração real (DAGs, dependências, backfill, UI de operação)
- Sem pool de conexões (cada execução abre conexão nova)
- Sem CI/CD, sem métricas, sem tracing
- 130+ entidades com boilerplate hardcoded e sem schema enforcement
- Sem CDC/idempotência transacional — rodar 2x é frágil
- Secrets em `.env` plano, sem rotação
- Cobertura de testes baixa, sem coverage automatizado

Este documento lista melhorias **da maior para a menor alavancagem**. Cada item pode virar um plano próprio em `docs/plans/<nome>.md` quando aprovado para execução, seguindo o padrão de [`sla-implementation.md`](sla-implementation.md).

### Legenda

- **Impacto:** 🔴 transforma o sistema · 🟠 ganho operacional grande · 🟡 ganho moderado · ⚪ polimento
- **Esforço:** ⏱️ horas · ⏱️⏱️ dias · ⏱️⏱️⏱️ semanas · ⏱️⏱️⏱️⏱️ meses
- **Status:** 📍 rascunho · 🟡 em discussão · ✅ aprovado · 🚀 em execução · ✔️ concluído

---

## Tier S — Mudanças que transformam o sistema

### 1. 🔴 Orquestração com Dagster / Prefect / Airflow ⏱️⏱️⏱️

**Problema:** crontab + subprocess. Sem DAGs, sem retry de job inteiro, sem dependências entre tabelas (`nf_compra` antes de `nf_compra_produtos`), sem backfill por intervalo, sem UI para operadores. Visibilidade só pelo bot Telegram.

**Solução:** migrar agendamentos para **Dagster** (recomendado — modelo de assets casa com tabelas) ou **Prefect 2** (mais leve). Cada tabela vira asset com schedule, retry, SLA e dependências. `run.py` atual continua sendo o executor de cada asset.

**Ganho:**
- UI web com histórico, retry com 1 clique
- Backfill por intervalo trivial
- Dependências entre tabelas explícitas
- Catálogo de dados automático
- Substitui boa parte do bot Telegram em UX

**Critical files:** `run.py`, `factories/entity_registry.py` (lista de assets), `agendamentos_ETL.txt` ou `docs/agendamentos_ETL.txt` (vai virar código).

**Status:** 📍 rascunho

---

### 2. 🔴 API HTTP de controle (FastAPI) ⏱️⏱️

**Problema:** disparar job manual exige SSH no servidor ou comando Telegram. Sem integração com outros sistemas (frontend interno, Slack workflow, Jenkins, GitHub Actions).

**Solução:** expor `bot/runner.py` via **FastAPI**:
- `POST /jobs` — dispara job (mesmos params do `run.py`)
- `GET /jobs/{hash}` — status
- `DELETE /jobs/{hash}` — cancela
- `GET /tables` — lista entidades (vinda de `EntityRegistry.valid_tables()`)
- `GET /health`, `GET /metrics` (Prometheus)

Auth: API key ou JWT. Streamlit/React opcional para UI.

**Critical files:** `bot/runner.py`, `factories/entity_registry.py`, novo `api/` ou `bot/api.py`.

**Status:** 📍 rascunho

---

### 3. 🔴 Observabilidade real — Prometheus + Grafana ⏱️⏱️⏱️

**Problema:** logs em arquivo + batching Telegram. Sem métricas, sem dashboards, sem tracing. Para saber se uma tabela está degradando: `grep` em log.

**Solução:** instrumentar `src/processes/process.py` e `src/core/table.py` com `prometheus-client`:
- `etl_rows_inserted_total{table,system}`
- `etl_duration_seconds{table,process}` (histogram)
- `etl_failures_total{table,reason}`
- `etl_last_success_timestamp{table}` (essencial para freshness)

Dashboards Grafana por sistema. Grafana Alerts complementam ou substituem `src/interfaces/bot/error_check.py` para anomalias (queda de volume, P95 alto). **OpenTelemetry tracing** opcional para correlacionar fases (extract → transform → load) em jobs paralelos.

**Critical files:** `src/processes/process.py`, `src/processes/incremental.py`, `src/processes/full_query.py`, `src/core/table.py`, novo `src/core/metrics.py`.

**Sinergia:** complementa o plano [`sla-implementation.md`](sla-implementation.md) que usa SQLite local. Métricas Prometheus dão visão global; SQLite dá histórico interno.

**Status:** 📍 rascunho

---

### 4. 🔴 Schema-as-code — Pydantic + auto-detecção de drift ⏱️⏱️⏱️

**Problema:** 130+ entidades com 8-10 linhas de boilerplate cada (`fromDB`, `toDB`, `name`, `columns`). Coluna nova na origem? Edita arquivo `.py` + `.sql`. Sem validação de tipo/NOT NULL/constraints. Sem aviso quando origem muda.

**Solução em duas etapas:**

a) **Pydantic models** para cada entidade declarando tipos e constraints. `Table` base usa metaclass que lê o model — elimina boilerplate.

b) **Schema diff job** — task agendada que compara `INFORMATION_SCHEMA` da origem vs. destino e dispara alerta Telegram quando há divergência (coluna nova, tipo mudou).

Alternativa pesada: **SQLAlchemy Core + Alembic** para versionar schemas com migrations.

**Critical files:** `src/core/table.py`, todos os arquivos em `src/systems/pbs/entities/`, `src/systems/senior/entities/`, `src/systems/bimktnaz/entities/`. Migração pode ser incremental (modulo a modulo).

**Status:** 📍 rascunho

---

### 5. 🔴 Idempotência + watermarks ⏱️⏱️⏱️

**Problema:** rodar mesmo job 2x duplica dados em alguns processos. RegularQuery faz truncate+insert; nDaysAgo deleta o dia e re-insere (frágil). `deleteDay()` é stub na base. Sem garantia transacional entre delete e insert — kill -9 no meio deixa estado inconsistente.

**Solução:**
- Tabela `etl_watermarks(table_name, last_loaded_at, last_loaded_value, run_hash)` no Postgres destino
- Wrappar delete+insert em **transação** explícita (`BEGIN ... COMMIT`)
- Para tabelas de mutação: implementar **MERGE / `ON CONFLICT`** no lugar de delete+insert
- Watermark permite retomar de onde parou se job morrer

**Critical files:** `src/core/table.py` (insert/truncate/deleteDay), `src/processes/incremental.py`, `src/processes/monthly.py`.

**Sinergia:** o `etl_runs` do plano de SLA é primo deste — pode-se considerar fundir as duas tabelas no futuro.

**Status:** 📍 rascunho

---

## Tier A — Profissionalização operacional

### 6. 🟠 CI/CD com GitHub Actions ⏱️⏱️

**Problema:** zero validação automática em PRs.

**Solução:** workflow rodando em PRs:
- `ruff check` (lint + isort em uma ferramenta)
- `mypy --strict` em pastas críticas (`processes/`, `factories/`, `bot/`)
- `pytest` + `pytest-cov` (badge no README)
- `pip-audit` para vulnerabilidades
- `pre-commit` config local com mesma stack

Em merge para `main`: build de imagem Docker e push para registry.

**Critical files:** novo `.github/workflows/ci.yml`, novo `.pre-commit-config.yaml`, novo `requirements-dev.txt`.

**Status:** 📍 rascunho

---

### 7. 🟠 Containerização production-ready ⏱️⏱️

**Problema:** `Dockerfile` existe mas deploy é venv em `/opt/app`. Sem reprodutibilidade entre dev/staging/prod.

**Solução:**
- Refinar `Dockerfile` multi-stage (builder + runtime slim)
- `docker-compose.yml` para dev local (Postgres, mock SQL Server, bot)
- Produção: **Helm chart** se houver K8s; senão Compose com `restart: unless-stopped`
- **systemd service** como fallback — substitui cron e reinicia em falha

**Critical files:** `Dockerfile`, novo `docker-compose.yml`, novo `deploy/helm/` ou `deploy/systemd/`.

**Status:** 📍 rascunho

---

### 8. 🟠 Gestão de secrets — Doppler / Vault / AWS Secrets Manager ⏱️⏱️

**Problema:** `.env` plano com credenciais de 5 bancos + token Telegram. Sem rotação, sem auditabilidade.

**Solução:**
- **Doppler** (mais simples) ou **HashiCorp Vault** (self-hosted) ou **AWS Secrets Manager**
- Camada `config/secrets.py` com fallback: Vault → `.env` em dev
- Rotação trimestral documentada

**Critical files:** todos em `src/core/databases/`, `src/interfaces/bot/telegram.py`, `src/core/logger/telegram_handler.py`.

**Status:** 📍 rascunho

---

### 9. 🟠 Pool de conexões via SQLAlchemy ⏱️⏱️

**Problema:** `driver.connection()` cria conexão nova a cada call. Em jobs com 10 threads, é 10x handshake desperdiçado. Sob carga, risco de `too many connections` no Postgres.

**Solução:** envolver drivers em `sqlalchemy.create_engine` com pool (`pool_size=10, max_overflow=20`). Drivers atuais (`pyodbc`, `oracledb`, `psycopg2`) já são compatíveis.

**Critical files:** `src/core/databases/connections/postgres_connection.py`, `sqlserver_connection.py`, `oracle_connection.py`, `src/factories/database_factory.py`.

**Status:** 📍 rascunho

---

### 10. 🟠 Auditoria + rate limiting do bot ⏱️⏱️

**Problema:** tabela `jobs` rastreia status mas não quem disparou. Sem rate limiting global. A tabela `rate_limit` existe em `bot/db.py` mas não é usada.

**Solução:**
- Nova tabela `audit_log(timestamp, user_id, username, command, params, result)` populada em `bot/commands/*`
- Ativar `rate_limit` (já no schema): max N comandos `/run` por hora
- Comando `/audit` para ver últimas 20 ações (admin only)

**Critical files:** `bot/db.py`, todos em `bot/commands/`, `bot/auth.py`.

**Status:** 📍 rascunho

---

### 11. 🟠 Dead Letter Queue + retry automático de jobs falhos ⏱️⏱️

**Problema:** job que falha vira `status="error"` no SQLite e só reprocessa se humano disparar de novo.

**Solução:**
- Após falha, agendar retry em backoff (1h, 6h, 24h) — campo `next_retry_at` na tabela `jobs` + worker que polla
- Após N tentativas: `status="dlq"` + alerta crítico Telegram
- Se item 1 (orquestrador) for adotado, isso vem grátis

**Critical files:** `bot/jobs.py`, `bot/poll.py`, `bot/runner.py`.

**Status:** 📍 rascunho

---

### 12. 🟠 Aumento de cobertura de testes ⏱️⏱️⏱️ (contínuo)

**Problema:** ~5 testes e2e básicos, unitários esparsos, sem coverage report. Refatoração é arriscada.

**Solução:**
- Meta inicial: **60% de cobertura** em `src/processes/`, `src/core/table.py`, `src/factories/`, `src/interfaces/bot/`
- **testcontainers-python** para Postgres real em integration tests (elimina mocks)
- **hypothesis** para property-based test em `Table.insert()` (gera linhas aleatórias, valida idempotência)
- Smoke test contra bancos reais em staging — não em CI

**Critical files:** `tests/conftest.py`, `tests/unit/`, `tests/integration/`, `tests/e2e/`.

**Status:** 📍 rascunho

---

## Tier B — Qualidade de código e DX

### 13. 🟡 Templating SQL com Jinja2 ⏱️⏱️

**Problema:** `REPLACE_START_DATE` / `REPLACE_END_DATE` via string replace. Sem condicionais, sem reuso de fragmentos comuns (filtro de empresa repetido em 20 SQLs).

**Solução:** migrar para Jinja2 (mesma engine do dbt). Fragmentos como `{% include "filters/empresa.sql" %}`. Engine central em `src/core/table.py`.

**Critical files:** `src/core/table.py`, todos em `src/systems/*/sqls/`.

**Status:** 📍 rascunho

---

### 14. 🟡 dbt para transformações pós-load ⏱️⏱️⏱️

**Problema:** sistema é E+L (extract + load). Transformações vivem no SQL de origem ou no consumidor.

**Solução:** **dbt** na camada de transformação no Postgres destino (modelos `staging` → `marts` → `analytics`). Testes de qualidade nativos (`unique`, `not_null`, `relationships`), lineage automático.

**Critical files:** novo `dbt/` na raiz, configuração de profile no `.env`.

**Status:** 📍 rascunho

---

### 15. 🟡 Logs estruturados em JSON ⏱️⏱️

**Problema:** logs em texto livre dificultam ingestão por Loki/ELK.

**Solução:** trocar `SingleLineFormatter` por `python-json-logger` ou `structlog`. Cada record vira JSON com `run_hash`, `table`, `process`, `level`, `message`, `duration_ms`.

**Memory note:** existe branch `feat/structured-logs` para isso (ver memory).

**Critical files:** `src/core/logger/standard_logger.py`, `src/core/logger/run_context.py`.

**Status:** 📍 rascunho · branch existente: `feat/structured-logs`

---

### 16. 🟡 Type hints completos + mypy strict ⏱️⏱️⏱️ (contínuo)

**Problema:** parcial. Algumas funções tipadas, outras não.

**Solução:** completar type hints em `src/processes/`, `src/core/table.py`, `src/factories/`. `mypy --strict` no CI (item 6).

**Critical files:** `src/processes/`, `src/core/table.py`, `src/factories/`.

**Status:** 📍 rascunho

---

### 17. ⚪ Backup automatizado de `.local/bot.db` ⏱️

**Problema:** SQLite do bot guarda histórico de jobs, audit, rate_limit. Servidor morre → perde tudo.

**Solução:** cron diário que faz `sqlite3 .local/bot.db ".backup .local/backups/bot-$(date +%F).db"` + envio para S3 / disco externo. Retenção 30 dias.

**Critical files:** `agendamentos_ETL.txt` ou `docs/agendamentos_ETL.txt`, novo `scripts/backup_botdb.sh`.

**Status:** 📍 rascunho

---

### 18. ⚪ Makefile / justfile ⏱️

**Problema:** comandos espalhados na documentação. Onboarding lento.

**Solução:** `Makefile` com targets: `make test`, `make lint`, `make run table=cliente`, `make backfill table=venda days=30`, `make logs date=2026-04-29`.

**Critical files:** novo `Makefile`.

**Status:** 📍 rascunho

---

## Tier C — Polimentos

### 19. ⚪ Bug fix em `src/core/databases/biNazaria.py`

Reutiliza variáveis `DB_BIMKTNAZ_POSTGRES_*` ao invés de `DB_BINAZARIA_*`. Provavelmente intencional (mesma instância), mas merece comentário explicativo ou variáveis dedicadas para evitar surpresa.

### 20. ⚪ Política de retenção de logs

Comprimir `logs/YYYY/MM/*.log` com mais de 30 dias para `.gz`, deletar com mais de 1 ano.

### 21. ⚪ Pre-commit hooks

`.pre-commit-config.yaml` com ruff, mypy leve, check-yaml, trailing-whitespace. Integra com item 6.

### 22. ⚪ Runbooks operacionais

Pasta `docs/runbooks/` com playbooks: "tabela X parou de atualizar", "Postgres rejeitando conexões", "bot Telegram offline".

### 23. ⚪ Substituir polling do bot por webhook

Telegram suporta webhook — mais eficiente que polling 30s. Requer item 2 (FastAPI) primeiro.

---

## Sequência sugerida de execução

| Sprint | Itens | Tema |
|--------|-------|------|
| **1** | 6 (CI/CD), 9 (pool), 15 (logs JSON), 17 (backup), 18 (Makefile) | Fundação rápida e barata |
| **2** | 3 (Prometheus/Grafana), 5 (watermarks), 10 (auditoria bot) | Observabilidade e segurança |
| **3** | 2 (FastAPI), 7 (Docker prod), 8 (vault) | Acessibilidade e segurança |
| **4** | 1 (orquestrador), 4 (schema-as-code), 14 (dbt) | Transformação arquitetural |
| **Contínuo** | 12 (testes), 16 (mypy), 22 (runbooks) | Qualidade |

---

## Critical files (resumo)

- **Entry/factories:** `run.py`, `src/factories/entity_registry.py`, `src/factories/database_factory.py`, `src/factories/mode_factory.py`
- **Processos ETL:** `src/processes/process.py`, `src/processes/full_query.py`, `src/processes/incremental.py`, `src/processes/monthly.py`, `src/processes/unit.py`, `src/processes/retry.py`
- **Carga e entidades:** `src/core/table.py`, `src/systems/pbs/entities/`, `src/systems/senior/entities/`, `src/systems/bimktnaz/entities/`
- **Conexões:** `src/core/databases/connections/{postgres,sqlserver,oracle}_connection.py`, `src/core/databases/{biMktNaz,biSenior,biNazaria,Senior,PBS_NAZARIA_DADOS}.py`
- **Logging:** `src/core/logger/{standard_logger,telegram_handler,error_parser,run_context}.py`
- **Bot:** `src/interfaces/bot/{runner,jobs,poll,auth,db,telegram,error_check}.py`, `src/interfaces/bot/commands/*`
- **SQLs:** `src/systems/pbs/sqls/`, `src/systems/senior/sqls/`, `src/systems/bimktnaz/sqls/`, `src/systems/pbs/sqls/biCompras/`
- **Testes:** `tests/conftest.py`, `tests/{unit,integration,e2e}/`
- **Build/deploy:** `requirements.txt`, `Dockerfile`, `pytest.ini`, `docs/agendamentos_ETL.txt`

---

## Verification

Como este é um documento de roadmap (não plano executável), a verificação é:

1. Validar com o time a priorização e o orçamento de esforço por sprint
2. Para cada item escolhido, criar `docs/plans/<nome>.md` no estilo de [`sla-implementation.md`](sla-implementation.md) com Context, Design, Critical files e Verification próprios
3. Atualizar a coluna `Status` deste arquivo conforme planos avançam

