from flask import Flask, jsonify, request

app = Flask(__name__)


@app.get("/api/hello")
def hello():
    return jsonify(message="Hello from Flask!")


@app.post("/api/add")
def add_numbers():
    data = request.get_json(silent=True) or {}
    num1 = float(data.get("num1", 0))
    num2 = float(data.get("num2", 0))
    return jsonify(result=num1 + num2)
