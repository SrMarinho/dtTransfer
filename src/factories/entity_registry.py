from src.core.logger.logging import logger
from src.core.entity import Entity

class EntityRegistry:
    _entities: dict = {}

    _workspace_entities: dict = {}

    @staticmethod
    def getInstance(queryName, params) -> Entity:
        if queryName in EntityRegistry._workspace_entities:
            factory = EntityRegistry._workspace_entities[queryName]
            return factory(params)
        if queryName in EntityRegistry._entities:
            return EntityRegistry._entities[queryName](params)
        logger.error(f"{queryName} - Entidade não encontrada!")
        raise ValueError(f"{queryName} - Entidade não encontrada!")

    @classmethod
    def valid_tables(cls) -> set:
        return set(cls._entities.keys()) | set(cls._workspace_entities.keys())

    @classmethod
    def list_tables(cls, system: str = None) -> list:
        tables = sorted(cls.valid_tables())
        if system:
            tables = [t for t in tables if t.startswith(f"{system}/")]
        return tables

    @classmethod
    def remove_entity(cls, key: str) -> None:
        cls._workspace_entities.pop(key, None)
        cls._entities.pop(key, None)

    @classmethod
    def remove_entity_prefix(cls, prefix: str) -> None:
        prefix = f"{prefix}/"
        cls._workspace_entities = {
            k: v for k, v in cls._workspace_entities.items() if not k.startswith(prefix)
        }
        cls._entities = {
            k: v for k, v in cls._entities.items() if not k.startswith(prefix)
        }

    @classmethod
    def register_yaml_workspace(cls, workspace) -> None:
        """Load YAML entity specs from a workspace and register them under
        '<workspace.id>/<entity_name>' keys. Raises if a key collides with
        an already-registered entity (legacy or YAML).
        """
        from src.engine.workspace.yaml_entity import YamlTable, load_entities

        specs = load_entities(workspace.entities_dir)
        for spec in specs:
            key = f"{workspace.id}/{spec.name}"
            if key in cls._entities:
                del cls._entities[key]
                logger.info(f"Migrated '{key}' from legacy to YAML workspace")
            # Re-registering the same key is a no-op (idempotent for repeated bootstraps).

            def _make(spec=spec, ws=workspace):
                return lambda params: YamlTable(spec=spec, workspace=ws, params=params)

            cls._workspace_entities[key] = _make()
