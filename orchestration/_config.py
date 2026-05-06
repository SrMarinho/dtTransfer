"""Entity configuration for Dagster asset building.

Override this file to configure custom process params per entity.
By default, process params are read from the entity's YAML spec.
"""

from src.factories.entity_registry import EntityRegistry


def get_process_params(entity_key: str) -> dict:
    """Return ETL process params for a given entity key (workspace/name).

    Priority:
    1. Entity YAML spec (process_type, incremental_column)
    2. Sensible defaults based on process_type

    Override TABLE_PARAMS dict below for fine-grained control.
    """
    base = {"truncate": True}

    try:
        instance = EntityRegistry.getInstance(entity_key, {})
        ptype = getattr(instance, "process_type", "full") or "full"
    except Exception:
        ptype = "full"

    base["process"] = ptype

    if ptype == "incremental":
        base.setdefault("days", 1)
        base.setdefault("threads", 4)
        base.setdefault("current_day", False)
    elif ptype == "monthly":
        base.setdefault("months", 1)
        base.setdefault("method", "byMonth")
    elif ptype == "full":
        base.setdefault("truncate", True)

    return base


# ── Override table params ─────────────────────────────────────────────────
# Uncomment and customize for your specific tables:
# TABLE_PARAMS = {
#     "myworkspace/orders": {"process": "incremental", "days": 10, "threads": 8},
#     "myworkspace/history": {"process": "monthly", "months": 13},
# }
TABLE_PARAMS: dict = {}
