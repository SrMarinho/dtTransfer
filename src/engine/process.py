"""Process API.

Base `Process` and built-in process types. Use `register_process` from
`src.engine.registry` to plug a custom process type.
"""

from src.processes.process import Process, strip_date_filter
from src.processes.full_query import FullQuery
from src.processes.incremental import Incremental
from src.processes.monthly import Monthly
from src.processes.unit import Unit
from src.processes.params import (
    FullQueryParams,
    IncrementalParams,
    MonthlyParams,
    UnitParams,
)

__all__ = [
    "Process",
    "FullQuery",
    "Incremental",
    "Monthly",
    "Unit",
    "FullQueryParams",
    "IncrementalParams",
    "MonthlyParams",
    "UnitParams",
    "strip_date_filter",
]
