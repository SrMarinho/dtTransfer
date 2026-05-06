from enum import Enum

from src.core.databases.fake_database import FakeDatabaseDriver


class Database(Enum):
    PBSNAZARIADADOS = 'PbsNazariaDados'
    BIMKTNAZ = 'biMktNaz'
    NEWBIMKTNAZ = 'NewBiMktNaz'
    SENIOR = 'Senior'
    BISENIOR = 'biSenior'
    BINAZARIA = 'biNazaria'
    FAKEDATABASE = 'FakeDatabase'


_ENUM_TO_WORKSPACE = {
    Database.PBSNAZARIADADOS: ("biMktNaz", "PbsNazariaDados"),
    Database.BIMKTNAZ: ("biMktNaz", "biMktNaz"),
    Database.NEWBIMKTNAZ: ("biMktNaz", "biMktNaz"),
    Database.SENIOR: ("biSenior", "Senior"),
    Database.BISENIOR: ("biSenior", "biSenior"),
    Database.BINAZARIA: ("biNazaria", "biNazaria"),
}


class DatabaseFactory:
    @staticmethod
    def getInstance(database_type):
        # Legacy Database enum → resolve via workspace
        if isinstance(database_type, Database):
            if database_type == Database.FAKEDATABASE:
                return FakeDatabaseDriver()
            ws_id, ref_name = _ENUM_TO_WORKSPACE.get(database_type, (None, None))
            if ws_id is None:
                raise ValueError("Banco de dados não encontrado!")
            return _resolve_from_workspace(ws_id, ref_name)

        # Workspace-aware: tuple (workspace_id, connection_ref)
        if isinstance(database_type, tuple) and len(database_type) == 2:
            return _resolve_from_workspace(*database_type)

        raise ValueError("Banco de dados não encontrado!")


def _resolve_from_workspace(workspace_id: str, ref_name: str):
    # Lazy import to avoid circular at module load
    from src.engine.workspace.registry import WorkspaceRegistry, WorkspaceNotFoundError
    from src.core.databases.generic import GenericDatabase

    try:
        ws = WorkspaceRegistry().get(workspace_id)
    except WorkspaceNotFoundError as e:
        raise ValueError(str(e)) from e

    candidates = [ws.target] + list(ws.sources)
    for ref in candidates:
        if ref.name == ref_name or ref.env_prefix == ref_name:
            return GenericDatabase(ref, workspace_id)
    raise ValueError(
        f"connection ref '{ref_name}' not found in workspace '{workspace_id}'"
    )


__all__ = ['Database', 'DatabaseFactory']
