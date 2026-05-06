from src.factories.entity_registry import EntityRegistry
import typer


def validate_table(table: str) -> str:
    if table not in EntityRegistry.valid_tables():
        raise typer.BadParameter(f"Tabela '{table}' nao registrada!")
    return table
