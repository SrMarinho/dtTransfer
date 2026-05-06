# Plano: Engine genérico + Workspaces (multi-bundle)

## Contexto

Hoje `biMktNaz` é um ETL acoplado a 3 bundles hardcoded da mesma empresa: `biSenior` (Senior/Oracle → Postgres), `biMktNaz` (PBS/SQLServer → Postgres), `biNazaria` (PBS/SQLServer → Postgres). 213 entidades Python com `fromDB`/`toDB` fixos via enum, `.env` com prefixos por bundle, CLI assume bundle único. Não dá pra terceiros usarem app sem forkar e mexer no código.

Objetivo: transformar app em **engine genérico** (a "casca") + **workspaces** (a "essência"). Workspace = pacote declarativo com sources, target, entidades, SQLs e migrations. Engine não conhece nenhum workspace específico — descobre em runtime. Os 3 legados continuam funcionando intactos via adapter, removíveis a qualquer momento.

Decisão sobre Omniquery: **não mesclar**. Worldviews diferentes (Omniquery = replace-all stateless sem migrations; biMktNaz = incremental + alembic + retry). Manter separado. Inspirar-se na sintaxe YAML declarativa só.

## Decisões

- **Modelo de entidade**: híbrido. Legados ficam Python (adapter), novos workspaces em YAML. Caminho legado removível depois.
- **Localização de workspaces**: ambos. Built-in em `config/workspaces/` (legados) + externo via `WORKSPACES_DIR` (novos, sem rebuild Docker). Engine mescla os dois com built-in tendo precedência em caso de conflito de id.
- **Migrations**: manual via CLI por workspace. App valida alembic head no startup, falha se desatualizado. Sem auto-upgrade.
- **Escopo PR1**: engine + adapter legado + loader YAML + 1 workspace exemplo fictício pra provar design. Conversão dos legados pra YAML em PRs futuros.

## Abordagem

### 1. Núcleo: Workspace abstraction

Novo módulo `src/workspace/`:

- `workspace.py` — classe `Workspace` (id, sources, target, entities, migrations_dir, sql_dir). Pydantic.
- `loader.py` — `WorkspaceLoader` descobre workspaces: lê `config/workspaces/` (built-in) e `$WORKSPACES_DIR` (externo). Suporta dois tipos:
  - **Python workspace** (legado): pasta com `__init__.py` que registra Tables via API do engine.
  - **YAML workspace** (novo): pasta com `workspace.yml` + `entities/*.yml` + `sqls/*.sql` + `migrations/`.
- `registry.py` — `WorkspaceRegistry` singleton, expõe `get(id) -> Workspace`, `list() -> list[Workspace]`.

### 2. Database registry runtime

Substituir `Database` enum (`src/factories/database_factory.py`) por registry dinâmico:

- Cada workspace declara suas conexões em `workspace.yml` (source + target). Engine instancia drivers (Postgres/SQLServer/Oracle) por nome lógico do workspace.
- Credenciais continuam em env. Workspace YAML referencia chaves: `target.dsn_env: DB_BIMKTNAZ_POSTGRES_*`. Sem prefixo hardcoded no código.
- `DatabaseFactory.getInstance(workspace_id, ref)` substitui `Database.BIMKTNAZ`.

### 3. Entity loader YAML

Novo `src/workspace/yaml_entity.py`:

- `entities/<name>.yml` define: `name`, `target_table`, `source_ref`, `target_ref`, `columns: [{name, type, nullable}]`, `sql_file`, `process_type` (full/incremental/monthly/unit), `incremental_column`.
- `YamlTable(Table)` — subclasse de `Table` que lê YAML e popula `__init__` dinamicamente. Reutiliza `createTable()`, `truncate()`, `insert()` existentes.
- `EntityRegistry` ganha método `register_yaml_workspace(workspace)` que cria YamlTable instances e registra em `_entities` com chave `<workspace_id>/<entity_name>`.

### 4. Adapter legado

Empacota cada legado como workspace built-in **sem reescrever as 213 entidades**:

- `config/workspaces/biSenior/__init__.py` — função `register(engine)` chama código existente que registra entidades em `EntityRegistry`.
- Mesmo pra biMktNaz e biNazaria.
- Código atual em `src/systems/{pbs,senior}/` permanece. Apenas é importado pelo workspace built-in correspondente.
- Remover legado depois = deletar pasta `config/workspaces/<id>/` + `src/systems/<system>/`.

### 5. CLI

`run.py`:

- Novo flag global `--workspace <id>` em todos comandos (`load`, `list-tables`, `validate-config`, `migrate`).
- Sem `--workspace` quando há mais de 1 workspace registrado: erro pedindo flag. Com 1 só: usa default.
- Comando novo `list-workspaces`.
- `migrate` aceita `--workspace <id>` e roda alembic upgrade/downgrade no diretório de migrations daquele workspace.

### 6. Alembic multi-workspace

`alembic.ini` hoje tem `[biMktNaz]` e `[biSenior]` hardcoded. Substituir por config dinâmico:

- `src/migrations/env.py` lê `WORKSPACE_ID` do env, resolve via `WorkspaceRegistry`, configura `script_location` e `sqlalchemy.url` do workspace.
- CLI `python run.py migrate --workspace biSenior upgrade head` exporta env e chama alembic.
- Cada workspace tem própria pasta `migrations/versions/` com sua linha de versionamento.
- Startup do app: validar head atual = head do diretório. Se diferente, `sys.exit(1)` com mensagem clara.

### 7. Workspace exemplo

`config/workspaces/example/`:

- `workspace.yml` com 1 source (Postgres dummy) + 1 target (Postgres dummy) + envs fictícios.
- `entities/sample.yml` com 3 colunas.
- `sqls/sample.sql` com `SELECT * FROM sample`.
- `migrations/versions/0001_initial.py` Alembic stub.
- README curto explicando como usar de template.

## Arquivos críticos a modificar

- `src/factories/database_factory.py` — enum → registry runtime.
- `src/factories/entity_registry.py` — registro estático → namespace por workspace.
- `src/factories/process_factory.py` — receber workspace_id + entity ref.
- `src/core/databases/{biMktNaz,biSenior,senior,nazaria}.py` — refatorar pra ler creds via ref do workspace.
- `src/migrations/env.py` — resolver workspace dinâmico.
- `alembic.ini` — limpar, mover config pra workspace.
- `run.py` — flag `--workspace`, comando `list-workspaces`.
- `src/interfaces/cli/commands/*.py` — propagar workspace_id.
- `.env.example` — reorganizar por workspace, deixar claro que vars ficam fora do código.

## Arquivos novos

- `src/workspace/workspace.py`, `loader.py`, `registry.py`, `yaml_entity.py`
- `config/workspaces/biSenior/__init__.py` (adapter)
- `config/workspaces/biMktNaz/__init__.py` (adapter)
- `config/workspaces/biNazaria/__init__.py` (adapter)
- `config/workspaces/example/` (workspace YAML exemplo completo)
- `docs/workspaces.md` — guia de criação de workspace novo
- `tests/unit/workspace/test_loader.py`, `test_registry.py`, `test_yaml_entity.py`
- `tests/integration/test_workspace_isolation.py` — garante que workspace A não vaza Tables pra workspace B

## Verificação end-to-end

1. **Legado intacto**: `python run.py load --workspace biSenior titulos_receber` roda igual a antes (mesma SQL, mesmo target). Comparar rowcount com baseline pré-refactor.
2. **Workspace YAML exemplo**: `python run.py load --workspace example sample` carrega 1 entidade YAML do zero contra Postgres local. Verificar DDL gerada bate com YAML.
3. **Descoberta externa**: setar `WORKSPACES_DIR=/tmp/ws`, criar workspace YAML lá, `python run.py list-workspaces` deve listá-lo junto dos built-in.
4. **Migrations**: `python run.py migrate --workspace example upgrade head` aplica migration. Subir app sem ter rodado upgrade → sair com erro de head desatualizado.
5. **Suite de testes**: `pytest tests/unit/workspace/ tests/integration/test_workspace_isolation.py tests/e2e/` tudo verde.
6. **Remoção limpa do legado** (teste manual): apagar `config/workspaces/biNazaria/` + `src/systems/pbs/entities/nazaria/*` (se isolado) → `list-workspaces` não mostra biNazaria, outros 2 continuam funcionando.

## Fora de escopo (PRs futuros)

- Converter os 3 legados pra YAML.
- Autogenerate de migration a partir de diff do YAML.
- Plugin entrypoints (workspace via pacote pip).
- UI/dashboard de workspaces.
- Importar Omniquery como loader opcional.

