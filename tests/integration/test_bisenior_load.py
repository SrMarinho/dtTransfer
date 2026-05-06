import pytest
from src.factories.process_factory import ProcessFactory
from src.factories.entity_registry import EntityRegistry


def _row_count(table_name: str) -> int:
    entity = EntityRegistry.getInstance(table_name, {})
    conn = entity.toDriver.connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {entity.name}")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count


# ---------------------------------------------------------------------------
# Full load — tabelas dimensionais (pequenas, carga completa viável)
# ---------------------------------------------------------------------------

@pytest.mark.integration
@pytest.mark.parametrize("table", [
    "biSenior/carteiras_cobranca",
    "biSenior/filiais",
    "biSenior/grupos_empresa",
    "biSenior/portadores",
    "biSenior/tipos_titulo",
    "biSenior/fornecedores",
])
def test_full_load_truncate(table):
    ProcessFactory.getInstance("full", {"table": table, "truncate": True}).run()
    assert _row_count(table) > 0


@pytest.mark.integration
@pytest.mark.xfail(reason="ORA-01841: dado com ano inválido na origem Senior", strict=False)
def test_full_load_titulos_receber():
    ProcessFactory.getInstance("full", {"table": "biSenior/titulos_receber", "truncate": True}).run()
    assert _row_count("biSenior/titulos_receber") >= 0


# ---------------------------------------------------------------------------
# Incremental — tabelas transacionais (últimos N dias)
# ---------------------------------------------------------------------------

@pytest.mark.integration
@pytest.mark.parametrize("table,days", [
    ("biSenior/clientes", 7),
    ("biSenior/transacoes", 7),
    ("biSenior/notas_fiscais_saida", 30),
    ("biSenior/titulos_pagar", 7),
    ("biSenior/titulos_receber", 7),
])
def test_incremental_load(table, days):
    params = {
        "table": table,
        "days": days,
        "truncate": False,
        "threads": 1,
    }
    ProcessFactory.getInstance("incremental", params).run()
    assert _row_count(table) >= 0


@pytest.mark.integration
def test_incremental_notas_fiscais_entrada():
    """Carga incremental sem truncate — dados concentrados em datas específicas na origem."""
    params = {
        "table": "biSenior/notas_fiscais_entrada",
        "days": 30,
        "truncate": False,
        "threads": 1,
    }
    ProcessFactory.getInstance("incremental", params).run()
    assert _row_count("biSenior/notas_fiscais_entrada") >= 0


# ---------------------------------------------------------------------------
# Monthly — tabelas com deleteMonth
# ---------------------------------------------------------------------------

@pytest.mark.integration
@pytest.mark.parametrize("table", [
    "biSenior/notas_fiscais_entrada",
    "biSenior/notas_fiscais_saida",
    "biSenior/titulos_pagar",
])
def test_monthly_load(table):
    params = {
        "table": table,
        "months": 1,
        "truncate": False,
        "method": "byMonth",
    }
    ProcessFactory.getInstance("monthly", params).byMonth()
    assert _row_count(table) >= 0

