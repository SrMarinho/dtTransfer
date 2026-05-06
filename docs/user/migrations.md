# Migrations

DataReplicator usa **Alembic** em modo raw SQL (sem ORM) para versionar mudanças de schema nos bancos de destino. Cada workspace tem migrations **isoladas** em `src/workspaces/<id>/migrations/`.

---

## Comandos

```bash
python run.py migrate upgrade -w meuws              # aplica pendentes
python run.py migrate upgrade -w meuws -r 0002      # até revisão específica

python run.py migrate status -w meuws               # versão atual + última disponível
python run.py migrate rollback -w meuws              # desfaz último migration
python run.py migrate rollback -w meuws --steps 2    # desfaz 2

python run.py migrate stamp -w meuws 0001            # marca revisão como aplicada sem executar
python run.py migrate create -w meuws -m "descricao" # gera nova migration
python run.py migrate validate -w meuws              # falha se DB não estiver no head
```

---

## Estrutura

Cada workspace YAML carrega suas próprias migrations:

```
src/workspaces/meuws/
  workspace.yml
  entities/            # YAML de entidades
  sqls/                # queries de extração
  migrations/
    env.py             # env.py do Alembic (gerado no scaffold)
    script.py.mako     # template de revision
    versions/          # gerado por `migrate create`
      0001_initial.py
```

Workspaces Python legacy (`biMktNaz`, `biSenior`, `biNazaria`) ainda não possuem migrations — usam o sistema antigo de `createTable()` inline. Ao converter para YAML, o scaffold inclui migrations.

---

## Criando uma nova migration

```bash
python run.py migrate create -w meuws -m "add coluna email"
```

Gera um arquivo em `src/workspaces/meuws/migrations/versions/`. Editar:

```python
def upgrade() -> None:
    op.add_column("produto", sa.Column("email", sa.Text, nullable=True))

def downgrade() -> None:
    op.drop_column("produto", "email")
```

Aplicar:

```bash
python run.py migrate upgrade -w meuws
```

### Autogenerate

```bash
python run.py migrate create -w meuws -m "add coluna email" --autogenerate
```

Compara o schema atual do banco com os modelos SQLAlchemy (se houver) e gera a migration automaticamente.

---

## Setup inicial (banco existente)

Para um banco que já existe em produção, crie um workspace e marque o baseline sem re-executar DDL.

### 1. Criar workspace

```bash
python run.py workspace new meuws --driver postgres --env-prefix DB_MEUWS
```

### 2. Gerar baseline SQL

```bash
pg_dump --schema-only -n public -d <banco> > src/workspaces/meuws/migrations/versions/0001_baseline.sql
```

### 3. Criar migration Python que aplica o SQL

Crie `src/workspaces/meuws/migrations/versions/0001_baseline.py`:

```python
"""baseline

Revision ID: 0001
Revises:
"""
from alembic import op

revision = "0001"
down_revision = None

def upgrade():
    with open(op.get_context().script.dir / "versions" / "0001_baseline.sql") as f:
        op.execute(f.read())

def downgrade():
    pass
```

### 4. Marcar como aplicado

```bash
python run.py migrate stamp -w meuws 0001
```

### 5. Verificar

```bash
python run.py migrate status -w meuws
# Deve mostrar: current: 0001 | available: 0001 | in sync: True
```

---

## Regras

- **Nunca alterar schema diretamente** — sempre via migration
- **Sempre implementar `downgrade()`** — mesmo que seja um `pass` documentado
- **Um migration por mudança lógica** — não agrupar ALTER TABLE não relacionados
- **Testar em desenvolvimento antes de aplicar em produção**
- **Commitar o arquivo de migration junto com o código** que depende da mudança

---

## Fluxo em deploy

```bash
git pull origin main
pip install -r requirements.txt

# Validar que todas as migrations estão aplicadas
python run.py migrate validate -w meuws

# Se falhar, aplicar pendentes
python run.py migrate upgrade -w meuws
```
