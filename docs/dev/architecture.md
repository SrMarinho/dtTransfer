# Architecture

## Directory Structure

```
/
├── run.py                              # CLI entry point
├── pyproject.toml                      # Python package config
├── pytest.ini                          # Test config
├── requirements.txt                    # Dependencies
├── .env / .env.example                 # Credentials
│
├── orchestration/                      # Dagster orchestration
│   ├── definitions.py                  # Entry point Definitions
│   ├── _runner.py                      # Subprocess → run.py CLI
│   ├── _config.py                      # Process params per entity
│   ├── _assets.py                      # Dynamic assets from EntityRegistry
│   ├── _schedules.py                   # Cron schedules
│   └── _sensors.py                     # Health check
│
├── schemas/                            # JSON Schemas for YAMLs
│   ├── workspace.json                  # Validates workspace.yml
│   └── entity.json                     # Validates entities/*.yml
│
├── dagster.yaml                        # Dagster config
├── workspace.yaml                      # Dagster workspace file
│
├── src/
│   ├── core/                           # Shared infrastructure
│   │   ├── entity.py                   # Base Entity class + filter_columns()
│   │   ├── databases/                  # Database connections
│   │   │   ├── connections/            # Drivers: Postgres, SQL Server, Oracle, SQLite
│   │   │   └── generic.py / fake_database.py
│   │   └── logger/                     # Logging (standard, Telegram, run_context)
│   │
│   ├── engine/                         # Public API + modern engine
│   │   ├── entity.py / workspace.py / process.py / driver.py / registry.py
│   │   ├── bootstrap.py / scaffold.py
│   │   ├── workspace/                  # Loader, registry, migrations, yaml_entity
│   │   └── drivers/                    # postgres, sqlserver, oracle, sqlite, fake
│   │
│   ├── factories/                      # Factories (legacy → engine transition)
│   │   ├── database_factory.py
│   │   ├── entity_registry.py
│   │   └── process_factory.py
│   │
│   ├── interfaces/                     # CLI + Telegram Bot
│   │   ├── cli/                        # Typer CLI
│   │   └── bot/                        # Telegram (auth, jobs, poll, runner)
│   │
│   ├── workspaces/                     # Workspace definitions
│   │   ├── example/                    # YAML + SQLite demo
│   │   └── ...                         # User-defined workspaces
│   │
│   └── processes/                      # Process implementations
│       ├── full_query.py
│       ├── incremental.py
│       ├── monthly.py
│       └── unit.py
│
├── docs/                               # Documentation
├── logs/                               # Rotated logs
└── tests/                              # Tests
    ├── unit/
    ├── integration/
    ├── e2e/
    └── bot/
```

## Execution Flow — CLI

```
run.py load full --table myws/customer
  └─ load.py → ModeFactory → ProcessFactory → EntityRegistry
       └─ Entity.getQuery() → SQL file
       └─ fromDriver (source) → fetch
       └─ filter_columns(table.columns, rows, cursor.description)
       └─ toDriver (target) → bulk_insert
```

## Execution Flow — Dagster

```
dagster asset materialize --select myws__customer
  └─ orchestration/definitions.py
       └─ _assets.py → build_all_assets()
            └─ EntityRegistry.valid_tables() → dynamic assets
            └─ _config.get_process_params() → process config
            └─ _runner.run_etl(context, table, **params)
                 └─ subprocess: run.py load full --table myws/customer
```

## filter_columns

`columns` in YAML acts as a filter + optional ordering:

```yaml
columns:
  - name
  - id
```

If omitted, all columns from `cursor.description` are used. Implemented as `src.core.entity.filter_columns()` and called in all 4 process types.

## Entity Resolution

Entity keys use the `<workspace>/<name>` namespace format:

```
'example/sample'     → SQLite (example workspace)
'myws/product'       → User-defined
```

No namespace collisions between workspaces.

## Workspace.enabled

Workspaces can be disabled without removal:

```yaml
# src/workspaces/local1/workspace.yml
enabled: false   # loader ignores, migrations not found, entities not registered
```

Default `true`. Omission = enabled.

## Conventions

- **Imports**: Absolute from `src.` (e.g. `from src.core.entity import Entity`)
- **Entities**: Extend `Entity`, define `fromDB`, `toDB`, `name`, `columns`
- **Processes**: Extend `Process`, implement `run()`
- **Tests**: `unit/` isolated, `integration/` with real DB, `e2e/` full pipeline
- **YAML Schema**: Every new `.yml` should have `$schema` pointing to `schemas/*.json`
