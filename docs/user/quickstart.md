# Quickstart — 5 minutes

From clone to first `load` running.

## 1. Setup

```bash
git clone <url> && cd <project>
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env  # edit credentials (or just DB_EXAMPLE_SQLITE_* for SQLite)
```

## 2. Create a workspace

```bash
python run.py workspace new myws --driver sqlite --env-prefix DB_MYWS
```

Creates `src/workspaces/myws/` with:

```
workspace.yml          # metadata
entities/              # 1 YAML per entity
sqls/                  # SQL queries
migrations/            # Alembic
```

## 3. Create an entity

```bash
python run.py entity new myws/product --process full
```

Edit `src/workspaces/myws/entities/product.yml` (adjust `columns:`) and `src/workspaces/myws/sqls/consulta_product.sql` (your extraction query).

## 4. Run migration

Create the table via Alembic:

```bash
python run.py migrate create -w myws -m "create product"
# edit the generated file in src/workspaces/myws/migrations/versions/
python run.py migrate upgrade -w myws
```

## 5. Execute load

```bash
python run.py load full --table myws/product --truncate
```

Done. Next: [workspaces.md](workspaces.md) for YAML details, [migrations.md](migrations.md) for Alembic.
