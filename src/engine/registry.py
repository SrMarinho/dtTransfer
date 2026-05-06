"""Process plug-in registry.

Built-in process types (full, incremental, monthly, unit) are recognized by
ProcessFactory. Custom process types register via:

    from src.engine import register_process, Process

    class MyProcess(Process):
        def __init__(self, table, params): ...
        def run(self): ...

    register_process("custom", MyProcess, params_parser=lambda d: ...)

Then `python run.py load` (or programmatic ProcessFactory) will dispatch
to it when invoked with that name.
"""

from typing import Callable, Dict, Optional, Tuple

_PROCESSES: Dict[str, Tuple[type, Optional[Callable]]] = {}


def register_process(
    name: str,
    cls: type,
    params_parser: Optional[Callable[[dict], object]] = None,
) -> None:
    """Register a custom process type.

    `params_parser` (optional) maps the raw params dict to a typed params
    object passed as the second argument to `cls.__init__`. If omitted, the
    raw dict is passed.
    """
    existing = _PROCESSES.get(name)
    if existing is not None and existing[0] is not cls:
        raise ValueError(
            f"process '{name}' already registered as {existing[0].__name__}"
        )
    _PROCESSES[name] = (cls, params_parser)


def get_process(name: str):
    return _PROCESSES.get(name)


def list_processes() -> list:
    return sorted(_PROCESSES)


__all__ = ["register_process", "get_process", "list_processes"]
