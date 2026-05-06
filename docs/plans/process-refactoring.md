# Plano: Refatorar src/processes/ para SOLID e testabilidade

## Context

Os processos em `src/processes/` concentram toda a lógica de ETL mas têm acoplamento alto que os torna difíceis de testar e evoluir:

- **`EntityRegistry.getInstance()` chamado dentro de `run()`** — impossível injetar um `Table` fake sem mockear a factory
- **`params: dict` com strings mágicas** — `"truncate"`, `"days"`, `"full"` sem schema; typos silenciosos; bool passado como `"True"` vs `True`
- **`date.today()` hardcoded** — datas não são injetáveis, dificultando testes de lógica de janela temporal
- **Logger global** — não há como observar o que foi logado em testes unitários
- **`threading.Thread` sem abstração** — `Incremental` gerencia threads manualmente, acoplando orquestração e execução
- Consequência: 0% de cobertura unitária em `run()`, `oneDay()`, `oneMonth()`; tudo depende de banco real

---

## Arquivos Críticos

| Arquivo | Papel |
|---|---|
| `src/processes/process.py` | Base abstrata — adicionar `__init__` com injeção |
| `src/processes/full_query.py` | `run()` acoplado à factory e driver |
| `src/processes/incremental.py` | `run()` + `oneDay()` + threads + datas hardcoded |
| `src/processes/monthly.py` | `run()` + `byMonth()` + `wholeInterval()` + datas hardcoded |
| `src/processes/unit.py` | `run()` acoplado à factory |
| `src/factories/process_factory.py` | Ponto onde injeção do `Table` deve acontecer |
| `src/interfaces/cli/commands/load.py` | Caller — passa params; precisa construir dataclass |
| `src/core/table.py` | `Table` base — nenhuma mudança estrutural necessária |
| `tests/unit/` | Novos testes unitários de processo |

---

## Abordagem

### 1. Injetar `Table` no construtor (maior ganho de testabilidade)

Processos param de receber `params['table']` e chamar a factory internamente para receber a instância já resolvida:

```python
# ANTES
class FullQuery:
    def run(self):
        table = EntityRegistry.getInstance(self.params['table'], self.params)

# DEPOIS
class FullQuery:
    def __init__(self, table: Table, params: FullQueryParams):
        self.table = table
        self.params = params
```

A responsabilidade de resolver `EntityRegistry.getInstance()` sobe para `ProcessFactory` e para o CLI.

### 2. Substituir `dict` por dataclasses tipados

Um dataclass por processo, eliminando strings mágicas e parse de `"True"`/`"False"`:

```python
@dataclass
class FullQueryParams:
    truncate: bool = False

@dataclass
class IncrementalParams:
    days: Optional[int] = None
    threads: int = 4
    truncate: bool = False
    current_day: bool = False
    full: bool = False

@dataclass
class MonthlyParams:
    months: Optional[int] = None
    method: str = "byMonth"
    truncate: bool = False
    full: bool = False

@dataclass
class UnitParams:
    unit: int = 0
```

Localização: `src/processes/params.py`

### 3. Clock injetável para datas

```python
# ANTES (em incremental.py)
today = date.today()

# DEPOIS
class Incremental:
    def __init__(self, table, params, today_fn=date.today, on_progress=None):
        self.today_fn = today_fn
    def run(self):
        today = self.today_fn()
```

Permite testes com data fixa sem monkeypatching de módulo.

### 4. Logger opcional (injetável, fallback global)

```python
class FullQuery:
    def __init__(self, table, params, logger=None):
        self._logger = logger or _default_logger
```

Permite espionar logs em testes sem afetar produção.

### 5. Substituir `threading.Thread` manual por `ThreadPoolExecutor`

`Incremental` troca 20 linhas de setup/join de threads por:

```python
with ThreadPoolExecutor(max_workers=threads_num) as executor:
    futures = [executor.submit(self.oneDay, table, query, day) for day in days]
    for f in as_completed(futures):
        f.result()  # propaga exceções
```

Simplifica e permite testes com `max_workers=1` (sequencial, determinístico).

---

## Passos de Implementação

1. **Criar `src/processes/params.py`** com os 4 dataclasses tipados
2. **Atualizar `Process.__init__`** para aceitar `(table: Table, params, logger=None)`
3. **Refatorar `FullQuery`**: remover chamada à factory, usar `self.table`, aceitar `FullQueryParams`
4. **Refatorar `Incremental`**: injetar `table`, `today_fn`, usar `IncrementalParams`, trocar threads por `ThreadPoolExecutor`
5. **Refatorar `Monthly`**: idem, injetar `today_fn`, usar `MonthlyParams`
6. **Refatorar `Unit`**: injetar `table`, usar `UnitParams`
7. **Atualizar `ProcessFactory`**: resolver `EntityRegistry.getInstance()` aqui antes de instanciar o processo
8. **Atualizar CLI `load.py`**: construir dataclass a partir dos parâmetros Typer (já são tipados) e passar ao `ProcessFactory`
9. **Atualizar testes existentes** (`test_ndays_progress.py`, `test_bisenior_load.py`) para nova assinatura
10. **Escrever testes unitários** para `FullQuery.run()`, `Incremental.run()`, `Monthly.byMonth()` usando `FakeDatabaseDriver` + table mock + data fixa

---

## Testes Unitários Alvo (novos)

```
tests/unit/test_full_query.py
  - test_run_inserts_rows_from_source
  - test_run_truncates_before_insert_when_flag_set
  - test_run_does_not_truncate_when_flag_false

tests/unit/test_incremental.py
  - test_run_processes_correct_number_of_days
  - test_run_includes_current_day_when_flag_set
  - test_run_truncates_before_processing
  - test_run_full_skips_date_filtering

tests/unit/test_monthly.py
  - test_bymonth_processes_correct_number_of_months
  - test_wholeinterval_executes_single_query
```

---

## Verificação

```bash
# Todos os testes unitários existentes continuam passando
python -m pytest tests/unit/ tests/bot/ -v

# Novos testes unitários passam sem banco real
python -m pytest tests/unit/test_full_query.py tests/unit/test_incremental.py tests/unit/test_monthly.py -v

# Testes de integração continuam passando com banco real
python -m pytest tests/integration/test_bisenior_load.py -v

# CLI responde corretamente
python run.py --help
python run.py list-tables list-tables
```

---

## Impacto e Riscos

- **Sem mudança de comportamento** em produção — apenas encapsula dependências que já existem
- **ProcessFactory** continua sendo o único ponto de entrada público; callers externos não mudam
- **Compatibilidade**: `test_bisenior_load.py` instancia processos diretamente com `dict` — será atualizado no passo 9
- **`retry.py`** não muda — é utilitário puro e já está bem testado

---

*Salvar versão final em `docs/plans/process-refactoring.md` após aprovação.*

