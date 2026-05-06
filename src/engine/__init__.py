"""DataReplicator engine — public API for building ETL workspaces.

Import from `src.engine.*` in new code. The legacy modules under
`src.core.*`, `src.factories.*`, `src.processes.*`, `src.engine.workspace.*` are
internal implementation details and exist only to support the legacy Python
entity bundles in `src/systems/`.

Public surface (lazy-resolved to avoid circular imports during bootstrap):
    from src.engine import (
        Entity, Table,
        Workspace, WorkspaceKind, ConnectionRef, EntitySpec, YamlTable,
        Process, FullQuery, Incremental, Monthly, Unit,
        Driver, register_driver, get_driver,
        register_process,
        bootstrap,
    )
"""

# Lazy attribute resolver — avoids loading heavy modules until accessed.
# Required because src.factories.database_driver_factory itself imports
# from src.engine.driver, creating a cycle if __init__ eagerly imports entity.

_LAZY = {
    "Entity": ("src.engine.entity", "Entity"),
    "Table": ("src.engine.entity", "Table"),
    "Workspace": ("src.engine.workspace", "Workspace"),
    "WorkspaceKind": ("src.engine.workspace", "WorkspaceKind"),
    "ConnectionRef": ("src.engine.workspace", "ConnectionRef"),
    "EntitySpec": ("src.engine.workspace", "EntitySpec"),
    "YamlTable": ("src.engine.workspace", "YamlTable"),
    "Process": ("src.engine.process", "Process"),
    "FullQuery": ("src.engine.process", "FullQuery"),
    "Incremental": ("src.engine.process", "Incremental"),
    "Monthly": ("src.engine.process", "Monthly"),
    "Unit": ("src.engine.process", "Unit"),
    "Driver": ("src.engine.driver", "Driver"),
    "register_driver": ("src.engine.driver", "register_driver"),
    "get_driver": ("src.engine.driver", "get_driver"),
    "register_process": ("src.engine.registry", "register_process"),
    "bootstrap": ("src.engine.bootstrap", "bootstrap"),
}


def __getattr__(name):
    if name in _LAZY:
        import importlib
        mod_name, attr = _LAZY[name]
        mod = importlib.import_module(mod_name)
        value = getattr(mod, attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module 'src.engine' has no attribute '{name}'")


def __dir__():
    return sorted(_LAZY)


__all__ = list(_LAZY)
