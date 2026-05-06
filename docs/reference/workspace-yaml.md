# Schema: workspace.yml e entity.yml

## `workspace.yml`

```yaml
id: <slug>                # obrigatório. Letra inicial, [A-Za-z0-9_-]
kind: yaml                # obrigatório. 'yaml' (ou 'python' para legacy)

target:                   # obrigatório
  name: <ref_name>        # opcional, mas recomendado
  driver: postgres        # obrigatório. {postgres, sqlserver, oracle, sqlite, fake}
  env_prefix: <PREFIX>    # obrigatório. Vars: <PREFIX>_HOST, _PORT, _DATABASE, _USERNAME, _PASSWORD
  options: {}             # opcional, dict livre

sources:                  # opcional, lista
  - name: <ref_name>
    driver: <kind>
    env_prefix: <PREFIX>
    options: {}
```

**Resolução de paths** (default, sobrescrevíveis):
- `entities_dir` → `<root>/entities`
- `sql_dir` → `<root>/sqls`
- `migrations_dir` → `<root>/migrations`

## `entities/<name>.yml`

```yaml
name: <slug>                 # obrigatório. snake_case
target_table: <table>        # obrigatório. nome físico no target
source: <ref_name>           # obrigatório. tem que existir em workspace.sources
target: <ref_name>           # obrigatório. tem que ser workspace.target.name
process_type: full           # obrigatório. {full, incremental, monthly, unit}
sql_file: <file>             # obrigatório. relativo a sql_dir
incremental_column: <col>    # opcional. só usado por incremental
columns:                     # opcional, lista plana
  - <col1>
  - <col2>
```

**Validação**: `extra: forbid` (Pydantic). Campos desconhecidos → `EntityLoadError`.

## Env vars por driver

| Driver | Vars obrigatórias | Opcionais |
|--------|-------------------|-----------|
| postgres | `_HOST`, `_PORT`, `_DATABASE`, `_USERNAME`, `_PASSWORD` | — |
| sqlserver | idem | — |
| oracle | `_HOST`, `_PORT`, `_USERNAME`, `_PASSWORD`, `_DATABASE` ou `_SERVICE_NAME` | `_ENCODING` |
| sqlite | `_DATABASE` (caminho do arquivo) | — |
| fake | — | — (in-memory, só testes) |

## Errors

| Erro | Causa |
|------|-------|
| `unknown driver 'X'` | `driver:` fora da lista permitida |
| `id must start with a letter...` | id do workspace inválido |
| `process_type must be one of [...]` | entity tem process_type inválido |
| `entity 'X' collides with a legacy entity` | nome colide com `_entities` legacy |
| `connection ref 'X' not found in workspace 'Y'` | entity referencia source/target inexistente |
