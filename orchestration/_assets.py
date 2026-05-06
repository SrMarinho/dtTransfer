"""Dynamic Dagster asset builder.

Assets are built from every registered entity in EntityRegistry.
Process params (process_type, days, months, etc.) are resolved from
the entity YAML spec, falling back to get_process_params().
"""

from dagster import asset, AssetExecutionContext
from orchestration._runner import run_etl
from orchestration._config import get_process_params, TABLE_PARAMS
from src.factories.entity_registry import EntityRegistry


def _safe_name(key: str) -> str:
    return key.replace("/", "__").replace("-", "_")


def _group_for(key: str) -> str:
    ws = key.split("/", 1)[0] if "/" in key else key
    return ws


def _build_asset(asset_name: str, params: dict) -> callable:
    p = dict(params)
    real_table = p.pop("table", asset_name)

    @asset(name=_safe_name(asset_name), group_name=_group_for(asset_name))
    def _fn(context: AssetExecutionContext) -> None:
        run_etl(context, table=real_table, **p)

    return _fn


def build_all_assets() -> list[callable]:
    assets = []
    seen: set[str] = set()

    for key in sorted(EntityRegistry.valid_tables()):
        asset_name = key
        params = dict(TABLE_PARAMS.get(asset_name, {}))
        if not params:
            params = get_process_params(asset_name)
        assets.append(_build_asset(asset_name, params))
        seen.add(asset_name)

    # Also include any TABLE_PARAMS entries that aren't in the registry
    for asset_name, params in TABLE_PARAMS.items():
        if asset_name not in seen:
            assets.append(_build_asset(asset_name, dict(params)))
            seen.add(asset_name)

    return assets
