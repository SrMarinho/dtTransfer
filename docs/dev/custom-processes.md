# Custom Process

Built-in: `full`, `incremental`, `monthly`, `unit` (see [user/processes.md](../user/processes.md)). Add a new type (CDC, daily snapshot, streaming) without editing core.

## API

```python
from dataclasses import dataclass
from src.engine import Process, register_process


@dataclass
class CdcParams:
    since_lsn: str
    batch_size: int = 1000


def parse_cdc(params: dict) -> CdcParams:
    return CdcParams(
        since_lsn=params["since_lsn"],
        batch_size=int(params.get("batch_size", 1000)),
    )


class CdcProcess(Process):
    def __init__(self, table, params: CdcParams):
        self.table = table
        self.params = params

    def run(self):
        rows = self._fetch_changes()
        self.table.insert(rows)


register_process("cdc", CdcProcess, params_parser=parse_cdc)
```

Depois `ProcessFactory.getInstance("cdc", params)` resolve para `CdcProcess`.

## Quando registrar

- **Plugin module**: `src/plugins/cdc.py` importado por `bootstrap` ou `run.py`
- **Workspace `__init__.py`** (Python kind) — chamado pelo loader
- **Entry point** (futuro): `pyproject.toml [project.entry-points."datareplicator.processes"]`

## CLI

`load full|incremental|monthly|unit` no `run.py` é hardcoded. Para custom, adicione um comando próprio em `src/interfaces/cli/groups/`:

```python
# src/interfaces/cli/groups/cdc.py
import typer
from src.factories.process_factory import ProcessFactory

app = typer.Typer()

@app.command()
def cdc_run(table: str, since_lsn: str):
    proc = ProcessFactory.getInstance("cdc", {"table": table, "since_lsn": since_lsn})
    proc.run()
```

E em `run.py`:

```python
from src.interfaces.cli.groups.cdc import app as cdc_app
app.add_typer(cdc_app, name="cdc")
```

## Convenções

- `Process.run()` é o único método obrigatório
- Parser de params devolve dataclass tipada (não dict solto)
- Use `table.toDriver.bulk_insert(conn, name, columns, rows)` para insert eficiente
- Para retry/backoff, copie o padrão de `src/processes/incremental.py`
