from fastapi import FastAPI
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles

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


# 로컬 미리보기용: `/`에서 public/을 서빙
# (로컬에서만 편하려고 추가한 것이고, Vercel 프로덕션에선 /api/*만 이 함수로 들어옴)
app.mount("/", StaticFiles(directory="public", html=True), name="public")
