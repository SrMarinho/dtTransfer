from dagster import SensorDefinition, sensor, SensorEvaluationContext
from datetime import datetime, timezone


@sensor(minimum_interval_seconds=600)
def dagster_health_sensor(context: SensorEvaluationContext):
    context.log.info(f"health check at {datetime.now(timezone.utc).isoformat()}")

sensors: list[SensorDefinition] = [dagster_health_sensor]
