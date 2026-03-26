from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

PUBLIC_DIR = Path(__file__).resolve().parents[1] / "public"


@app.get("/")
def home():
    return send_from_directory(PUBLIC_DIR, "index.html")


@app.get("/<path:path>")
def static_files(path: str):
    candidate = (PUBLIC_DIR / path).resolve()
    if PUBLIC_DIR in candidate.parents and candidate.is_file():
        return send_from_directory(PUBLIC_DIR, path)
    return send_from_directory(PUBLIC_DIR, "index.html")


@app.get("/api/hello")
def hello():
    return jsonify(message="Hello from Flask!")


@app.post("/api/add")
def add_numbers():
    data = request.get_json(silent=True) or {}
    num1 = float(data.get("num1", 0))
    num2 = float(data.get("num2", 0))
    return jsonify(result=num1 + num2)
