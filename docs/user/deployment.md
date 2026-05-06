# Deployment & Scheduling

## Production Deploy

```bash
cd /opt/myapp
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt

# Apply pending migrations
python run.py migrate upgrade -w myws

# Validate connections
python run.py workspace validate
```

## Dagster (Orchestrator)

### Systemd services

```ini
# /etc/systemd/system/dagster-daemon.service
[Unit]
Description=Dagster Daemon — ETL
After=network.target

[Service]
User=myuser
WorkingDirectory=/opt/myapp
Environment=DAGSTER_HOME=/opt/myapp/.local/dagster
Environment=TZ=America/Fortaleza
EnvironmentFile=/opt/myapp/.env
ExecStart=/opt/myapp/.venv/bin/dagster-daemon run -w workspace.yaml
Restart=on-failure
RestartSec=15

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable dagster-daemon
sudo systemctl start dagster-daemon
```

### Full deploy with Dagster

```bash
git pull origin main
pip install -r requirements.txt
python run.py migrate upgrade -w myws
sudo systemctl restart dagster-daemon
```

## Scheduling (crontab)

```cron
CRON_TZ=America/Fortaleza
APP=/opt/myapp
PY=$APP/.venv/bin/python

# Dimensions — daily
0 5 * * * cd $APP && $PY run.py load full --table myws/product --truncate

# Transactional — every 3h
0 0-7/3 * * * cd $APP && $PY run.py load incremental --table myws/sales --days 10 --threads 10

# Monthly history
0 1 * * * cd $APP && $PY run.py load monthly --table myws/receivables --months 13

# Monitoring — every 30 min
*/30 * * * * cd $APP && $PY run.py logs errors
```

## Migrations

All schema changes must go through migrations — never directly on the database.

```bash
# Check status
python run.py migrate status -w myws

# Create (auto-detect)
python run.py migrate create -w myws --autogenerate -m "description"

# Apply
python run.py migrate upgrade -w myws

# Rollback
python run.py migrate rollback -w myws --steps 1
```

## Monitoring

```bash
# Live logs
tail -f logs/$(date +%Y/%m)/$(date +%Y%m%d).log

# Errors
python run.py logs errors

# Recent successful runs
grep "finalizado" logs/$(date +%Y/%m)/$(date +%Y%m%d).log | tail -10
```

Errors are sent to Telegram if `TELEGRAM_BOT_TOKEN` is configured.

## Troubleshooting

### `.env` not loaded

Use `EnvironmentFile` in systemd or `source` in crontab.

### Dagster daemon stopped

```bash
sudo systemctl status dagster-daemon
journalctl -u dagster-daemon -f
```

### Thread tuning

```bash
# Increase if CPU is underutilized
python run.py load incremental --table sales --days 10 --threads 15

# Decrease if DB contention
python run.py load incremental --table sales --days 10 --threads 5
```
