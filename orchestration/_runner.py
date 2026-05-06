import os, subprocess, sys

_PYTHON = sys.executable
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOAD_CMD_MAP = {
    "full": "full",
    "incremental": "incremental",
    "monthly": "monthly",
    "unit": "unit",
}

def run_etl(context, table, process="full", truncate=False, days=None, threads=None,
            current_day=False, months=None, method="byMonth", unit=None, full=None):
    subcmd = LOAD_CMD_MAP.get(process, "full")
    cmd = [_PYTHON, "run.py", "load", subcmd, "--table", table]
    if truncate:
        cmd.append("--truncate")
    if days is not None:
        cmd += ["--days", str(days)]
    if threads is not None:
        cmd += ["--threads", str(threads)]
    if current_day:
        cmd.append("--current-day")
    if months is not None:
        cmd += ["--months", str(months)]
    if method and process == "monthly":
        cmd += ["--method", method]
    if unit is not None:
        cmd += ["--unit", str(unit)]
    if full:
        cmd.append("--full")

    context.log.info(f"cmd: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=_ROOT, capture_output=True, text=True)
    if result.stdout:
        context.log.info(result.stdout.strip())
    if result.stderr:
        context.log.warning(result.stderr.strip())
    if result.returncode != 0:
        raise Exception(f"ETL falhou (exit {result.returncode}): {result.stderr[:500]}")
