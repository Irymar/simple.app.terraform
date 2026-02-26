import os
import time
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "appdb"),
    "user": os.getenv("DB_USER", "appuser"),
    "password": os.getenv("DB_PASSWORD", "apppass"),
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def wait_for_db(max_retries=30, delay_seconds=2):
    for attempt in range(1, max_retries + 1):
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
            print("DB is ready")
            return
        except Exception as exc:
            print(f"DB not ready ({attempt}/{max_retries}): {exc}")
            time.sleep(delay_seconds)
    raise RuntimeError("Database is not reachable")


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
                """
            )
            cur.execute("SELECT COUNT(*) FROM notes;")
            count = cur.fetchone()[0]
            if count == 0:
                cur.execute(
                    "INSERT INTO notes (text, created_at) VALUES (%s, %s);",
                    ("Hello from simple app", datetime.utcnow()),
                )
        conn.commit()


app = Flask(__name__)
CORS(app)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/notes")
def list_notes():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, text, created_at FROM notes ORDER BY id DESC;")
            notes = cur.fetchall()
    return jsonify(notes)


@app.post("/api/notes")
def create_note():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO notes (text)
                VALUES (%s)
                RETURNING id, text, created_at;
                """,
                (text,),
            )
            saved = cur.fetchone()
        conn.commit()
    return jsonify(saved), 201


@app.put("/api/notes/<int:note_id>")
def update_note(note_id):
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                UPDATE notes
                SET text = %s
                WHERE id = %s
                RETURNING id, text, created_at;
                """,
                (text, note_id),
            )
            updated = cur.fetchone()
        conn.commit()

    if not updated:
        return jsonify({"error": "note not found"}), 404
    return jsonify(updated)


@app.delete("/api/notes/<int:note_id>")
def delete_note(note_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM notes WHERE id = %s RETURNING id;", (note_id,))
            deleted = cur.fetchone()
        conn.commit()

    if not deleted:
        return jsonify({"error": "note not found"}), 404
    return jsonify({"status": "deleted", "id": note_id})


# Backward-compatible alias with the old single-note endpoint.
@app.get("/api/note")
def get_note_alias():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, text, created_at FROM notes ORDER BY id DESC LIMIT 1;"
            )
            note = cur.fetchone()
    return jsonify(note)


# Backward-compatible alias with the old create endpoint.
@app.post("/api/note")
def create_note_alias():
    return create_note()


if __name__ == "__main__":
    wait_for_db()
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
