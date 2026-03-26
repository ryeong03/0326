from fastapi import FastAPI
from pydantic import BaseModel

try:
    from mangum import Mangum
except Exception:  # pragma: no cover
    Mangum = None


app = FastAPI()


class Numbers(BaseModel):
    num1: float
    num2: float


@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI!"}


@app.post("/api/add")
async def add_numbers(data: Numbers):
    return {"result": data.num1 + data.num2}


handler = Mangum(app) if Mangum else app
