# DataReplicator

ETL engine + Dagster orchestration. Replica SQL Server/Oracle → PostgreSQL. 130+ entidades com batch insert, multithreading e schedules versionadas.

| Origem | Destino | Sistema |
|--------|---------|---------|
| SQL Server | PostgreSQL | biMktNaz |
| Oracle | PostgreSQL | biSenior |
| SQL Server | PostgreSQL | biNazaria |

---

## Setup

```bash
git clone <url> && cd DataReplicator
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env  # preencher credenciais
```

→ [Instalação detalhada](docs/user/installation.md)

---

## CLI

```bash
# Carga completa
python run.py load full --table cliente --truncate

# Incremental
python run.py load incremental --table venda --days 10 --threads 10

# Mensal
python run.py load monthly --table titulos_contas_receber --months 13

# Por unidade
python run.py load unit --table estoque --unit 2

# Diagnostics
python run.py workspace list
python run.py entity list
python run.py workspace validate
python run.py logs errors

# Migrations
python run.py migrate upgrade -w biMktNaz
python run.py migrate status -w biMktNaz
```

→ [CLI completo](docs/user/cli.md) | [Processos](docs/user/processes.md) | [Workspaces](docs/user/workspaces.md)

---

## Dagster Orchestration (novo)

Orquestrador via **Dagster OSS**. Schedules, retry 1-click, backfill, asset catalog, logs em tempo real.

```bash
# Terminal 1 — daemon (executa schedules)
$env:DAGSTER_HOME = ".local/dagster"
dagster-daemon run -w workspace.yaml

# Terminal 2 — webserver (UI)
dagster-webserver -w workspace.yaml -p 3000

# Materializar manualmente
dagster asset materialize --select cliente -f orchestration/definitions.py

# Ver schedules
dagster schedule list -f orchestration/definitions.py
```

189 assets gerados dinamicamente do EntityRegistry, 27 schedules do crontab, 17 unidades de estoque.

→ [Plano de migração](docs/plans/orchestrator-dagster.md)

---

## YAML Workspaces

Workspaces declarativos sem código Python por entidade:

```
src/workspaces/<id>/
  workspace.yml          # metadata, sources, target
  entities/<name>.yml    # 1 entidade por arquivo
  sqls/<name>.sql        # query de extração
  migrations/            # Alembic
```

Schema validado via `$schema` → autocomplete no VSCode.

→ [Workspaces](docs/user/workspaces.md) | [Schemas JSON](schemas/)

---

## Documentação

| Tópico | Link |
|--------|------|
| Instalação | [installation.md](docs/user/installation.md) |
| CLI | [cli.md](docs/user/cli.md) |
| Workspaces YAML | [workspaces.md](docs/user/workspaces.md) |
| Dagster | [orchestrator-dagster.md](docs/plans/orchestrator-dagster.md) |
| Deployment | [deployment.md](docs/user/deployment.md) |
| Architecture | [architecture.md](docs/dev/architecture.md) |

---

## Stack

- Python 3.9+ · PostgreSQL · SQL Server (pyodbc) · Oracle (oracledb) · SQLite
- Typer CLI · Dagster 1.12 · Alembic · JSON Schema · Telegram Bot API
