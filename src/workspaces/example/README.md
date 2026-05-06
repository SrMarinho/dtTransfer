# Workspace exemplo

Template de workspace YAML. Use como base pra criar seus próprios.

## Estrutura

```
example/
  workspace.yml          # metadata, sources, target
  entities/
    sample.yml           # 1 entidade por arquivo
  sqls/
    sample.sql           # query de extração da source
  migrations/
    env.py               # alembic env (genérico, pode reusar)
    script.py.mako       # template de migration
    versions/
      0001_initial.py    # migrations versionadas
```

## Variáveis de ambiente

```
DB_EXAMPLE_SQLITE_DATABASE=/tmp/example.db
DB_EXAMPLE_SOURCE_SQLITE_DATABASE=/tmp/example_source.db
```

## Comandos

```
python run.py list-workspaces list-workspaces
python run.py migrate upgrade --workspace example
python run.py migrate status --workspace example
```
