"""Connection helpers for direct DB inspection during local development.

Part of REQ 007 — Paket 2. Bootstraps clients for PostgreSQL, MongoDB and
Redis using the local docker-compose defaults. Override via env vars.

Usage:
    cd unifiedui/scripts/debug
    uv run --with psycopg2-binary --with pymongo --with redis python -i db_inspect.py

Then in the REPL:
    pg.execute("SELECT id, name FROM tenants LIMIT 5").fetchall()
    mongo.messages.find_one({"tenant_id": "t-1"})
    redis.keys("identity:*")

NEVER run this script against production. Local docker-compose only.
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import psycopg2.extensions  # type: ignore[import-not-found]
    import pymongo.database  # type: ignore[import-not-found]
    import redis as redis_lib  # type: ignore[import-not-found]


PG_HOST = os.environ.get("PG_HOST", "localhost")
PG_PORT = int(os.environ.get("PG_PORT", "5432"))
PG_USER = os.environ.get("PG_USER", "unifiedui")
PG_PASSWORD = os.environ.get("PG_PASSWORD", "unifiedui_password")
PG_DB = os.environ.get("PG_DB", "unifiedui")

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:admin@localhost:27017/")
MONGO_DB = os.environ.get("MONGO_DB", "unifiedui")

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "admin")
REDIS_DB = int(os.environ.get("REDIS_DB", "0"))


class _PG:
    """Thin convenience wrapper around a psycopg2 cursor."""

    def __init__(self, conn: "psycopg2.extensions.connection") -> None:
        self.conn = conn

    def execute(self, sql: str, params: tuple[Any, ...] | None = None) -> "psycopg2.extensions.cursor":
        """Run a SQL statement and return the open cursor (call .fetchall/.fetchone)."""
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur

    def tables(self) -> list[str]:
        """List all tables in the public schema."""
        cur = self.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
        )
        return [row[0] for row in cur.fetchall()]


def _connect_pg() -> _PG:
    import psycopg2  # type: ignore[import-not-found]

    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DB,
    )
    conn.autocommit = True
    return _PG(conn)


def _connect_mongo() -> "pymongo.database.Database":
    from pymongo import MongoClient  # type: ignore[import-not-found]

    client = MongoClient(MONGO_URI)
    return client[MONGO_DB]


def _connect_redis() -> "redis_lib.Redis":
    import redis  # type: ignore[import-not-found]

    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=REDIS_DB,
        decode_responses=True,
    )


def main() -> None:
    """Print connection status and inject pg/mongo/redis into the REPL globals."""
    print(f"[db_inspect] PG     {PG_USER}@{PG_HOST}:{PG_PORT}/{PG_DB}")
    print(f"[db_inspect] Mongo  {MONGO_URI} db={MONGO_DB}")
    print(f"[db_inspect] Redis  {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
    g = globals()
    try:
        g["pg"] = _connect_pg()
        print("[db_inspect] pg ok — try: pg.tables()")
    except Exception as exc:
        print(f"[db_inspect] pg FAILED: {exc}", file=sys.stderr)
    try:
        g["mongo"] = _connect_mongo()
        print(f"[db_inspect] mongo ok — collections: {g['mongo'].list_collection_names()[:5]} ...")
    except Exception as exc:
        print(f"[db_inspect] mongo FAILED: {exc}", file=sys.stderr)
    try:
        g["redis"] = _connect_redis()
        g["redis"].ping()
        print("[db_inspect] redis ok — try: redis.keys('identity:*')")
    except Exception as exc:
        print(f"[db_inspect] redis FAILED: {exc}", file=sys.stderr)


main()
