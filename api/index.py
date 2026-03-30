from fastapi import FastAPI
from fastapi import Request
from pydantic import BaseModel
from starlette.responses import Response
import json

app = FastAPI()

from . import db

db.ensure_schema()


class Numbers(BaseModel):
    num1: float
    num2: float


@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI!", "db_enabled": db.is_enabled()}


@app.post("/api/add")
async def add_numbers(data: Numbers, request: Request):
    result = data.num1 + data.num2

    forwarded_for = request.headers.get("x-forwarded-for")
    ip = (forwarded_for.split(",")[0].strip() if forwarded_for else None) or (
        request.client.host if request.client else None
    )
    user_agent = request.headers.get("user-agent")

    try:
        db.insert_log(
            num1=data.num1,
            num2=data.num2,
            result=result,
            ip=ip,
            user_agent=user_agent,
        )
    except Exception:
        pass

    return {"result": result, "db_enabled": db.is_enabled()}


@app.get("/api/logs")
async def get_logs(limit: int = 20):
    return {"db_enabled": db.is_enabled(), "logs": db.fetch_logs(limit=limit)}


# For assignment: expose raw JSON logs at /log (via vercel route)
@app.get("/api/log")
async def get_raw_log(limit: int = 50):
    rows = db.fetch_logs(limit=limit)
    out = []
    for r in rows:
        out.append(
            {
                "id": r["id"],
                "ts": r["created_at"],
                "a": r["num1"],
                "b": r["num2"],
                "op": "add",
                "result": r["result"],
                "error": None,
            }
        )
    # JSON Lines (NDJSON): one JSON object per line
    content = "\n".join(json.dumps(item, ensure_ascii=False) for item in out) + ("\n" if out else "")
    # Use text/plain so browsers render instead of downloading.
    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": "inline"},
    )


@app.get("/log")
async def get_raw_log_root(limit: int = 50):
    return await get_raw_log(limit=limit)
