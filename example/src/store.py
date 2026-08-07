"""Persistencia. SQLite, una tabla."""
import sqlite3
import time
from pathlib import Path

from .codes import FIRST_ID, encode

DB = Path("links.db")
SCHEMA = """
CREATE TABLE IF NOT EXISTS links (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  target   TEXT    NOT NULL,
  created  INTEGER NOT NULL,
  expires  INTEGER,
  hits     INTEGER NOT NULL DEFAULT 0
);
"""


def connect(path: Path = DB) -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.execute(SCHEMA)
    # `sqlite_sequence` no tiene fila para la tabla hasta el PRIMER insert, así que el
    # UPDATE solo no hacía nada en una base nueva y el primer código salía "1" — justo lo
    # que el piso existe para evitar. Lo encontró okf-init leyendo el código.
    con.execute(
        "INSERT INTO sqlite_sequence (name, seq) SELECT 'links', ? "
        "WHERE NOT EXISTS (SELECT 1 FROM sqlite_sequence WHERE name = 'links')",
        (FIRST_ID,),
    )
    con.execute("UPDATE sqlite_sequence SET seq = MAX(seq, ?) WHERE name = 'links'", (FIRST_ID,))
    con.commit()
    return con


def shorten(con: sqlite3.Connection, target: str, ttl_days: int | None = None) -> str:
    expires = int(time.time()) + ttl_days * 86400 if ttl_days else None
    cur = con.execute(
        "INSERT INTO links (target, created, expires) VALUES (?, ?, ?)",
        (target, int(time.time()), expires),
    )
    con.commit()
    return encode(cur.lastrowid)


def resolve(con: sqlite3.Connection, link_id: int) -> tuple[str, bool] | None:
    row = con.execute("SELECT target, expires FROM links WHERE id = ?", (link_id,)).fetchone()
    if row is None:
        return None
    target, expires = row
    return target, bool(expires and expires < time.time())


def count_hit(con: sqlite3.Connection, link_id: int) -> None:
    con.execute("UPDATE links SET hits = hits + 1 WHERE id = ?", (link_id,))
    con.commit()
