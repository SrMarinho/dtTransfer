# Plano de Melhorias no CLI

## Decisões
- **Biblioteca**: Typer
- **Compatibilidade**: Quebrar — remover `--params +key value`
- **Entry point (`drep`)**: Não por enquanto
- **Novos subcomandos**: `load`, `list-tables`, `validate-config`, `check-errors`
- **Nome da tabela**: Flag (`--table`)

## Nova Interface

```bash
# LOAD
python run.py load regular --table cliente --truncate
python run.py load nDaysAgo --table venda --days 10 --threads 10
python run.py load nMonthsAgo --table recebimentos --months 4 --method byMonth
python run.py load perUnit --table estoque --unit 2

# LIST
python run.py list-tables
python run.py list-tables --system biSenior

# VALIDATE
python run.py validate-config

# CHECK
python run.py check-errors
python run.py check-errors --since 10:00 --until 16:00
python run.py check-errors --date 2026-04-27
```

## Estratégia de Commits (Reduzida)

1. `feat: adiciona typer e reescreve CLI com subcomandos` — requirements, run.py, cli/load, validators
2. `feat: adiciona list-tables, validate-config e check-errors` — novos comandos + helper factory
3. `docs: atualiza documentação para novo CLI` — usage.md, README.md, deployment.md, agendamentos
4. `test: adiciona testes unitários para CLI` — test_cli.py
