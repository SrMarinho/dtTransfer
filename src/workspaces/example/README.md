# Example Workspace

A sample YAML workspace to demonstrate the workspace structure. Use it as a starting point for your own.

## Structure

```
example/
  workspace.yml          # metadata, sources, target
  entities/
    sample.yml           # one entity per file
  sqls/
    sample.sql           # extraction query from source
  migrations/
    env.py               # alembic env (generic, can be reused)
    script.py.mako       # migration template
    versions/
      0001_initial.py    # versioned migrations
```

## Environment Variables

```
DB_EXAMPLE_SQLITE_DATABASE=/tmp/example.db
DB_EXAMPLE_SOURCE_SQLITE_DATABASE=/tmp/example_source.db
```

## Commands

```bash
python run.py workspace list
python run.py entity list
python run.py migrate upgrade --workspace example
python run.py migrate status --workspace example
python run.py load full --table example/sample
```
