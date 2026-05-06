# Testing

## Executar

```bash
pytest -m "not integration and not e2e" -q   # rápido, sem DB
pytest tests/unit/workspace -q                # só workspace
pytest tests/bdd -q                           # BDD gherkin
pytest tests/                                 # tudo (precisa DB)
```

`pytest.ini` define `pythonpath = src`. Markers: `integration`, `e2e`.

## Workspace de teste isolado

SQLite local + workspace `example` (já incluso):

```bash
DB_EXAMPLE_SQLITE_DATABASE=/tmp/test.db python run.py migrate upgrade -w example
DB_EXAMPLE_SQLITE_DATABASE=/tmp/test.db python run.py load full -t example/sample
```

## Testar entity nova sem DB real

Use `driver: sqlite` + `env_prefix` apontando para arquivo temporário:

```python
import tempfile, os
from src.engine import bootstrap
from src.factories.entity_registry import EntityRegistry

with tempfile.NamedTemporaryFile(suffix=".db") as f:
    os.environ["DB_MEUWS_DATABASE"] = f.name
    bootstrap()
    entity = EntityRegistry.getInstance("meuws/produto", {})
    # ... rodar migration, popular, asserir
```

## Estrutura de testes

```
tests/
  unit/           — sem DB, mocks
  unit/workspace/ — registry, loader, YAML parsing
  bdd/            — discovery, isolation
  integration/    — drivers reais
  e2e/            — pipeline completa
  bot/            — Telegram
```

## Fixtures úteis

- `WorkspaceRegistry().clear()` — reset entre tests
- `EntityRegistry._workspace_entities = {}` — reset registro YAML
- `monkeypatch.setenv` — env vars de DB

