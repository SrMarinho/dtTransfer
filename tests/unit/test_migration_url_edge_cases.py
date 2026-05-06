"""Migration URL builder edge cases: all drivers, missing env vars."""
import pytest
from src.engine.workspace.migrations import build_sqlalchemy_url
from src.engine.workspace.workspace import ConnectionRef


class TestBuildUrl:
    def test_sqlite_relative(self, monkeypatch):
        monkeypatch.setenv("DB_X_DATABASE", "data/test.db")
        ref = ConnectionRef(driver="sqlite", env_prefix="DB_X")
        assert "sqlite:///data/test.db" in build_sqlalchemy_url(ref)

    def test_sqlite_absolute(self, monkeypatch):
        monkeypatch.setenv("DB_X_DATABASE", "/var/lib/data.db")
        ref = ConnectionRef(driver="sqlite", env_prefix="DB_X")
        assert "sqlite:////var/lib/data.db" in build_sqlalchemy_url(ref)

    def test_sqlite_windows_path(self, monkeypatch):
        monkeypatch.setenv("DB_X_DATABASE", "C:\\data\\test.db")
        ref = ConnectionRef(driver="sqlite", env_prefix="DB_X")
        url = build_sqlalchemy_url(ref)
        # windows absolute paths start with drive letter
        assert url.startswith("sqlite:///")

    def test_sqlite_empty_db(self, monkeypatch):
        monkeypatch.setenv("DB_X_DATABASE", "")
        ref = ConnectionRef(driver="sqlite", env_prefix="DB_X")
        url = build_sqlalchemy_url(ref)
        assert url == "sqlite:///"

    def test_postgres_full(self, monkeypatch):
        monkeypatch.setenv("DB_PG_HOST", "pg.example.com")
        monkeypatch.setenv("DB_PG_PORT", "5432")
        monkeypatch.setenv("DB_PG_DATABASE", "mydb")
        monkeypatch.setenv("DB_PG_USERNAME", "user")
        monkeypatch.setenv("DB_PG_PASSWORD", "pass")
        ref = ConnectionRef(driver="postgres", env_prefix="DB_PG")
        url = build_sqlalchemy_url(ref)
        assert "postgresql+psycopg2://user:pass@pg.example.com:5432/mydb" in url

    def test_postgres_default_port(self, monkeypatch):
        monkeypatch.setenv("DB_PG_HOST", "h")
        monkeypatch.setenv("DB_PG_DATABASE", "d")
        monkeypatch.setenv("DB_PG_USERNAME", "u")
        monkeypatch.setenv("DB_PG_PASSWORD", "p")
        ref = ConnectionRef(driver="postgres", env_prefix="DB_PG")
        url = build_sqlalchemy_url(ref)
        assert ":5432" in url

    def test_sqlserver_full(self, monkeypatch):
        monkeypatch.setenv("DB_SS_HOST", "sql.example.com")
        monkeypatch.setenv("DB_SS_PORT", "1433")
        monkeypatch.setenv("DB_SS_DATABASE", "mssql_db")
        monkeypatch.setenv("DB_SS_USERNAME", "sa")
        monkeypatch.setenv("DB_SS_PASSWORD", "p@ss")
        ref = ConnectionRef(driver="sqlserver", env_prefix="DB_SS")
        url = build_sqlalchemy_url(ref)
        assert "mssql+pyodbc://sa:p" in url

    def test_oracle_with_service_name(self, monkeypatch):
        monkeypatch.setenv("DB_OR_HOST", "ora.example.com")
        monkeypatch.setenv("DB_OR_PORT", "1521")
        monkeypatch.setenv("DB_OR_USER", "system")
        monkeypatch.setenv("DB_OR_PASSWORD", "oracle")
        monkeypatch.setenv("DB_OR_SERVICE_NAME", "XE")
        ref = ConnectionRef(driver="oracle", env_prefix="DB_OR")
        url = build_sqlalchemy_url(ref)
        assert "oracle+oracledb://system:oracle@ora.example.com:1521" in url
        assert "service_name=XE" in url

    def test_oracle_username_fallback(self, monkeypatch):
        monkeypatch.setenv("DB_OR_HOST", "h")
        monkeypatch.setenv("DB_OR_PORT", "1521")
        monkeypatch.setenv("DB_OR_USERNAME", "sys")
        monkeypatch.setenv("DB_OR_PASSWORD", "p")
        monkeypatch.setenv("DB_OR_DATABASE", "XE")
        ref = ConnectionRef(driver="oracle", env_prefix="DB_OR")
        url = build_sqlalchemy_url(ref)
        assert "sys" in url

    def test_unknown_driver_raises(self):
        ref = ConnectionRef(driver="fake", env_prefix="DB_X")
        with pytest.raises(ValueError, match="unsupported driver"):
            build_sqlalchemy_url(ref)

    def test_postgres_missing_optional_port(self, monkeypatch):
        monkeypatch.setenv("DB_PG_HOST", "h")
        monkeypatch.setenv("DB_PG_DATABASE", "d")
        monkeypatch.setenv("DB_PG_USERNAME", "u")
        monkeypatch.setenv("DB_PG_PASSWORD", "p")
        ref = ConnectionRef(driver="postgres", env_prefix="DB_PG")
        url = build_sqlalchemy_url(ref)
        assert "5432" in url  # default port
