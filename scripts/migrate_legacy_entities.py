"""One-time migration: convert legacy Python entities to YAML workspaces."""

import ast
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_entity_registry() -> list[dict]:
    path = REPO_ROOT / "src" / "factories" / "entity_registry.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))

    entities = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            target = node.targets[0] if node.targets else None
            if isinstance(target, ast.Name) and target.id == "_entities":
                for key, val in zip(node.value.keys, node.value.values):
                    entity_key = ast.literal_eval(key)
                    if isinstance(val, ast.Attribute):
                        module_prefix = val.value.id
                        class_name = val.attr
                    elif isinstance(val, ast.Name):
                        module_prefix = val.id
                        class_name = None
                    else:
                        print(f"  [WARN] unexpected value type for {entity_key}: {type(val).__name__}")
                        continue
                    entities.append({
                        "key": entity_key,
                        "module": module_prefix,
                        "class_name": class_name,
                    })
    return entities


def resolve_workspace(key: str, module: str) -> str:
    if module == "Senior":
        return "biSenior"
    if module == "Pbs":
        if key.startswith("biNazaria/"):
            return "biNazaria"
        return "biMktNaz"
    raise ValueError(f"Unknown module: {module}")


def entity_name(key: str) -> str:
    return key.split("/", 1)[-1]


def sql_filename(name: str) -> str:
    return f"consulta_{name}.sql"


def find_sql_file_in_system(name: str, module: str) -> Path | None:
    if module == "Pbs":
        base = REPO_ROOT / "src" / "systems" / "pbs" / "sqls"
    elif module == "Senior":
        base = REPO_ROOT / "src" / "systems" / "senior" / "sqls"
    else:
        return None
    path = base / f"consulta_{name}.sql"
    return path if path.exists() else None


def get_entity_py_path(name: str, module: str) -> Path | None:
    if module == "Pbs":
        base = REPO_ROOT / "src" / "systems" / "pbs" / "entities"
    elif module == "Senior":
        base = REPO_ROOT / "src" / "systems" / "senior" / "entities"
    else:
        return None
    p = base / f"{name}.py"
    return p if p.exists() else None


def parse_entity_py(py_path: Path) -> tuple[list[str], str | None]:
    if not py_path:
        return [], None
    tree = ast.parse(py_path.read_text(encoding="utf-8"))
    columns = []
    incremental_col = None

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if (
                    isinstance(t, ast.Attribute)
                    and isinstance(t.value, ast.Name)
                    and t.value.id == "self"
                ):
                    if t.attr == "columns" and isinstance(node.value, ast.List):
                        columns = [
                            el.value
                            for el in node.value.elts
                            if isinstance(el, ast.Constant)
                        ]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in ("deleteDay", "deleteMonth"):
            for inner in ast.walk(node):
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "execute"
                ):
                    for arg in inner.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            sql = arg.value
                            m = re.search(
                                r"DELETE\s+FROM\s+\S+\s+WHERE\s+(\w+)",
                                sql,
                                re.IGNORECASE | re.DOTALL,
                            )
                            if m:
                                col = m.group(1).split("::")[0]
                                if col and incremental_col is None:
                                    incremental_col = col
                                    break

    return columns, incremental_col


def generate_yaml_content(
    key: str,
    module: str,
    columns: list[str],
    incremental_column: str | None,
) -> str:
    lines = []
    lines.append("$schema: ../../../../schemas/entity.json")
    e_name = entity_name(key)
    lines.append(f"name: {e_name}")
    lines.append(f"target_table: {e_name}")

    if module == "Pbs":
        source = "PbsNazariaDados"
        target = "biNazaria" if key.startswith("biNazaria/") else "biMktNaz"
    else:
        source = "Senior"
        target = "biSenior"

    lines.append(f"source: {source}")
    lines.append(f"target: {target}")
    lines.append("process_type: full")
    if incremental_column:
        lines.append(f"incremental_column: {incremental_column}")
    lines.append(f"sql_file: {sql_filename(e_name)}")
    if columns:
        lines.append("columns:")
        for c in columns:
            lines.append(f"  - {c}")
    return "\n".join(lines) + "\n"


def main():
    entities = parse_entity_registry()
    print(f"Encontradas {len(entities)} entidades no registry\n")

    stats = {"generated": 0, "sql_copied": 0, "skipped": 0}

    for entry in entities:
        key = entry["key"]
        module = entry["module"]
        name = entity_name(key)
        workspace = resolve_workspace(key, module)

        ws_dir = REPO_ROOT / "src" / "workspaces" / workspace
        entities_dir = ws_dir / "entities"
        sqls_dir = ws_dir / "sqls"
        entities_dir.mkdir(parents=True, exist_ok=True)
        sqls_dir.mkdir(parents=True, exist_ok=True)

        # Copy SQL file
        sql_src = find_sql_file_in_system(name, module)
        if sql_src and sql_src.exists():
            dst = sqls_dir / sql_src.name
            if not dst.exists():
                shutil.copy2(sql_src, dst)
                stats["sql_copied"] += 1

        # Parse entity Python file
        py_path = get_entity_py_path(name, module)
        columns, incremental_col = parse_entity_py(py_path)

        # Generate YAML
        yaml_path = entities_dir / f"{name}.yml"
        if yaml_path.exists():
            stats["skipped"] += 1
            continue

        content = generate_yaml_content(key, module, columns, incremental_col)
        yaml_path.write_text(content, encoding="utf-8")
        stats["generated"] += 1
        print(f"  [{workspace}] {key}" + (f"  (incr_col={incremental_col})" if incremental_col else ""))

    print(f"\nGerados: {stats['generated']}")
    print(f"SQLs copiados: {stats['sql_copied']}")
    print(f"Pulados: {stats['skipped']}")


if __name__ == "__main__":
    main()
