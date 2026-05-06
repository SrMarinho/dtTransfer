# Workspaces

App = engine genérico. Workspace = bundle declarativo (sources + target + entidades + SQLs + migrations) que descreve um fluxo de replicação. Engine não conhece nenhum workspace específico — descobre em runtime.

## Tipos de workspace

| Tipo | Como define entidades | Quando usar |
|---|---|---|
| `yaml` | YAML declarativo em `entities/*.yml` | Novos workspaces. Sem código Python por entidade. |
| `python` | Subclasses `Table` em `src/systems/<...>` | Legados (`biSenior`, `biMktNaz`, `biNazaria`). Removível. |

## Localização

Engine descobre workspaces em duas pastas:

1. **Built-in**: `src/workspaces/<id>/` (versionado em git).
2. **Externo**: `$WORKSPACES_DIR/<id>/` (volume mount, sem rebuild).

Built-in tem precedência em conflito de id. Pasta sem `workspace.yml` ou `__init__.py` é ignorada.

## Estrutura de um workspace YAML

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

`env_prefix` aponta pras vars `<PREFIX>_HOST/_PORT/_DATABASE/_USERNAME/_PASSWORD` (Oracle também usa `_SERVICE_NAME` e `_ENCODING`).

Drivers suportados: `postgres`, `sqlserver`, `oracle`, `sqlite`, `fake`.

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

Cada workspace tem suas próprias migrations Alembic isoladas em `<root>/migrations/versions/`. Aplicação não roda upgrade automático — falha no startup se DB estiver atrás. Workflow:

1. Dev → adiciona migration localmente, roda `migrate upgrade --workspace x`.
2. Homo/prod → durante deploy, antes de subir app, rodar `migrate upgrade`.
3. App valida head no startup via `migrate validate`.

## Workspace exemplo

`src/workspaces/example/` é um template SQLite minimal. Use como base.

> Para migração de entidades legacy, veja [legacy-systems.md](../legacy/legacy-systems.md).
