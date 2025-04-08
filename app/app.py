from flask import Flask, request, redirect, render_template
from config.db import app

@app.route("/")
def index():
    return render_template("index.htl")

if __name__ == "__main__":
    app-run(debud=True, port=5000, host="0.0.0.0")