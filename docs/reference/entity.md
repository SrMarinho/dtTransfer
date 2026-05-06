# API: Entity

```python
from src.engine import Entity   # alias de Table
```

## Atributos

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `name` | `str` | nome físico da tabela no target |
| `columns` | `list[str]` | colunas em ordem do SELECT |
| `fromDB` | `Database \| (ws_id, ref_name)` | source (legacy enum ou tupla workspace) |
| `toDB` | mesmo | target |
| `query_path` | `str` | caminho do .sql |
| `params` | qualquer | params injetados pelo Process |

## Properties

- `fromDriver` — instância do DB wrapper (lazy, cached)
- `toDriver` — idem para target

## Métodos

| Método | Retorna | Descrição |
|--------|---------|-----------|
| `getQuery()` | `str` | lê `sql_file` |
| `insert(rows)` | `None` | delega para `toDriver.getDriver().bulk_insert` |
| `existsTable()` | `bool` | check em `information_schema` |
| `truncate()` | `None` | DELETE FROM (não TRUNCATE) |
| `createTable()` | `None` | YAML: roda Alembic upgrade head; legacy: override custom |
| `deleteDay(start, end)` | `None` | hook para incremental, override por entity |

## YamlTable

Subclasse para entidades YAML. Inicializada com `(spec: EntitySpec, workspace: Workspace, params)`. Define `name`, `columns`, `fromDB=(ws.id, spec.source)`, `toDB=(ws.id, spec.target)`, `query_path` automaticamente.
