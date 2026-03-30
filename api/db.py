import os
from typing import Any, Dict, List, Optional, Tuple

import psycopg


def _database_url() -> Optional[str]:
    # Prefer explicit DATABASE_URL, but also support:
    # - Vercel Postgres env vars (POSTGRES_URL*)
    # - Supabase ↔ Vercel Integration env vars (DATABASE_POSTGRES_URL*)
    candidates = [
        os.getenv("DATABASE_URL"),
        os.getenv("DATABASE_POSTGRES_URL_NON_POOLING"),
        os.getenv("DATABASE_POSTGRES_URL"),
        os.getenv("DATABASE_POSTGRES_PRISMA_URL"),
        os.getenv("POSTGRES_URL_NON_POOLING"),
        os.getenv("POSTGRES_URL"),
    ]
    for url in candidates:
        if url:
            return url
    return None


def is_enabled() -> bool:
    return _database_url() is not None


def _connect() -> psycopg.Connection:
    url = _database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return psycopg.connect(url, autocommit=True)


def ensure_schema() -> None:
    if not is_enabled():
        return

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                create table if not exists calc_logs (
                  id bigserial primary key,
                  num1 double precision not null,
                  num2 double precision not null,
                  result double precision not null,
                  ip text null,
                  user_agent text null,
                  created_at timestamptz not null default now()
                );
                """
            )


def insert_log(
    *,
    num1: float,
    num2: float,
    result: float,
    ip: Optional[str],
    user_agent: Optional[str],
) -> None:
    if not is_enabled():
        return

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into calc_logs (num1, num2, result, ip, user_agent)
                values (%s, %s, %s, %s, %s)
                """,
                (num1, num2, result, ip, user_agent),
            )


def fetch_logs(*, limit: int = 20) -> List[Dict[str, Any]]:
    if not is_enabled():
        return []

    limit = max(1, min(int(limit), 200))

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select id, num1, num2, result, ip, user_agent, created_at
                from calc_logs
                order by id desc
                limit %s
                """,
                (limit,),
            )
            rows: List[Tuple[Any, ...]] = cur.fetchall()

    out: List[Dict[str, Any]] = []
    for (id_, num1, num2, result, ip, user_agent, created_at) in rows:
        out.append(
            {
                "id": id_,
                "num1": float(num1),
                "num2": float(num2),
                "result": float(result),
                "ip": ip,
                "user_agent": user_agent,
                "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at),
            }
        )
    return out

