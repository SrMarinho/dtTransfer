# {{ cookiecutter.project_name }}

Declarative ETL engine. Define data pipelines in YAML — no Python per entity.

```
src/workspaces/<id>/
  workspace.yml          # metadata, sources, target
  entities/<name>.yml    # 1 entity per file
  sqls/<name>.sql        # extraction query
  migrations/            # Alembic
```

## Quick Start

```bash
git clone <url> && cd {{ cookiecutter.project_slug }}
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
```

### Create your first workspace

```bash
python run.py workspace new myworkspace --driver postgres
```

### Add an entity

```bash
python run.py entity new myworkspace/customers --process incremental
```

### Run ETL

```bash
python run.py load full --table myworkspace/customers --truncate
python run.py load incremental --table myworkspace/orders --days 10 --threads 4
python run.py load monthly --table myworkspace/reports --months 13
```

## CLI

| Command | Description |
|---------|-------------|
| `workspace list` | List active workspaces |
| `workspace validate` | Test all DB connections |
| `workspace new` | Scaffold a new workspace |
| `entity list` | List registered entities |
| `entity new` | Scaffold a new entity |
| `entity validate insert` | Test INSERT on an entity |
| `load full` | Full truncate + reload |
| `load incremental` | Incremental by N days |
| `load monthly` | Incremental by N months |
| `load unit` | Load by business unit |
| `migrate upgrade` | Run Alembic migrations |
| `logs errors` | Inspect error logs |

## Dagster Orchestration

```bash
dagster-daemon run -w workspace.yaml
dagster-webserver -w workspace.yaml -p 3000
```

Assets are built dynamically from registered entities.

## Documentation

| Topic | Link |
|-------|------|
| Installation | [docs/user/installation.md](docs/user/installation.md) |
| CLI | [docs/user/cli.md](docs/user/cli.md) |
| Workspaces | [docs/user/workspaces.md](docs/user/workspaces.md) |
| Processes | [docs/user/processes.md](docs/user/processes.md) |
| Migrations | [docs/user/migrations.md](docs/user/migrations.md) |
| Deployment | [docs/user/deployment.md](docs/user/deployment.md) |
| Architecture | [docs/dev/architecture.md](docs/dev/architecture.md) |
| Creating Entities | [docs/dev/creating-entities.md](docs/dev/creating-entities.md) |
| Creating Workspaces | [docs/dev/creating-workspaces.md](docs/dev/creating-workspaces.md) |
| Custom Drivers | [docs/dev/custom-drivers.md](docs/dev/custom-drivers.md) |
| Custom Processes | [docs/dev/custom-processes.md](docs/dev/custom-processes.md) |

## Supported Drivers

- PostgreSQL
- SQL Server (pyodbc)
- Oracle (oracledb)
- SQLite

## Stack

Python 3.9+ · Typer CLI · Dagster · Alembic · JSON Schema · Pydantic
