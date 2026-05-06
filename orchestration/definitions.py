from dagster import Definitions
from orchestration._assets import build_all_assets
from orchestration._schedules import schedules
from orchestration._sensors import sensors

all_assets = build_all_assets()

defs = Definitions(
    assets=all_assets,
    schedules=schedules,
    sensors=sensors,
)
