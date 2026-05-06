from src.core.logger.logging import logger
from src.core.settings import THREADS_NUM
from src.factories.entity_registry import EntityRegistry
from src.processes.full_query import FullQuery
from src.processes.incremental import Incremental
from src.processes.monthly import Monthly
from src.processes.unit import Unit
from src.processes.params import FullQueryParams, IncrementalParams, MonthlyParams, UnitParams


def _to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() == "true"


def _parse_full(params: dict) -> FullQueryParams:
    return FullQueryParams(
        truncate=_to_bool(params.get("truncate", False)),
    )


def _parse_incremental(params: dict) -> IncrementalParams:
    days_raw = params.get("days")
    days = int(days_raw) if days_raw is not None else None
    threads_raw = params.get("threads", THREADS_NUM)
    return IncrementalParams(
        days=days,
        threads=int(threads_raw),
        truncate=_to_bool(params.get("truncate", False)),
        current_day=_to_bool(params.get("currentDay", False)),
        full=_to_bool(params.get("full", False)),
    )


def _parse_monthly(params: dict) -> MonthlyParams:
    months_raw = params.get("months")
    months = int(months_raw) if months_raw is not None else None
    return MonthlyParams(
        months=months,
        method=params.get("method", "byMonth"),
        truncate=_to_bool(params.get("truncate", False)),
        full=_to_bool(params.get("full", False)),
    )


def _parse_unit(params: dict) -> UnitParams:
    return UnitParams(unit=int(params.get("unit", 0)))


class ProcessFactory:
    @staticmethod
    def getInstance(name: str, params: dict, on_progress=None):
        table = EntityRegistry.getInstance(params["table"], params)

        if name == "full":
            return FullQuery(table, _parse_full(params))

        if name == "incremental":
            retry_base = float(params.get("retry_base_delay", 30.0))
            retry_max = float(params.get("retry_max_delay", 120.0))
            return Incremental(
                table,
                _parse_incremental(params),
                on_progress=on_progress,
                retry_base_delay=retry_base,
                retry_max_delay=retry_max,
            )

        if name == "monthly":
            retry_base = float(params.get("retry_base_delay", 30.0))
            retry_max = float(params.get("retry_max_delay", 120.0))
            return Monthly(
                table,
                _parse_monthly(params),
                on_progress=on_progress,
                retry_base_delay=retry_base,
                retry_max_delay=retry_max,
            )

        if name == "unit":
            return Unit(table, _parse_unit(params))

        # Custom process types registered via src.engine.register_process
        from src.engine.registry import get_process
        custom = get_process(name)
        if custom is not None:
            cls, parser = custom
            parsed = parser(params) if parser else params
            return cls(table, parsed)

        logger.error(f"{name} - Processo não encontrado!")
        raise ValueError(f"{name} - Processo não encontrado!")
