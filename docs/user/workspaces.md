# Workspaces

App is a generic engine. A workspace is a declarative bundle (sources + target + entities + SQLs + migrations) describing a replication flow. The engine discovers workspaces at runtime.

## Workspace types

| Type | How entities are defined | When to use |
|---|---|---|
| `yaml` | Declarative YAML in `entities/*.yml` | New workspaces. No Python per entity. |
| `python` | `Table` subclasses in `src/systems/<...>` | Legacy (removed in this template). |

## Location

Engine discovers workspaces from two directories:

1. **Built-in**: `src/workspaces/<id>/` (versioned in git).
2. **External**: `$WORKSPACES_DIR/<id>/` (volume mount, no rebuild).

Built-in takes precedence on id conflict. Directories without `workspace.yml` are ignored.

## YAML workspace structure

```
src/workspaces/<id>/
  workspace.yml          # metadata, sources, target
  entities/
    <name>.yml           # 1 entidade por arquivo
  sqls/
    <name>.sql           # query de extração
  migrations/
    env.py               # alembic env
    script.py.mako
    versions/
      0001_initial.py
```

### `workspace.yml`

```yaml
id: example
kind: yaml
target:
  name: target_pg
  driver: postgres
  env_prefix: DB_EXAMPLE_POSTGRES
sources:
  - name: source_pg
    driver: postgres
    env_prefix: DB_EXAMPLE_SOURCE_POSTGRES
```

`env_prefix` points to `<PREFIX>_HOST/_PORT/_DATABASE/_USERNAME/_PASSWORD` (Oracle also uses `_SERVICE_NAME` and `_ENCODING`).

Supported drivers: `postgres`, `sqlserver`, `oracle`, `sqlite`, `fake`.

### `entities/<name>.yml`

```yaml
name: sample
target_table: sample
source_ref: source_pg     # nome de connection em sources[]
target_ref: target_pg     # nome de connection em target
process_type: full        # full | incremental | monthly | unit
sql_file: sample.sql      # arquivo em sqls/
columns:
  - {name: id, type: integer, nullable: false, primary_key: true}
  - {name: nome, type: text, nullable: true}
```

## CLI

```
python run.py workspace list
python run.py entity list -w <id>
python run.py load full --table <id>/<entity>
python run.py migrate upgrade -w <id>
python run.py migrate status -w <id>
python run.py migrate validate -w <id>
```

## Migrations

Each workspace has its own isolated Alembic migrations in `<root>/migrations/versions/`. The app validates head at startup via `migrate validate`. Workflow:

1. Dev → add migration locally, run `migrate upgrade --workspace x`.
2. Staging/prod → during deploy, run `migrate upgrade` before starting the app.
3. App validates head at startup via `migrate validate`.

## Example workspace

`src/workspaces/example/` is a minimal SQLite template. Use it as a starting point.
