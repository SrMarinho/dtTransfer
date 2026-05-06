from unittest.mock import patch

from typer.testing import CliRunner

from src.interfaces.cli.commands.load import _resolve_table, app as load_app


class TestResolveTable:
    def test_prefixes_when_workspace_given_and_no_slash(self):
        assert _resolve_table("titulos_receber", "biSenior") == "biSenior/titulos_receber"

    def test_keeps_qualified_when_already_namespaced(self):
        assert _resolve_table("biMktNaz/ac_recebimentos", "biSenior") == "biMktNaz/ac_recebimentos"

    def test_no_workspace_keeps_raw(self):
        assert _resolve_table("foo", None) == "foo"


def test_load_full_passes_workspace_to_runner():
    runner = CliRunner()
    with patch("src.interfaces.cli.commands.load._run_process") as run:
        result = runner.invoke(
            load_app,
            ["full", "--table", "titulos_receber", "--workspace", "biSenior"],
        )
    assert result.exit_code == 0
    args, kwargs = run.call_args
    assert args[0] == "full"
    assert args[1] == "titulos_receber"
    assert args[3] == "biSenior"
