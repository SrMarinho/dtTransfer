# Deployment & Agendamentos

## Deploy em Produção

```bash
cd /opt/nzretlconnect/biMktNaz
git pull origin main
source bimktnaz/bin/activate
pip install -r requirements.txt

# Aplicar migrations pendentes
python run.py migrate upgrade -w biMktNaz
python run.py migrate upgrade -w biSenior
python run.py migrate upgrade -w biNazaria

# Validar conexões
python run.py workspace validate
```

---

## Dagster (novo orquestrador)

### Systemd services

```ini
# /etc/systemd/system/dagster-daemon.service
[Unit]
Description=Dagster Daemon — DataReplicator ETL
After=network.target

[Service]
User=nzretlconnect
WorkingDirectory=/opt/nzretlconnect/biMktNaz
Environment=DAGSTER_HOME=/opt/nzretlconnect/biMktNaz/.local/dagster
Environment=LD_LIBRARY_PATH=/opt/oracle/instantclient_21_12
Environment=TZ=America/Fortaleza
EnvironmentFile=/opt/nzretlconnect/biMktNaz/.env
ExecStart=/opt/nzretlconnect/biMktNaz/bimktnaz/bin/dagster-daemon run -w workspace.yaml
Restart=on-failure
RestartSec=15

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start dagster-daemon
sudo systemctl start dagster-webserver   # opcional (apenas UI)
```

### Deploy completo com Dagster

```bash
git pull origin main
pip install -r requirements.txt
python run.py migrate upgrade -w biMktNaz
sudo systemctl restart dagster-daemon dagster-webserver
# Verificar: dagster definitions validate -f orchestration/definitions.py
```

→ [Plano de migração completo](docs/plans/orchestrator-dagster.md)

---

## Agendamentos (crontab — legado)

Agendamentos completos em `docs/agendamentos_ETL.txt`. Timezone: `America/Fortaleza`.

```cron
CRON_TZ=America/Fortaleza
APP=/opt/nzretlconnect/biMktNaz
PY=$APP/bimktnaz/bin/python

# Dimensões — 5h
0 5 * * * source ~/.bashrc && cd $APP && $PY run.py load full --table cliente --truncate

# Transacional — a cada 3h
0 0-7/3 * * * source ~/.bashrc && cd $APP && $PY run.py load incremental --table venda --days 10 --threads 10

# Histórico mensal — 1h
0 1 * * * source ~/.bashrc && cd $APP && $PY run.py load monthly --table titulos_contas_receber --months 13

# Monitoramento — a cada 30 min
*/30 * * * * source ~/.bashrc && cd $APP && $PY run.py logs errors
```

---

## Migrations

Toda mudança de schema deve ser via migration — nunca diretamente no banco.

```bash
# Ver estado
python run.py migrate status -w biMktNaz

# Criar (auto-detect)
python run.py migrate create -w biMktNaz --autogenerate -m "descricao"

# Aplicar
python run.py migrate upgrade -w biMktNaz

# Desfazer
python run.py migrate rollback -w biMktNaz --steps 1
```

---

## Monitoramento

```bash
# Logs em tempo real
tail -f logs/2026/04/20260430.log

# Erros do dia
python run.py logs errors

# Últimas execuções bem-sucedidas
grep "finalizado" logs/2026/04/20260430.log | tail -10
```

Erros enviados ao Telegram se `TELEGRAM_BOT_TOKEN` configurado.

---

## Troubleshooting

### `.env` não carregado

Use `EnvironmentFile` no systemd ou `source ~/.bashrc` no cron.

### Dagster daemon parou

```bash
sudo systemctl status dagster-daemon
journalctl -u dagster-daemon -f
# Health check automático via cron a cada 10 min
```

### Tuning de threads

```bash
# Aumentar se CPU subutilizada
python run.py load incremental --table venda --days 10 --threads 15

# Diminuir se contenção no banco
python run.py load incremental --table venda --days 10 --threads 5
```
