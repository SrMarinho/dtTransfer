"""Dagster schedule definitions.

Override this file to define your own cron schedules.
Assets are built dynamically from EntityRegistry (see _assets.py).

Usage:
    from dagster import ScheduleDefinition, define_asset_job, AssetSelection

    ScheduleDefinition(
        job=define_asset_job("my_job", selection=AssetSelection.groups("mygroup")),
        cron_schedule="0 3 * * *",
        execution_timezone="America/Fortaleza",
    )
"""

from dagster import ScheduleDefinition

# ── Example schedule ───────────────────────────────────────────────────────
# schedules = [
#     ScheduleDefinition(
#         job=define_asset_job("job_daily", selection=AssetSelection.groups("myworkspace")),
#         cron_schedule="0 3 * * *",
#         execution_timezone="America/Fortaleza",
#     ),
# ]

schedules: list[ScheduleDefinition] = []
