# Instalação & Configuração

## Requisitos do Sistema

- **Python**: 3.9+
- **Acesso de rede** aos bancos de dados (origem e destino)
- **Drivers**:
  - ODBC Driver 18 for SQL Server (para SQL Server)
  - Oracle Instant Client (para Oracle)

No Ubuntu/Debian:
```bash
# SQL Server
sudo apt-get install odbc-driver-18-for-sql-server

# Oracle (se necessário)
# Baixar do site Oracle e configurar variáveis de ambiente
```

No Windows:
- ODBC Driver: vem com SQL Server ou baixar separado
- Oracle Instant Client: descompactar e adicionar ao PATH

## Instalação do Projeto

### 1. Clone e ambiente virtual

```bash
git clone <url-repositorio>
cd DataReplicator

# Crie um ambiente virtual
python -m venv venv

# Ative
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. Instale dependências

```bash
pip install -r requirements.txt
```

**Dependências principais**:
- `psycopg2-binary==2.9.10` — PostgreSQL
- `pyodbc==5.1.0` — SQL Server
- `oracledb==1.2.2` — Oracle
- `python-dotenv==1.0.1` — carregamento de `.env`
- `python-dateutil==2.9.0.post0` — date utilities
- `pyyaml==6.0.2` — parsing de YAML (SLA config)

### 3. Configure variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com as credenciais reais
```

## Arquivo `.env`

### Logging

```env
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR | CRITICAL
```

### SQL Server — PBS Nazaria

```env
DB_NAZARIA_SQLSERVER_HOST=seu-servidor
DB_NAZARIA_SQLSERVER_PORT=1433
DB_NAZARIA_SQLSERVER_DATABASE=nome_db
DB_NAZARIA_SQLSERVER_USERNAME=usuario
DB_NAZARIA_SQLSERVER_PASSWORD=senha
```

### PostgreSQL — biMktNaz (destino)

```env
DB_BIMKTNAZ_POSTGRES_HOST=localhost
DB_BIMKTNAZ_POSTGRES_PORT=5432
DB_BIMKTNAZ_POSTGRES_DATABASE=biMktNaz
DB_BIMKTNAZ_POSTGRES_USERNAME=usuario
DB_BIMKTNAZ_POSTGRES_PASSWORD=senha
```

### Oracle — Senior (origem)

```env
DB_SENIOR_ORACLE_HOST=seu-servidor
DB_SENIOR_ORACLE_PORT=1521
DB_SENIOR_ORACLE_SERVICE_NAME=SERVICENAME
DB_SENIOR_ORACLE_USER=usuario
DB_SENIOR_ORACLE_PASSWORD=senha
DB_SENIOR_ORACLE_ENCODING=utf8
```

### PostgreSQL — biSenior (destino)

```env
DB_BISENIOR_POSTGRES_HOST=localhost
DB_BISENIOR_POSTGRES_PORT=5432
DB_BISENIOR_POSTGRES_DATABASE=biSenior
DB_BISENIOR_POSTGRES_USERNAME=usuario
DB_BISENIOR_POSTGRES_PASSWORD=senha
```

### Telegram (Notificações)

```env
TELEGRAM_BOT_TOKEN=seu-token
TELEGRAM_CHAT_ID=seu-chat-id
```

Obtenha o token no BotFather (@BotFather no Telegram), e o chat ID enviando uma mensagem pro seu bot e acessando `https://api.telegram.org/bot{TOKEN}/getUpdates`.

### SLA (opcional)

```env
# Não há variáveis de env adicionais para SLA; config fica em sla_config.yaml
```

## Verificação da Instalação

### 1. Teste de importações

```bash
python -c "import psycopg2; import pyodbc; import oracledb; print('OK')"
```

### 2. Teste de conexão

```bash
python scripts/check_telegram.py
# Deve enviar uma mensagem de teste para seu chat
```

### 3. Teste de ETL simples

```bash
# Execute uma tabela pequena
python run.py load full --table cliente --truncate

# Confira os logs
cat logs/2026/04/20260428.log
```

## Troubleshooting

### Erro: "ODBC driver not found"

```
pyodbc.OperationalError: ('01000', "[01000] [unixODBC][Driver Manager]Can't open lib 'ODBC Driver 18 for SQL Server'"...
```

**Solução**: instale o driver ODBC 18 ou configure `Driver='{ODBC Driver 17 for SQL Server}'` no código.

### Erro: "Connection refused" no Oracle

**Solução**: 
- Verifique Oracle Instant Client no PATH
- Teste: `sqlplus usuario/senha@SERVICE_NAME`

### Erro: "authentication failed" no PostgreSQL

**Solução**:
- Confirme credenciais no `.env`
- Teste: `psql -h host -U usuario -d database`

## Próximo Passo

Leia [Como Usar](usage.md) para aprender a executar o pipeline.
