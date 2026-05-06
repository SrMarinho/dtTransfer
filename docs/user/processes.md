# Processos ETL

DataReplicator tem 4 processos de carga, selecionados pelo subcomando `load`:

```
python run.py load <processo> --table <entidade> [opções]
```

---

## `full` — Carga completa

Executa a query sem filtro de data, insere tudo. Ideal para tabelas de referência (dimensões estáticas).

```bash
python run.py load full --table biSenior/fornecedores --truncate
python run.py load full --table biSenior/clientes --truncate
```

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--table` / `-t` | *obrigatório* | Nome da entidade |
| `--truncate` | `False` | Trunca destino antes de inserir |

**Quando usar:** tabelas pequenas, masterdata, primeira carga de qualquer tabela.

**Requisito SQL:** query sem `REPLACE_START_DATE`/`REPLACE_END_DATE`.

---

## `incremental` — Carga por dias

Processa N dias no passado, um dia por thread. Para cada dia: delete + insert com filtro de data.

```bash
# Últimos 7 dias, 4 threads
python run.py load incremental --table biSenior/notas_fiscais_saida --days 7 --threads 4

# Incluindo hoje
python run.py load incremental --table biSenior/titulos_receber --days 1 --current-day

# Full load (sem loop de dias)
python run.py load incremental --table biSenior/notas_fiscais_saida --full --truncate
```

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--table` / `-t` | *obrigatório* | Nome da entidade |
| `--days` / `-d` | *obrigatório¹* | Dias atrás a sincronizar |
| `--threads` | `4` | Threads paralelas (1–50) |
| `--truncate` | `False` | Trunca destino antes de processar |
| `--current-day` | `False` | Inclui o dia atual (padrão: começa ontem) |
| `--full` | `False` | Full load: trunca + insere sem filtro de data |

> ¹ `--days` é dispensável quando `--full` é usado.

**Quando usar:** dados transacionais com coluna de data (`data_emissao`, `data_vencimento`, etc).

**Requisito SQL:** query com placeholders `REPLACE_START_DATE` e `REPLACE_END_DATE`.

**Requisito entidade:** `deleteDay(startDate, endDate)` implementado.

### Como funciona o `--full`

Com `--full`, o processo ignora o loop de dias:
1. Trunca a tabela (se `--truncate`)
2. Remove os filtros de data da query (`WHERE ... REPLACE_START_DATE ...`)
3. Executa a query limpa e insere tudo em batches

---

## `monthly` — Carga por meses

Processa N meses, mês a mês (sequencial). Para cada mês: delete + insert com filtro mensal.

```bash
# Últimos 3 meses
python run.py load monthly --table biSenior/balancete_contabil --months 3

# Intervalo completo de uma vez (sem loop)
python run.py load monthly --table biSenior/balancete_contabil --months 6 --method wholeInterval

# Full load (sem filtro de data)
python run.py load monthly --table biSenior/balancete_contabil --full --truncate
```

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--table` / `-t` | *obrigatório* | Nome da entidade |
| `--months` / `-m` | *obrigatório¹* | Meses atrás a sincronizar |
| `--method` | `byMonth` | `byMonth` (sequencial) ou `wholeInterval` (intervalo único) |
| `--truncate` | `False` | Trunca destino antes de processar |
| `--full` | `False` | Full load: trunca + insere sem filtro de data |

> ¹ `--months` é dispensável quando `--full` é usado.

**Quando usar:** dados com granularidade mensal — balancetes, conciliação bancária.

**Requisito SQL:** query com `REPLACE_START_DATE` e `REPLACE_END_DATE`.

**Requisito entidade:** `deleteMonth(startDate, endDate)` implementado.

### `byMonth` vs `wholeInterval`

| | `byMonth` | `wholeInterval` |
|---|---|---|
| Delete | Um mês de cada vez | Todo o intervalo de uma vez |
| Insert | Um mês de cada vez | Todo o intervalo de uma vez |
| Uso | Dado que muda mês a mês | Dado imutável por período |

---

## `unit` — Carga por unidade

Processa dados de uma unidade/CD específica, substituindo `REPLACE_UNIT_HERE` na query.

```bash
python run.py load unit --table estoque --unit 2
```

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--table` / `-t` | *obrigatório* | Nome da entidade |
| `--unit` / `-u` | *obrigatório* | ID da unidade/CD |

**Quando usar:** tabelas particionadas por CD/unidade onde carga global é inviável.

---

## Comparação

| Processo | Threading | Filtro | `--full` | Uso típico |
|----------|-----------|--------|----------|------------|
| `full` | ✗ | Nenhum | — | Referências, masterdata |
| `incremental` | ✓ (por dia) | Data diária | ✓ | Transacional (NF, títulos) |
| `monthly` | ✗ | Data mensal | ✓ | Balancetes, conciliação |
| `unit` | ✗ | Por unidade | ✗ | Estoque por CD |

---

## Adicionando um novo processo

> Para adicionar tipos de processo customizados, veja o [guia de desenvolvedor](../dev/custom-processes.md).
