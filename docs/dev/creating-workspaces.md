# Creating a Workspace

A workspace is an isolated ETL pipeline unit: target DB, sources, entities, migrations.

## Scaffold

```bash
python run.py workspace new <id> --driver sqlite --env-prefix DB_<ID>
```

Cria `src/workspaces/<id>/`:

```
workspace.yml              # metadata
entities/                  # vazio — popule com `entity new`
sqls/                      # queries SQL
migrations/
  env.py                   # Alembic env
  script.py.mako           # template de revision
  versions/                # vazio — gerado por `migrate create`
```

## Estrutura de `workspace.yml`

```yaml
id: meuws                  # único, slug (letra inicial, letras/dígitos/_/-)
kind: yaml                 # sempre 'yaml' para novos workspaces

target:                    # destino dos dados
  name: target_db
  driver: postgres         # postgres|sqlserver|oracle|sqlite
  env_prefix: DB_MEUWS_PG  # vars: DB_MEUWS_PG_HOST, _PORT, _DATABASE, _USERNAME, _PASSWORD

sources:                   # origens (lista; pode ter várias)
  - name: erp_db
    driver: oracle
    env_prefix: DB_MEUWS_ORACLE
  - name: legado_db
    driver: sqlserver
    env_prefix: DB_MEUWS_SQLSRV
```

## Ciclo

1. `workspace new` — esqueleto
2. `entity new` — adicionar entidades (ver [creating-entities.md](creating-entities.md))
3. `migrate create` — gerar migration com DDL
4. `migrate upgrade` — aplicar
5. `load full|incremental|monthly|unit` — rodar pipeline

## Workspace externo (sem rebuild)

Coloque em qualquer pasta, aponte `WORKSPACES_DIR`:

```bash
export WORKSPACES_DIR=/srv/etl/workspaces
python run.py workspace list  # descobre os de lá também
```

Conflito de id: built-in (`src/workspaces/`) vence.

## Convenções

- `target_table` no entity YAML = nome físico em `target.driver`
- `columns:` lista plana — autoridade de schema é Alembic, não o YAML
- `sql_file:` resolvido relativo a `<workspace>/sqls/`
- Toda DDL em `migrations/versions/*.py`, nunca em código Python
