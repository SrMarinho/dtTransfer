# API: Process

```python
from src.engine import Process, FullQuery, Incremental, Monthly, Unit
```

## Base

```python
class Process(ABC):
    @abstractmethod
    def run(self): ...
```

Subclasse. Construtor recebe `(table: Entity, params: <typed>)` mais opcionais (`on_progress`, `retry_base_delay`, `retry_max_delay`).

## Built-in

| Tipo | Params | Comportamento |
|------|--------|---------------|
| `FullQuery` | `FullQueryParams(truncate)` | strip placeholders → SELECT → bulk insert |
| `Incremental` | `IncrementalParams(days, threads, truncate, current_day, full)` | gera intervalos diários → ThreadPoolExecutor |
| `Monthly` | `MonthlyParams(months, method, truncate, full)` | gera intervalos mensais (byMonth ou wholeInterval) |
| `Unit` | `UnitParams(unit)` | substitui `REPLACE_UNIT_HERE` |

`Incremental.run()` e `Monthly.run()` usam retry com backoff em erros transientes (importar de `src.processes.retry`).

## Registry custom

```python
from src.engine import register_process

register_process("cdc", CdcProcess, params_parser=parse_cdc)
```

`ProcessFactory.getInstance("cdc", params)` consulta o registry após não achar built-in.

## strip_date_filter

```python
from src.engine.process import strip_date_filter
strip_date_filter(query) -> str
```

Remove linhas com `REPLACE_START_DATE` ou `REPLACE_END_DATE`. Usado por `--full`.
