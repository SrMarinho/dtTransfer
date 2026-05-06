import pytest
from typer.testing import CliRunner
from run import app


@pytest.fixture
def runner():
    return CliRunner()


class TestLoadCommands:
    def test_load_full_help(self, runner):
        result = runner.invoke(app, ["load", "full", "--help"])
        assert result.exit_code == 0
        assert "Sincronizacao completa" in result.output
        assert "--table" in result.output
        assert "--truncate" in result.output

    def test_load_full_missing_table(self, runner):
        result = runner.invoke(app, ["load", "full"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "'--table'" in result.output

    def test_load_incremental_help(self, runner):
        result = runner.invoke(app, ["load", "incremental", "--help"])
        assert result.exit_code == 0
        assert "Sincronizacao incremental" in result.output
        assert "--days" in result.output
        assert "--threads" in result.output
        assert "--current-day" in result.output

    def test_load_incremental_missing_days(self, runner):
        result = runner.invoke(app, ["load", "incremental", "--table", "venda"])
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "--days" in result.output

    def test_load_monthly_help(self, runner):
        result = runner.invoke(app, ["load", "monthly", "--help"])
        assert result.exit_code == 0
        assert "--months" in result.output
        assert "--method" in result.output

    def test_load_unit_help(self, runner):
        result = runner.invoke(app, ["load", "unit", "--help"])
        assert result.exit_code == 0
        assert "--unit" in result.output

    def test_load_incremental_missing_table(self, runner):
        result = runner.invoke(app, ["load", "incremental", "--days", "5"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "'--table'" in result.output

    def test_load_incremental_default_threads(self, runner):
        result = runner.invoke(app, ["load", "incremental", "--table", "venda", "--days", "10", "--help"])
        assert result.exit_code == 0
        assert "--threads" in result.output

    def test_load_incremental_with_current_day(self, runner):
        result = runner.invoke(app, ["load", "incremental", "--table", "venda", "--days", "1", "--current-day", "--help"])
        assert result.exit_code == 0
        assert "--current-day" in result.output

    def test_load_monthly_missing_table(self, runner):
        result = runner.invoke(app, ["load", "monthly", "--months", "6"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "'--table'" in result.output

    def test_load_monthly_missing_months(self, runner):
        result = runner.invoke(app, ["load", "monthly", "--table", "venda"])
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "--months" in result.output

    def test_load_monthly_with_method(self, runner):
        result = runner.invoke(app, ["load", "monthly", "--table", "venda", "--months", "3", "--method", "wholeInterval", "--help"])
        assert result.exit_code == 0
        assert "wholeInterval" in result.output or "--method" in result.output

    def test_load_monthly_with_truncate(self, runner):
        result = runner.invoke(app, ["load", "monthly", "--table", "venda", "--months", "3", "--truncate", "--help"])
        assert result.exit_code == 0
        assert "--truncate" in result.output

    def test_load_unit_missing_table(self, runner):
        result = runner.invoke(app, ["load", "unit", "--unit", "2"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "'--table'" in result.output

    def test_load_unit_missing_unit(self, runner):
        result = runner.invoke(app, ["load", "unit", "--table", "estoque"])
        assert result.exit_code != 0

    def test_load_full_with_truncate(self, runner):
        result = runner.invoke(app, ["load", "full", "--table", "cliente", "--truncate", "--help"])
        assert result.exit_code == 0
        assert "--truncate" in result.output

    def test_load_full_without_truncate(self, runner):
        result = runner.invoke(app, ["load", "full", "--table", "cliente", "--help"])
        assert result.exit_code == 0
        assert "Sincronizacao completa" in result.output


class TestEntityCommand:
    def test_entity_list_help(self, runner):
        result = runner.invoke(app, ["entity", "list", "--help"])
        assert result.exit_code == 0
        assert "--deleted" in result.output

    def test_entity_list_all(self, runner):
        result = runner.invoke(app, ["entity", "list"])
        assert result.exit_code == 0
        assert "Entidades registradas" in result.output
        assert "cliente" in result.output

    def test_entity_list_biSenior(self, runner):
        result = runner.invoke(app, ["entity", "list", "biSenior"])
        assert result.exit_code == 0
        assert "biSenior/" in result.output

    def test_validate_insert_help(self, runner):
        result = runner.invoke(app, ["entity", "validate", "insert", "--help"])
        assert result.exit_code == 0
        assert "--values" in result.output
        assert "--columns" in result.output
        assert "--commit" in result.output
        assert "--sql-only" in result.output
        assert "--delimiter" in result.output
        assert "--notify" in result.output

    def test_validate_insert_sql_only(self, runner):
        result = runner.invoke(app, [
            "entity", "validate", "insert", "biMktNaz/cliente",
            "--values", "1,2",
            "--columns", "codigo_cliente,cnpj",
            "--sql-only",
        ])
        assert result.exit_code == 0
        assert "INSERT INTO cliente" in result.output
        assert "codigo_cliente" in result.output
        assert "cnpj" in result.output

    def test_validate_insert_mismatch_columns(self, runner):
        result = runner.invoke(app, [
            "entity", "validate", "insert", "biMktNaz/cliente",
            "--values", "1",
            "--columns", "codigo_cliente,cnpj",
        ])
        assert result.exit_code != 0
        assert "devem ter o mesmo numero" in result.output

    def test_validate_insert_missing_qualified(self, runner):
        result = runner.invoke(app, [
            "entity", "validate", "insert", "invalid",
            "--values", "1,2",
        ])
        assert result.exit_code != 0
        assert "formato esperado" in result.output


class TestWorkspaceCommand:
    def test_workspace_list_help(self, runner):
        result = runner.invoke(app, ["workspace", "list", "--help"])
        assert result.exit_code == 0

    def test_workspace_validate_help(self, runner):
        result = runner.invoke(app, ["workspace", "validate", "--help"])
        assert result.exit_code == 0


class TestLogsCommand:
    def test_logs_errors_help(self, runner):
        result = runner.invoke(app, ["logs", "errors", "--help"])
        assert result.exit_code == 0
        assert "--date" in result.output
        assert "--days-ago" in result.output
        assert "--since" in result.output
        assert "--until" in result.output
        assert "--detailed" in result.output

    def test_logs_errors_today_no_errors(self, runner):
        result = runner.invoke(app, ["logs", "errors"])
        assert result.exit_code in (0, 1)


class TestTableValidation:
    def test_invalid_table_rejected(self, runner):
        result = runner.invoke(app, ["load", "full", "--table", "tabela_inexistente"])
        assert result.exit_code != 0

    def test_valid_table_accepted(self, runner):
        # Just verify parsing passes; actual run would need DB
        result = runner.invoke(app, ["load", "full", "--table", "cliente"])
        # Exit code depends on DB availability; we're just checking parsing passes
        assert "Invalid value" not in result.output
