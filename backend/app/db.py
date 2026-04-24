from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

from app.config import settings


_pool: MySQLConnectionPool | None = None


def get_pool() -> MySQLConnectionPool:
    global _pool
    if _pool is None:
        _pool = MySQLConnectionPool(
            pool_name="musicdb_pool",
            pool_size=8,
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
        )
    return _pool


@contextmanager
def get_connection() -> Iterator[Any]:
    conn = get_pool().get_connection()
    try:
        yield conn
    finally:
        conn.close()


def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]


def fetch_one(query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    rows = fetch_all(query, params)
    return rows[0] if rows else None


def execute(query: str, params: tuple[Any, ...] = ()) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount


def call_proc(proc_name: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            placeholders = ", ".join(["%s"] * len(params)) if params else ""
            proc_call = f"CALL {proc_name}({placeholders})"
            cursor.execute(proc_call, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
