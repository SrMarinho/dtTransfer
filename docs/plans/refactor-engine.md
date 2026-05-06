# Plano: Refatoração para Framework / Engine ETL

## Context

O projeto `DataReplicator` evoluiu de uma ferramenta ETL pontual (3 sistemas hardcoded: biMktNaz, biSenior, biNazaria) para uma engine declarativa baseada em workspaces YAML. O esqueleto de framework já existe (`src/workspace/`, `WorkspaceLoader`, `WorkspaceRegistry`, `YamlTable`, factories), mas convive com:

- 213 entidades Python legadas registradas manualmente em `EntityRegistry._entities` (dict gigante de imports)
- DDL inline em `createTable()` espalhado por 152+ arquivos em `src/systems/pbs/entities/`
- 2 caminhos de resolução de DB (enum `Database` legacy vs tupla `(workspace_id, ref)`)
- `_SYSTEM_MAP` hardcoded em `src/core/table.py` mapeando enum → pasta de SQLs
- `Table.insert()` com lógica específica de driver (psycopg2 `copy_from` vs `executemany`) misturada na entidade
- Docs orientados ao **uso**, sem guia de **desenvolvedor/extensão**

### Objetivo

Tornar o projeto um framework instalável tipo Django/Vue: o desenvolvedor clona, define seus workspaces YAML em `config/workspaces/<id>/` e roda. Núcleo (`src/`) intocável, extensão por configuração.

### Restrição crítica

**Entidades legadas (`biMktNaz`, `biSenior`, `biNazaria` em `src/systems/{pbs,senior}/`) DEVEM continuar funcionando** até o usuário concluir homologação. Refatoração é aditiva e isola o legacy atrás de um shim, sem deletar.

---

## Estratégia: 5 fases incrementais

Cada fase entrega valor isolado. Fase 5 (remoção do legacy) só roda após homologação manual do usuário — não incluída neste plano.

### Fase 1 — `src/engine/` como API pública (facade)

Em vez de mover fisicamente 30+ arquivos (alto risco para 213 arquivos legacy), cria-se `src/engine/` como **fachada de API pública**. Re-exporta o que o desenvolvedor de novos workspaces precisa. Lógica interna fica nos paths atuais.

**Estrutura:**
```
src/engine/
  __init__.py            # API pública: Entity, Process, Workspace, Driver, bootstrap, register_driver, register_process
  entity.py              # re-exporta Table como Entity (Table = Entity é alias)
  workspace.py           # re-exporta Workspace, ConnectionRef, EntitySpec, YamlTable
  process.py             # re-exporta Process e tipos (FullQuery, Incremental, Monthly, Unit)
  driver.py              # re-exporta Driver base + register_driver
  bootstrap.py           # re-exporta bootstrap()
  cli.py                 # helpers para extender CLI (futuro)
```

**Por quê facade e não move físico:**
- 213 arquivos legacy importam `from src.core.entity import Table` e `from src.factories.database_factory import Database`. Move físico exige shims em todo path antigo + atualização de imports internos cruzados — risco de circular imports.
- Facade dá ao framework uma API pública limpa **agora** sem tocar legacy.
- Fase 5 (futura, pós-homologação) faz move físico real e remove os módulos antigos. Aí o `src/engine/` deixa de ser facade e vira o lugar canônico.

**Convenção pública (documentada para devs):**
> Sempre importe de `src.engine.*` em código novo. Paths antigos (`src.core.table`, `src.factories.*`) são internos/legacy.

**Manter onde está:** todo o `src/`, exceto a nova pasta `src/engine/`.

**Arquivos críticos:**
- `src/core/table.py:1-152`
- `src/factories/entity_registry.py:1-261`
- `src/factories/database_factory.py:1-69`
- `src/workspace/bootstrap.py:1-32`

### Fase 2 — Extensibilidade & limpeza de smells

**a) Driver registry plugável**
Substituir o dict hardcoded em `DatabaseDriverFactory.getInstance` (linhas 10-15) por registry com `register_driver(name, cls)`. Permite adicionar driver custom sem editar o factory. Driver base abstract com `connection()`, `bulk_insert(table, columns, rows)`, `truncate(table)` em `src/engine/drivers/base.py`.

**b) Mover `bulk_insert` para o driver**
Tirar `Table.insert()` (`src/core/table.py:57-113`) — toda a lógica de `copy_from` / `executemany` / escape — e colocar em cada driver:
- `PostgresDB.bulk_insert()` usa `copy_from`
- `SqliteDB.bulk_insert()` / `SqlserverDB.bulk_insert()` / `OracleDB.bulk_insert()` usam `executemany`
- `Entity.insert(rows)` vira: `self.toDriver.bulk_insert(self.name, self.columns, rows)`

Resolve duplicação e o `hasattr(cursor, 'copy_from')` frágil.

**c) Process registry plugável**
Espelhar driver registry: `ProcessFactory.register("custom", MyProcess)`. Permite o desenvolvedor criar tipos de processo novos sem editar o core.

**d) Remover `_SYSTEM_MAP` hardcoded**
`src/core/table.py:7-14` é dead code para `YamlTable` (que já tem `query_path` próprio em `yaml_entity.py:68`). Manter só no shim de Entity legacy. YamlTable ignora.

**e) Eliminar `register_python_workspace` no-op**
`entity_registry.py:251-261` — método placeholder vazio. Remover ou implementar de verdade (hook que chama `module.register(factory)` se existir).

**f) Detectar entidades duplicadas no carregamento**
`EntityRegistry.register_yaml_workspace` deve falhar se a key já existe em `_entities` ou `_workspace_entities`. Hoje sobrescreve silenciosamente.

### Fase 2.5 — CLI restructure (subcommand groups)

CLI atual tem redundância: `python run.py list-workspaces list-workspaces` (causa: `add_typer` + sub-`@app.command()` no mesmo nome). Reorganizar estilo `kubectl` / `django-admin`:

```
python run.py workspace list                   # ex list-workspaces
python run.py workspace validate               # ex validate-config
python run.py workspace new <id>               # NOVO (Fase 3 scaffold)
python run.py entity list [-w id]              # ex list-tables
python run.py entity new <ws>/<name>           # NOVO (Fase 3)
python run.py migrate upgrade -w id            # já existe
python run.py migrate status|validate|create -w id
python run.py load full|incremental|monthly|unit -t ws/entity
python run.py logs errors [--since 10:00]      # ex check-errors
```

Implementação:
- `src/interfaces/cli/groups/workspace.py` — Typer com `list`, `validate`, `new`
- `src/interfaces/cli/groups/entity.py` — `list`, `new`
- `src/interfaces/cli/groups/logs.py` — `errors`
- `migrate` e `load` já são grupos; manter
- `run.py` registra grupos limpos

**Aliases retrocompat** (1 release de aviso, depois deletar):
- `list-workspaces` → deprecation warning + chama `workspace list`
- `list-tables` → `entity list`
- `validate-config` → `workspace validate`
- `check-errors` → `logs errors`

### Fase 3 — Scaffolding CLI

Comandos `workspace new` / `entity new` (já adicionados ao grupo na Fase 2.5):

```bash
python run.py workspace new <id>             # cria config/workspaces/<id>/{workspace.yml, entities/, sqls/, migrations/}
python run.py entity new <workspace>/<name>  # cria entities/<name>.yml + sqls/consulta_<name>.sql template
```

Templates em `src/engine/templates/` (workspace.yml.tmpl, entity.yml.tmpl, sql.tmpl).

Convenções documentadas e reforçadas:
- `target_table` no YAML = nome físico em `target.driver`
- `columns:` lista plana (autoridade de schema = Alembic, não YAML)
- `sql_file:` resolvido relativo a `<workspace>/sqls/`
- Nomes de entidade `snake_case`, ids de workspace `camelCase` ou `kebab-case`
- Toda DDL via Alembic (`migrations/versions/*.py`), nunca em código

### Fase 4 — Documentação (split usuário vs desenvolvedor)

Reorganizar `docs/`:

```
docs/
  user/                       # COMO USAR (operador ETL)
    installation.md           # mover existente
    quickstart.md             # NOVO: 5min, criar workspace + 1 entidade + rodar
    cli.md                    # NOVO: referência completa de cada comando
    workspaces.md             # mover, focar em como configurar
    migrations.md             # mover
    deployment.md             # mover
    monitoring.md             # mover
    troubleshooting.md        # NOVO: erros comuns, .env, drivers
  dev/                        # COMO ESTENDER (desenvolvedor)
    architecture.md           # reescrever: engine, fluxo, extensão
    creating-workspaces.md    # NOVO: passo-a-passo workspace YAML do zero
    creating-entities.md      # NOVO: spec, SQL, columns, process_type
    custom-drivers.md         # NOVO: como registrar driver novo
    custom-processes.md       # NOVO: subclasse Process, registrar
    testing.md                # NOVO: como testar workspace local com SQLite
    contributing.md           # NOVO: estrutura do repo, convenções, PRs
  reference/                  # API
    entity.md                 # API de Entity (ex-Table)
    process.md                # API de Process
    driver.md                 # API de Driver
    workspace-yaml.md         # schema completo de workspace.yml e entity.yml
  legacy/                     # DEPRECATED (avisar que será removido)
    legacy-systems.md         # como o legacy biMktNaz/biSenior/biNazaria funciona
```

Atualizar `README.md` raiz: 1 quickstart de 30s + links para `docs/user/` e `docs/dev/`.

`AGENTS.md` simplificado: aponta para `docs/dev/architecture.md` ao invés de duplicar.

### Fase 5 — (FUTURO, NÃO EXECUTAR AGORA)

Após homologação do usuário em ambiente de testes:
- Migrar entidades de `src/systems/pbs/` e `src/systems/senior/` para workspaces YAML em `config/workspaces/{biMktNaz,biSenior,biNazaria}/entities/*.yml`
- Apagar `src/systems/`
- Apagar shims de compat de Fase 1
- Apagar enum `Database` e `_LEGACY_CLASSES` em `database_factory.py`
- Apagar `src/core/databases/{biMktNaz,biSenior,biNazaria,Senior,PBS_NAZARIA_DADOS,newBiMktNaz}.py`

---

## Arquivos críticos a modificar (Fases 1-4)

| Arquivo | Mudança |
|---------|---------|
| `src/core/table.py` | Vira shim → `src/engine/entity.py` |
| `src/factories/entity_registry.py` | Vira shim, lógica em `src/engine/factories/entity_registry.py`; adiciona detecção de duplicata; remove `register_python_workspace` no-op |
| `src/factories/database_driver_factory.py` | Vira `register_driver()` API |
| `src/factories/database_factory.py` | Vira shim, `_LEGACY_CLASSES` movido para `src/engine/factories/_legacy_compat.py` (isolado) |
| `src/factories/process_factory.py` | Adiciona `register()` |
| `src/workspace/*` | Movido para `src/engine/workspace/*` (5 arquivos) |
| `src/processes/*` | Movido para `src/engine/processes/*` |
| `src/core/databases/connections/*` | Movido para `src/engine/drivers/*`; cada driver ganha `bulk_insert()` |
| `src/core/logger/*` | Movido para `src/engine/logging/*` |
| `src/interfaces/cli/commands/scaffold.py` | NOVO — comando `new` |
| `src/engine/templates/*` | NOVOS — templates de scaffold |
| `docs/**` | Reorganização completa: user/ dev/ reference/ legacy/ |
| `README.md` | Reescrita curta, aponta para docs |
| `AGENTS.md` | Simplificar |

## Arquivos a NÃO tocar (legacy intacto)

- `src/systems/pbs/entities/*.py` (152 arquivos)
- `src/systems/senior/entities/*.py` (61 arquivos)
- `src/systems/{pbs,senior}/sqls/**`
- `src/core/databases/{biMktNaz,biSenior,biNazaria,Senior,PBS_NAZARIA_DADOS,newBiMktNaz}.py`
- `src/core/databases/fake_database.py`
- `src/core/databases/generic.py`

Os shims de Fase 1 garantem que esses arquivos continuam importando dos paths antigos.

## Reuso explícito

- `WorkspaceLoader` (`src/workspace/loader.py:22`) — já faz o que framework precisa, só muda de path
- `WorkspaceRegistry` (`src/workspace/registry.py`) — singleton thread-safe, manter
- `EntitySpec` Pydantic (`src/workspace/yaml_entity.py:20`) — schema correto, manter
- `bootstrap()` (`src/workspace/bootstrap.py:14`) — idempotente, manter
- `run_alembic` (`src/workspace/migrations.py`) — manter

Não criar novas abstrações onde já existe.

---

## Verificação (testes ponta-a-ponta)

Após cada fase rodar:

```bash
# Suite unit + bdd não-DB
pytest -m "not integration and not e2e" -q

# Workspace YAML local (SQLite, exemplo já existe)
python run.py list-workspaces
python run.py list-tables --workspace example
python run.py migrate upgrade --workspace example
python run.py load full --table example/produto

# Legacy ainda funciona
python run.py list-tables --workspace biSenior
python run.py validate-config

# Fase 3 scaffold
python run.py new workspace teste123
ls config/workspaces/teste123/   # deve ter workspace.yml, entities/, sqls/, migrations/
python run.py new entity teste123/foo
python run.py list-tables --workspace teste123

# Fase 4 docs
ls docs/user docs/dev docs/reference docs/legacy   # estrutura existe
```

Critério de aceite por fase:
- **Fase 1**: imports antigos seguem funcionando (`from src.core.entity import Table`, `from src.factories.database_factory import Database`); todos os testes passam; nada em `src/systems/` foi tocado
- **Fase 2**: drivers reconhecem `bulk_insert()`; `register_driver("foo", FakeDriver)` funciona; teste novo cobre isso
- **Fase 3**: comando `new` cria estrutura válida; entidade gerada aparece em `list-tables`
- **Fase 4**: links em README resolvem; cada arquivo em `docs/dev/` tem exemplo executável

---

## Ordem de execução sugerida

1. Fase 1 inteira em PR único (move + shims) — mecânico, baixo risco
2. Fase 2 dividida: 2a-2b (drivers) → 2c (processos) → 2d-2f (limpeza) — cada um testável isolado
3. Fase 3 — scaffold + templates
4. Fase 4 — docs (pode rodar paralelo a 3)
5. Fase 5 — congelada até homologação manual

Sem commits ao longo do trabalho até o usuário pedir explicitamente.

