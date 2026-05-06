from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from src.engine.workspace.workspace import Workspace

REPO_ROOT = Path(__file__).resolve().parents[3]
RECYCLE_ROOT = REPO_ROOT / ".local" / "recycle_bin"


def _ts_now() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _write_metadata(dest: Path, data: dict) -> None:
    (dest / "_deleted_at").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _read_metadata(dest: Path) -> dict:
    meta = dest / "_deleted_at"
    if not meta.exists():
        return {}
    return json.loads(meta.read_text(encoding="utf-8"))


def _parse_timestamp(name: str) -> str | None:
    parts = name.rsplit("_", 1)
    return parts[1] if len(parts) == 2 and len(parts[1]) == 15 else None


# ─── Workspace ───────────────────────────────────────────────────────────────


def _ws_recycle_dir() -> Path:
    return RECYCLE_ROOT / "workspaces"


def _ws_dest_id(ws_id: str) -> str:
    return f"{ws_id}_{_ts_now()}"


def soft_delete_workspace(ws: Workspace) -> Path:
    src = Path(ws.root_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"Diretório do workspace não encontrado: {src}")

    dest = _ws_recycle_dir() / _ws_dest_id(ws.id)
    dest.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(str(src), str(dest))

    _write_metadata(dest, {
        "deleted_at": datetime.now().isoformat(),
        "type": "workspace",
        "workspace": ws.id,
        "original_path": str(src),
    })

    return dest


def hard_delete_workspace(ws: Workspace) -> None:
    src = Path(ws.root_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"Diretório do workspace não encontrado: {src}")
    shutil.rmtree(src)


def list_deleted_workspaces() -> List[Dict[str, Any]]:
    root = _ws_recycle_dir()
    if not root.exists():
        return []
    result = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        meta = _read_metadata(entry)
        ts = _parse_timestamp(entry.name)
        result.append({
            "id": meta.get("workspace", entry.name),
            "ts": ts or "unknown",
            "path": meta.get("original_path", ""),
            "deleted_at": meta.get("deleted_at", ""),
            "dir": entry,
        })
    return result


def restore_workspace(ws_id: str, timestamp: str | None = None) -> Path:
    deleted = list_deleted_workspaces()
    matches = [d for d in deleted if d["id"] == ws_id]
    if not matches:
        raise FileNotFoundError(
            f"Nenhum workspace '{ws_id}' encontrado na lixeira."
        )

    if timestamp:
        matches = [m for m in matches if m["ts"] == timestamp]
        if not matches:
            raise FileNotFoundError(
                f"Workspace '{ws_id}' com timestamp '{timestamp}' não encontrado."
            )

    entry = matches[-1]  # mais recente
    dest = Path(entry["path"])

    if dest.exists():
        raise FileExistsError(
            f"Já existe um diretório em {dest}. Remova ou renomeie antes de restaurar."
        )

    # Restore original metadata
    original_meta = _read_metadata(entry["dir"])
    # Remove _deleted_at before moving back
    meta_file = entry["dir"] / "_deleted_at"
    if meta_file.exists():
        meta_file.unlink()

    shutil.move(str(entry["dir"]), str(dest))

    return dest


# ─── Entity ──────────────────────────────────────────────────────────────────


def _entity_recycle_base() -> Path:
    return RECYCLE_ROOT / "entities"


def _entity_dest_id(name: str) -> str:
    return f"{name}_{_ts_now()}"


def _entity_yml_path(ws_dir: Path, name: str) -> Path:
    return ws_dir / "entities" / f"{name}.yml"


def _entity_sql_path(ws_dir: Path, name: str) -> Path | None:
    yml = _entity_yml_path(ws_dir, name)
    if not yml.exists():
        return None
    try:
        data = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
        sql_file = data.get("sql_file", f"consulta_{name}.sql")
        sql = ws_dir / "sqls" / sql_file
        return sql if sql.exists() else None
    except Exception:
        return None


def soft_delete_entity(ws_id: str, name: str, ws_dir: Path) -> Path:
    yml = _entity_yml_path(ws_dir, name)
    if not yml.exists():
        raise FileNotFoundError(
            f"Entity YAML não encontrado: {yml}"
        )

    dest = _entity_recycle_base() / ws_id / _entity_dest_id(name)
    dest.mkdir(parents=True, exist_ok=True)

    # Move YAML
    yml_dest = dest / yml.name
    shutil.move(str(yml), str(yml_dest))

    # Move SQL if exists
    sql_src = _entity_sql_path(ws_dir, name)
    sql_dest = None
    if sql_src:
        sql_dest = dest / sql_src.name
        shutil.move(str(sql_src), str(sql_dest))

    _write_metadata(dest, {
        "deleted_at": datetime.now().isoformat(),
        "type": "entity",
        "workspace": ws_id,
        "entity": name,
        "original_yml": str(yml_dest),
        "original_sql": str(sql_dest) if sql_dest else None,
    })

    return dest


def hard_delete_entity(ws_id: str, name: str, ws_dir: Path) -> None:
    yml = _entity_yml_path(ws_dir, name)
    yml.unlink(missing_ok=True)

    sql = _entity_sql_path(ws_dir, name)
    if sql:
        sql.unlink(missing_ok=True)


def list_deleted_entities(ws_id: str | None = None) -> List[Dict[str, Any]]:
    root = _entity_recycle_base()
    if not root.exists():
        return []

    result = []
    workspaces = [root / ws_id] if ws_id else sorted(root.iterdir())

    for ws_dir in workspaces:
        if not ws_dir.is_dir():
            continue
        for entry in sorted(ws_dir.iterdir()):
            if not entry.is_dir():
                continue
            meta = _read_metadata(entry)
            ts = _parse_timestamp(entry.name)
            result.append({
                "workspace": meta.get("workspace", ws_dir.name),
                "entity": meta.get("entity", entry.name),
                "ts": ts or "unknown",
                "deleted_at": meta.get("deleted_at", ""),
                "dir": entry,
            })

    return result


def restore_entity(ws_id: str, name: str, timestamp: str | None = None) -> None:
    deleted = list_deleted_entities(ws_id)
    matches = [d for d in deleted if d["entity"] == name]
    if not matches:
        raise FileNotFoundError(
            f"Nenhuma entidade '{ws_id}/{name}' encontrada na lixeira."
        )

    if timestamp:
        matches = [m for m in matches if m["ts"] == timestamp]
        if not matches:
            raise FileNotFoundError(
                f"Entidade '{ws_id}/{name}' com timestamp '{timestamp}' não encontrada."
            )

    entry = matches[-1]
    meta = _read_metadata(entry["dir"])

    yml_orig = REPO_ROOT / "src" / "workspaces" / ws_id / "entities" / f"{name}.yml"
    sql_orig = None
    if meta.get("original_sql"):
        sql_orig = Path(meta["original_sql"])

    if yml_orig.exists():
        raise FileExistsError(
            f"Já existe uma entidade '{ws_id}/{name}' em {yml_orig}. "
            "Remova ou use --force para sobrescrever."
        )

    yml_src = entry["dir"] / f"{name}.yml"
    if not yml_src.exists():
        raise FileNotFoundError(f"YAML não encontrado na lixeira: {yml_src}")

    yml_orig.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(yml_src), str(yml_orig))

    if meta.get("original_sql"):
        sql_src = entry["dir"] / Path(meta["original_sql"]).name
        if sql_src.exists():
            sql_orig_parent = Path(meta["original_sql"]).parent
            sql_orig_parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(sql_src), str(meta["original_sql"]))

    # Cleanup empty dir
    _cleanup_empty_dirs(entry["dir"])


def _cleanup_empty_dirs(path: Path) -> None:
    for parent in [path, path.parent]:
        try:
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
        except OSError:
            pass


__all__ = [
    "soft_delete_workspace",
    "hard_delete_workspace",
    "list_deleted_workspaces",
    "restore_workspace",
    "soft_delete_entity",
    "hard_delete_entity",
    "list_deleted_entities",
    "restore_entity",
]
