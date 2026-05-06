# CLI Reference

## Usage

```bash
python run.py <command> [subcommand] [options]
```

## Commands

### `load` — Run ETL load

```bash
# Full load (truncate + insert)
python run.py load full --table myws/customer --truncate

# Incremental by days (multithreaded)
python run.py load incremental --table myws/sales --days 10 --threads 10

# Incremental with current day
python run.py load incremental --table myws/sales --days 1 --current-day

# Full incremental (no date loop)
python run.py load incremental --table myws/sales --full --truncate

# Monthly
python run.py load monthly --table myws/receivables --months 13

# Monthly — single interval
python run.py load monthly --table myws/balances --months 6 --method wholeInterval

# By business unit
python run.py load unit --table myws/inventory --unit 2
```

### `workspace` — Manage workspaces

```bash
python run.py workspace list              # list all
python run.py workspace validate          # test connections
python run.py workspace new local2        # create new YAML workspace
python run.py workspace delete local2     # soft delete
python run.py workspace restore local2    # restore from recycle bin
```

### `entity` — Manage entities

```bash
python run.py entity list                 # all entities
python run.py entity list myws            # filter by workspace
python run.py entity new myws/product     # create new entity
```

### `migrate` — Alembic migrations

```bash
python run.py migrate status -w myws
python run.py migrate upgrade -w myws
python run.py migrate create -w myws --autogenerate -m "add cpf column"
python run.py migrate rollback -w myws --steps 1
python run.py migrate stamp -w myws 0001
python run.py migrate validate -w myws
```

### `logs` — Inspect logs

```bash
python run.py logs errors                     # today's errors
python run.py logs errors --since 10:00 --until 16:00
python run.py logs errors --detailed
```

## Dagster Orchestration

```bash
# Validate definitions
dagster definitions validate -f orchestration/definitions.py

# List assets
dagster asset list -f orchestration/definitions.py

# Materialize one asset
dagster asset materialize --select myws__product -f orchestration/definitions.py

# Schedules
dagster schedule list -f orchestration/definitions.py
dagster schedule start job_daily_schedule -f orchestration/definitions.py

# UI / Daemon
dagster-webserver -w workspace.yaml -p 3000
dagster-daemon run -w workspace.yaml
```

## Parameter Reference

### `load full`

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--table` / `-t` | *required* | Entity name |
| `--workspace` / `-w` | None | Workspace id |
| `--truncate` | `False` | Truncate before insert |

### `load incremental`

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--table` / `-t` | *required* | Entity name |
| `--workspace` / `-w` | None | Workspace id |
| `--days` / `-d` | *required¹* | Days back to sync |
| `--threads` | `4` | Parallel threads (1-50) |
| `--truncate` | `False` | Truncate before processing |
| `--current-day` | `False` | Include today |
| `--full` | `False` | Full load without date filter |

> ¹ Not required when `--full` is used.

### `load monthly`

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--table` / `-t` | *required* | Entity name |
| `--workspace` / `-w` | None | Workspace id |
| `--months` / `-m` | *required¹* | Months back to sync |
| `--method` | `byMonth` | `byMonth` or `wholeInterval` |
| `--truncate` | `False` | Truncate before processing |
| `--full` | `False` | Full load without date filter |

### `load unit`

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--table` / `-t` | *required* | Entity name |
| `--workspace` / `-w` | None | Workspace id |
| `--unit` / `-u` | *required* | Business unit / CD id |
