from dagster import asset, AssetExecutionContext
from orchestration._runner import run_etl
from orchestration._config import TABLE_PARAMS, VARIANT_PARENTS, AC_TABLES, ESTOQUE_UNITS
from src.factories.entity_registry import EntityRegistry


def _safe_name(key):
    return key.replace("/", "__").replace("-", "_")

def _group_for(key):
    if key.startswith("biNazaria/"):
        return "biNazaria"
    if key.startswith("biSenior/"):
        return "biSenior"
    if key.startswith("biMktNaz/"):
        return "biMktNaz"
    return "biMktNaz"


def _build_asset(asset_name, params):
    p = dict(params)
    real_table = p.pop("table", asset_name)

    @asset(name=_safe_name(asset_name), group_name=_group_for(asset_name))
    def _fn(context: AssetExecutionContext):
        run_etl(context, table=real_table, **p)

    return _fn


def build_all_assets():
    assets = []
    seen = set()

    for key in sorted(EntityRegistry.valid_tables()):
        if key in VARIANT_PARENTS:
            continue
        asset_name = key
        params = dict(TABLE_PARAMS.get(asset_name, {"process": "full", "truncate": True}))
        assets.append(_build_asset(asset_name, params))
        seen.add(asset_name)

    for asset_name, params in TABLE_PARAMS.items():
        if asset_name in seen:
            continue
        assets.append(_build_asset(asset_name, dict(params)))
        seen.add(asset_name)

    def _make_estoque_asset(unit):
        @asset(name=f"estoque_unit_{unit}", group_name="biMktNaz_estoque")
        def _fn(context: AssetExecutionContext):
            run_etl(context, table="estoque", process="unit", unit=unit)
        return _fn

    for unit_val in ESTOQUE_UNITS:
        assets.append(_make_estoque_asset(unit_val))

    return assets
