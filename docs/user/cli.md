# Como Usar

## Formato geral

```bash
python run.py <comando> [subcomando] [opções]
```

---

## Comandos disponíveis

### `load` — Executa carga ETL

```bash
# Carga completa (truncate + insert)
python run.py load full --table cliente --truncate

# Incremental por dias (multithread)
python run.py load incremental --table venda --days 10 --threads 10

# Incremental com current-day
python run.py load incremental --table venda --days 1 --current-day

# Incremental full load (sem loop de datas)
python run.py load incremental --table venda --full --truncate

# Mensal
python run.py load monthly --table titulos_contas_receber --months 13

# Mensal — intervalo único
python run.py load monthly --table balancete_contabil --months 6 --method wholeInterval

# Por unidade/CD
python run.py load unit --table estoque --unit 2
```

### `workspace` — Gerencia workspaces

```bash
python run.py workspace list                  # listar todos
python run.py workspace validate              # testar conexoes
python run.py workspace new local2            # criar novo workspace YAML
```

### `entity` — Gerencia entidades

```bash
python run.py entity list                     # todas (193)
python run.py entity list -w biSenior         # filtrar por workspace
```

### `migrate` — Migrations Alembic

```bash
python run.py migrate status -w biMktNaz
python run.py migrate upgrade -w biMktNaz
python run.py migrate create -w biMktNaz --autogenerate -m "add coluna cpf"
python run.py migrate rollback -w biMktNaz --steps 1
```

### `logs` — Inspeciona logs

```bash
python run.py logs errors                     # erros de hoje
python run.py logs errors --since 10:00 --until 16:00
python run.py logs errors --detailed
```

---

## Dagster Orchestration

```bash
# Validar definitions
dagster definitions validate -f orchestration/definitions.py

# Listar assets (189)
dagster asset list -f orchestration/definitions.py

# Materializar 1 asset
dagster asset materialize --select cliente -f orchestration/definitions.py

# Schedules
dagster schedule list -f orchestration/definitions.py
dagster schedule start job_5h_schedule -f orchestration/definitions.py

# UI / Daemon
dagster-webserver -w workspace.yaml -p 3000
dagster-daemon run -w workspace.yaml
```

---

## Referência de parâmetros

### `load full`

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--table` / `-t` | *obrigatório* | Nome da entidade |
| `--truncate` | `False` | Trunca destino antes de inserir |

### `load incremental`

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--table` / `-t` | *obrigatório* | Nome da entidade |
| `--days` / `-d` | *obrigatório¹* | Dias atrás a sincronizar |
| `--threads` | `4` | Threads paralelas (1–50) |
| `--truncate` | `False` | Trunca destino antes de processar |
| `--current-day` | `False` | Inclui o dia atual |
| `--full` | `False` | Full load sem filtro de data |

> ¹ Dispensável quando `--full` é usado.

### `load monthly`

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--table` / `-t` | *obrigatório* | Nome da entidade |
| `--months` / `-m` | *obrigatório¹* | Meses atrás a sincronizar |
| `--method` | `byMonth` | `byMonth` ou `wholeInterval` |
| `--truncate` | `False` | Trunca destino antes de processar |
| `--full` | `False` | Full load sem filtro de data |

> ¹ Dispensável quando `--full` é usado.

### `load unit`

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--table` / `-t` | *obrigatório* | Nome da entidade |
| `--unit` / `-u` | *obrigatório* | ID da unidade/CD |
