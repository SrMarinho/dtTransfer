# Contribuir

## Estrutura do repositório

```
src/
  engine/                   # API pública (use isso em código novo)
    __init__.py             # facade lazy: Entity, Workspace, Process, Driver, register_*, bootstrap
    entity.py               # re-export de Entity + alias Table
    workspace.py            # Workspace, ConnectionRef, EntitySpec, YamlTable
    process.py              # Process, FullQuery, Incremental, Monthly, Unit
    driver.py               # Driver base + register_driver/get_driver
    registry.py             # register_process
    bootstrap.py            # bootstrap()
    scaffold.py             # workspace new / entity new
  engine/workspace/         # impl interna (loader, registry, bootstrap, migrations, yaml_entity)
  factories/                # impl interna (queryable, database, process, driver, mode, logger factories)
  processes/                # impl: FullQuery, Incremental, Monthly, Unit, retry, params
  core/
    entity.py               # classe base Entity
    databases/connections/  # drivers built-in
    databases/{biMktNaz,biSenior,...}.py  # legacy DB wrappers
    logger/                 # logging, telegram, error parser
  systems/                  # ENTIDADES PYTHON LEGACY (não tocar)
    pbs/entities/           # 152 entidades
    senior/entities/        # 61 entidades
  interfaces/
    cli/
      groups/               # workspace, entity, logs (subcommand groups novos)
      commands/             # load, migrate (já estruturados); aliases legacy
    bot/                    # Telegram
  workspaces/               # workspaces YAML + Python built-in (em git)
  scripts/                  # utilitários
docs/                       # esta pasta
tests/
```

## Convenção de imports

- **Código de framework**: `from src.engine import ...`
- **Código legacy** (`src/systems/`): mantém `from src.core.entity import Entity`, `from src.factories.database_factory import Database`
- Não criar imports cruzados entre `src/engine/*` e `src/systems/*` (engine é base, systems é cliente)

## Convenção de commits

Conventional Commits — exemplo:

```
feat(workspace): add scaffold command for entity creation
fix(driver): postgres bulk_insert handles empty buffer
refactor(cli): split monolithic commands into subcommand groups
docs(dev): add custom-drivers guide
```

Tipos válidos: `feat`, `fix`, `refactor`, `test`, `chore`, `docs`, `style`, `perf`, `ci`, `build`, `revert`.

## Workflow

1. Branch a partir de `main`: `git checkout -b feat/<descrição>`
2. Edite, rode testes: `pytest -m "not integration and not e2e"`
3. Commit pequenos com mensagens claras
4. Não tocar em `src/systems/` (legacy)
5. PR descreve **o quê** e **por quê** (não o como — diff fala)

## Não fazer

- Adicionar campos novos em `EntitySpec` sem migrar specs existentes
- Hardcodar driver/process novo no factory — use `register_driver` / `register_process`
- Inline DDL em `Entity.createTable()` — use Alembic
- Comentários explicando o quê — código bem nomeado fala por si

## Roadmap

Ver [docs/plans/refactor-engine.md](../plans/refactor-engine.md) e [docs/plans/roadmap.md](../plans/roadmap.md).

