from dataclasses import dataclass
from typing import Optional


@dataclass
class FullQueryParams:
    truncate: bool = False


@dataclass
class IncrementalParams:
    days: Optional[int] = None
    threads: int = 4
    truncate: bool = False
    current_day: bool = False
    full: bool = False


@dataclass
class MonthlyParams:
    months: Optional[int] = None
    method: str = "byMonth"
    truncate: bool = False
    full: bool = False


@dataclass
class UnitParams:
    unit: int = 0
