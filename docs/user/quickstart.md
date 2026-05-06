# Quickstart — 5 minutos

Da clonagem ao primeiro `load` rodando.

## 1. Setup

```bash
git clone <url> && cd biMktNaz
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env  # preencher credenciais (ou só DB_MEUWS_DATABASE para SQLite)
```

## 2. Criar workspace

```bash
python run.py workspace new meuws --driver sqlite --env-prefix DB_MEUWS
```

Cria `src/workspaces/meuws/` com:

```
workspace.yml          # metadata
entities/              # 1 YAML por entidade
sqls/                  # queries SQL
migrations/            # Alembic
```

## 3. Criar entity

```bash
python run.py entity new meuws/produto --process full
```

Edite `src/workspaces/meuws/entities/produto.yml` ajustando `columns:` e `src/workspaces/meuws/sqls/consulta_produto.sql` com sua query.

## 4. Rodar migration

Crie tabela em `migrations/versions/`:

```bash
python run.py migrate create -w meuws -m "create produto"
# edita o arquivo gerado em src/workspaces/meuws/migrations/versions/
python run.py migrate upgrade -w meuws
```

## 5. Executar load

```bash
python run.py load full --table meuws/produto --truncate
```

Pronto. Próximo: [workspaces.md](workspaces.md) para detalhes do YAML, [migrations.md](migrations.md) para Alembic.
