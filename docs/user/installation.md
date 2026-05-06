# Installation & Configuration

## System Requirements

- **Python**: 3.9+
- **Network access** to source and target databases
- **Drivers**:
  - ODBC Driver 18 for SQL Server
  - Oracle Instant Client (for Oracle connections)

On Ubuntu/Debian:
```bash
# SQL Server
sudo apt-get install odbc-driver-18-for-sql-server

# Oracle (if needed)
# Download from Oracle website and configure environment variables
```

On Windows:
- ODBC Driver: included with SQL Server or download separately
- Oracle Instant Client: extract and add to PATH

## Project Installation

### 1. Clone and virtual environment

```bash
git clone <repo-url>
cd <project>

# Create virtual environment
python -m venv venv

# Activate
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your real credentials
```

Each workspace uses `env_prefix` to resolve its connection variables. For a workspace with `env_prefix: DB_MYAPP`, the following variables are expected:

```
DB_MYAPP_HOST     = 127.0.0.1
DB_MYAPP_PORT     = 5432
DB_MYAPP_DATABASE = mydb
DB_MYAPP_USERNAME = user
DB_MYAPP_PASSWORD = secret
```

See `.env.example` for all supported variable patterns per driver.

### Telegram Notifications (Optional)

```env
TELEGRAM_BOT_TOKEN=your-token
TELEGRAM_CHAT_ID=your-chat-id
```

Get the token from BotFather (@BotFather on Telegram). Get the chat ID by sending a message to your bot and visiting `https://api.telegram.org/bot{TOKEN}/getUpdates`.

## Verification

### 1. Test imports

```bash
python -c "import psycopg2; import pyodbc; import oracledb; print('OK')"
```

### 2. Test connections

```bash
python run.py workspace validate
```

### 3. Test a small ETL

```bash
python run.py load full --table example/sample --truncate
# Check logs
cat logs/$(date +%Y/%m)/$(date +%Y%m%d).log
```

## Next Steps

Read [Quickstart](quickstart.md) to create your first workspace and entity.
