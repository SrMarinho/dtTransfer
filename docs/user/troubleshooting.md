# Troubleshooting

## Workspace não aparece em `workspace list`

- `workspace.yml` malformado → `python -c "import yaml; yaml.safe_load(open('src/workspaces/X/workspace.yml'))"` para validar
- `id:` não é slug válido (precisa começar com letra; só letras, dígitos, `_`, `-`)
- Diretório começa com `.` → ignorado pelo loader

## Entity não aparece em `entity list -w X`

- Falta `entities/<nome>.yml`
- `process_type:` fora de `{full, incremental, monthly, unit}`
- `sql_file:` aponta para arquivo que não existe em `sqls/`

## `Entidade não encontrada` no `load`

- Esqueceu o prefixo do workspace → use `meuws/produto` ou `--workspace meuws`
- `bootstrap()` não rodou → executando direto via `python -m`? Use `python run.py`

## Erro de conexão

- `python run.py workspace validate` → mostra qual ref/driver falha
- Variáveis de ambiente faltando: `<ENV_PREFIX>_HOST`, `_PORT`, `_DATABASE`, `_USERNAME`, `_PASSWORD`
- SQLite só precisa `<PREFIX>_DATABASE` (caminho do arquivo)
- Oracle: `_SERVICE_NAME` opcional, `_ENCODING` opcional

## Migration "out of sync"

- DB tem revisão diferente da última versão em `migrations/versions/`
- `python run.py migrate status -w X` mostra `current` vs `available`
- `migrate upgrade -w X` aplica pendentes
- `migrate stamp -w X head` força marcar como atualizado (sem aplicar SQL — use só se sabe o que faz)

## CLI imprime `[deprecated]`

- Comando renomeado. Tabela de tradução:

| Antigo | Novo |
|--------|------|
| `list-workspaces` | `workspace list` |
| `list-tables` | `entity list` |
| `validate-config` | `workspace validate` |
| `check-errors` | `logs errors` |

Aliases removidos no próximo major.
