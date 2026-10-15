import os
import time

import pymysql
from flask import Flask, redirect, render_template, request

app = Flask(__name__)


def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "mysql"),
        user=os.getenv("MYSQL_USER", "appuser"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DB", "messages_db"),
        cursorclass=pymysql.cursors.DictCursor,
    )


def init_db():
    for attempt in range(10):
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        message VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            connection.commit()
            connection.close()
            print("Database table is ready.")
            return
        except pymysql.MySQLError:
            if attempt == 9:
                raise
            time.sleep(3)


@app.route("/", methods=["GET"])
def home():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, message, created_at FROM messages ORDER BY id DESC"
            )
            messages = cursor.fetchall()
        return render_template("index.html", messages=messages)
    finally:
        connection.close()


@app.route("/submit", methods=["POST"])
def submit():
    message = request.form.get("message", "").strip()

    if message:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO messages (message) VALUES (%s)",
                    (message,),
                )
            connection.commit()
        finally:
            connection.close()

    return redirect("/")


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200


init_db()
