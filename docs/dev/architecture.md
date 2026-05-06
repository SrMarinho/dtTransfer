# Arquitetura Modular

## Estrutura de Diretórios

```
/
├── run.py                              # Ponto de entrada CLI
├── pyproject.toml                      # Config do pacote Python
├── pytest.ini                          # Config de testes
├── requirements.txt                    # Dependências
├── .env / .env.example                 # Credenciais
├── .vscode/settings.json               # YAML schemas (autocomplete)
│
├── orchestration/                      # ★ NOVO: Orquestração Dagster
│   ├── __init__.py
│   ├── definitions.py                  # Entry point Definitions
│   ├── _runner.py                      # Subprocess → run.py CLI
│   ├── _config.py                      # TABLE_PARAMS, VARIANTS, AC_TABLES
│   ├── _assets.py                      # 189 assets dinâmicos do EntityRegistry
│   ├── _schedules.py                   # 27 schedules traduzidos do crontab
│   └── _sensors.py                     # Health check
│
├── schemas/                            # ★ NOVO: JSON Schemas para YAMLs
│   ├── workspace.json                  # Valida workspace.yml
│   └── entity.json                     # Valida entities/*.yml
│
├── dagster.yaml                        # Config Dagster (concorrência, retenção)
├── workspace.yaml                       # Dagster workspace file
│
├── src/
│   ├── core/                           # Infraestrutura compartilhada (legacy)
│   │   ├── entity.py                   # Classe base Entity + filter_columns()
│   │   ├── databases/                  # Conexões com bancos de dados
│   │   │   ├── connections/            # Drivers: Postgres, SQL Server, Oracle
│   │   │   ├── generic.py              # GenericDatabase (driver-agnóstico)
│   │   │   ├── fake_database.py        # Stub para testes
│   │   │   └── {biMktNaz,biSenior,...}.py
│   │   └── logger/                     # Logging (standard, Telegram, run_context)
│   │
│   ├── engine/                         # API pública + engine moderna
│   │   ├── __init__.py                 # Facade lazy: Entity, Workspace, Process
│   │   ├── entity.py / workspace.py / process.py / driver.py / registry.py
│   │   ├── bootstrap.py
│   │   ├── scaffold.py                 # workspace new / entity new
│   │   ├── drivers/                    # postgres, sqlserver, oracle, sqlite, fake
│   │   ├── processes/                  # full_query, incremental, monthly, unit
│   │   └── workspace/                  # Loader, registry, migrations, yaml_entity
│   │       ├── bootstrap.py / loader.py / registry.py
│   │       ├── workspace.py            # Modelos: Workspace, ConnectionRef
│   │       └── yaml_entity.py          # EntitySpec, YamlTable
│   │
│   ├── factories/                      # Fábricas (transição legacy → engine)
│   │   ├── database_factory.py
│   │   ├── entity_registry.py          # Pbs.Classe / Senior.Classe (sem colisão)
│   │   └── process_factory.py
│   │
│   ├── interfaces/                     # CLI + Bot Telegram
│   │   ├── cli/                        # Typer CLI
│   │   │   ├── groups/{workspace,entity,logs}.py
│   │   │   └── commands/{load,migrate}.py
│   │   └── bot/                        # Telegram (auth, jobs, poll, runner)
│   │
│   ├── systems/                        # Entidades LEGACY
│   │   ├── pbs/entities/ + sqls/       # ~152 entidades (fonte SQL Server)
│   │   └── senior/entities/ + sqls/    # ~61 entidades (fonte Oracle)
│   │
│   ├── workspaces/                     # Definições de workspace
│   │   ├── biMktNaz/ (Python adapter)
│   │   ├── biSenior/ (Python adapter)
│   │   ├── biNazaria/ (Python adapter)
│   │   ├── example/ (YAML + SQLite)
│   │   └── local1/ (YAML + Postgres dev)
│   │
│   └── processes/                      # Deprecated (usar src.engine.processes)
│
├── docs/                               # Documentação
├── logs/                               # Logs rotacionados
└── tests/                              # Testes
    ├── unit/
    ├── integration/
    ├── e2e/
    └── bot/
```

## Fluxo de Execução — CLI (legado)

```
run.py load full --table cliente
  └─ load.py → ModeFactory → ProcessFactory → EntityRegistry
       └─ Entity.getQuery() → SQL file
       └─ fromDriver (origem) → fetch
       └─ filter_columns(table.columns, rows, cursor.description)
       └─ toDriver (destino) → bulk_insert
```

## Fluxo de Execução — Dagster (novo)

```
dagster asset materialize --select cliente
  └─ orchestration/definitions.py
       └─ _assets.py → build_all_assets()
            └─ EntityRegistry.valid_tables() → 189 assets
            └─ TABLE_PARAMS (process, days, threads, etc.)
            └─ _runner.run_etl(context, table, **params)
                 └─ subprocess: run.py load full --table cliente --truncate
                      └─ (mesmo fluxo legado acima)
```

## filter_columns

`columns` no YAML vira filtro + ordenação opcional:

```yaml
# Entity retorna 5 colunas, mas só quero 2 na ordem que escolher
columns:
  - nome_fantasia
  - codigo_cliente
```

Se omitido, usa todas colunas do `cursor.description`. Implementado como função standalone `src.core.entity.filter_columns()` e chamada nos 4 processos (FullQuery, Incremental, Monthly, Unit).

## Mapeamento de Entidades

`EntityRegistry._entities` usa namespace explícito `Pbs.` / `Senior.`:

```
'cliente'                   → Pbs.Cliente (SQL Server)
'acompanhamento_solicitacoes_compras' → Senior.AcompanhamentoSolicitacoesCompras (Oracle)
'biSenior/titulos_receber' → Senior.TitulosReceber
'biMktNaz/nota_fiscal'     → Pbs.NotaFiscal
'biNazaria/produtos'       → Pbs.Produtos
```

Não há colisão de nomes entre os dois sistemas.

## Resolução de SQL

`Entity.getQuery()` resolve o caminho do SQL baseado no `fromDB` via `_SYSTEM_MAP`:

| fromDB          | Pasta    | Caminho do SQL                              |
|-----------------|----------|---------------------------------------------|
| PBSNAZARIADADOS | `pbs`    | src/systems/pbs/sqls/consulta_{name}.sql    |
| SENIOR          | `senior` | src/systems/senior/sqls/consulta_{name}.sql |

## Workspace.enabled

Workspace pode ser desligado sem remover:

```yaml
# src/workspaces/local1/workspace.yml
enabled: false   # loader ignora, migrate não acha, entities não registram
```

Default `true`. Omissão = ativado.

## Convenções

- **Imports**: Caminho absoluto a partir de `src.` (ex: `from src.core.entity import Entity`)
- **Entidades**: Herdam de `Entity`, definem `fromDB`, `toDB`, `name`, `columns`
- **Processos**: Herdam de `Process`, implementam `run()`
- **Testes**: `unit/` isolados, `integration/` com banco real, `e2e/` pipeline completo
- **Schema YAML**: Todo `.yml` novo deve ter `$schema` apontando para `schemas/*.json`
