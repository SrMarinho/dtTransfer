# Creating an Entity

An entity maps to one pipeline table: 1 YAML + 1 SQL.

## Scaffold

```bash
python run.py entity new meuws/produto --process full
```

Gera:

```
src/workspaces/meuws/entities/produto.yml
src/workspaces/meuws/sqls/consulta_produto.sql
```

## Estrutura de `entity.yml`

```yaml
name: produto                     # nome lógico (snake_case)
target_table: produto             # nome físico no target
source: erp_db                    # nome de uma ConnectionRef em sources
target: target_db                 # nome de target
process_type: full                # full|incremental|monthly|unit
sql_file: consulta_produto.sql    # relativo a sqls/
incremental_column: data_emissao  # opcional, só para incremental
columns:                          # lista plana (sem tipo)
  - codigo_produto
  - descricao
  - ncm
```

`columns:` deve corresponder à ordem do `SELECT` no SQL e ao schema Alembic.

## SQL

`sqls/consulta_produto.sql` recebe placeholders:

| Placeholder | Substituído por | Quando |
|-------------|-----------------|--------|
| `REPLACE_START_DATE` | data início (YYYY-MM-DD) | incremental, monthly |
| `REPLACE_END_DATE` | data fim | incremental, monthly |
| `REPLACE_UNIT_HERE` | id da unidade | unit |

Process `full` ignora placeholders. Para incremental sem filtro de data (ex: bootstrap), use `--full` que strip-a as linhas com placeholders.

Exemplo incremental:

```sql
SELECT
    codigo_produto,
    descricao,
    ncm
FROM erp.produto
WHERE data_alteracao BETWEEN 'REPLACE_START_DATE' AND 'REPLACE_END_DATE'
```

## Process types

| Type | Quando usar | Flags relevantes |
|------|-------------|------------------|
| `full` | Dim tables, masterdata sem volume | `--truncate` |
| `incremental` | Transacionais por dia | `--days N --threads M --current-day --full --truncate` |
| `monthly` | Balancetes, conciliação | `--months N --method byMonth\|wholeInterval --truncate --full` |
| `unit` | Particionado por unidade/CD | `--unit ID` |

## Execução

```bash
python run.py load full -t meuws/produto --truncate
python run.py load incremental -t meuws/notas --days 7 --threads 4
```

`-t meuws/produto` ou `--workspace meuws --table produto` (forma curta).
