import typer
from src.factories.database_factory import DatabaseFactory, Database

app = typer.Typer(help="Valida conexoes de banco de dados")


@app.command()
def validate_config():
    """Testa a conexao com todos os bancos de dados configurados."""
    databases = [db for db in Database if db != Database.FAKEDATABASE]
    ok = []
    failed = []
    for db_enum in databases:
        try:
            db = DatabaseFactory.getInstance(db_enum)
            conn = db.connection()
            cursor = conn.cursor()
            if db.driver == "pgsql":
                cursor.execute("SELECT 1")
            else:
                cursor.execute("SELECT 1 FROM DUAL")
            cursor.fetchone()
            cursor.close()
            conn.close()
            ok.append(db.name)
            typer.secho(f"OK  {db.name}", fg=typer.colors.GREEN)
        except Exception as e:
            failed.append((db.name, str(e)))
            typer.secho(f"ERR {db.name}: {e}", fg=typer.colors.RED, err=True)

    if failed:
        raise typer.Exit(code=1)
