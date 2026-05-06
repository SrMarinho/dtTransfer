import re
from typing import Optional


def limit_query(sql: str, n: int, driver: str) -> str:
    clean = sql.strip().rstrip(";")
    driver = driver.lower()

    if driver == "sqlserver":
        return f"SET ROWCOUNT {n};\n{clean}\nSET ROWCOUNT 0;"

    if driver == "oracle":
        if re.search(r"^\s*SELECT\b", clean, re.IGNORECASE):
            return f"SELECT * FROM ({clean}) WHERE ROWNUM <= {n}"
        raise ValueError(
            "Oracle limit nao suportado para queries nao-SELECT. "
            "Use um SQL que comeca com SELECT."
        )

    if driver in ("postgres", "pgsql"):
        if re.search(r"^\s*SELECT\b", clean, re.IGNORECASE):
            return f"SELECT * FROM ({clean}) AS _lim LIMIT {n}"
        raise ValueError(
            "Postgres limit nao suportado para queries nao-SELECT. "
            "Use um SQL que comeca com SELECT."
        )

    return sql
