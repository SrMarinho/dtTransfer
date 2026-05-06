# Monitoring

## Logs

Logs are written to `logs/<year>/<month>/<date>.log`.

### Checking Errors

```bash
# Today's errors
python run.py logs errors

# Errors between 10:00 and 16:00
python run.py logs errors --since 10:00 --until 16:00

# Full error messages
python run.py logs errors --detailed

# Specific date
python run.py logs errors --date 2025-01-15
```

### Live Tail

```bash
tail -f logs/$(date +%Y/%m)/$(date +%Y%m%d).log
```

## Telegram Notifications

If `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are configured:
- Error summaries are sent automatically
- Entity validation results can be notified with `--notify`

## Dagster

- Asset catalog: real-time execution history
- Schedules: track next tick and last run
- Sensors: health check every 10 minutes
