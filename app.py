from __future__ import annotations

import re
import sqlite3
import time
from pathlib import Path

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TRAINING_DB = DATA_DIR / "training.db"
MAX_ROWS = 100

app = Flask(__name__)


EQUIPOS = [
    (1, "PC-SOP-01", "Notebook", "Operativo", "Soporte TI", "Felipe"),
    (2, "PC-RRHH-02", "Escritorio", "En mantenimiento", "Recursos Humanos", "Andrea"),
    (3, "SW-CORE-01", "Switch", "Operativo", "Infraestructura", None),
    (4, "NB-VTA-04", "Notebook", "Fuera de servicio", "Ventas", "Carlos"),
    (5, "SRV-ARCH-01", "Servidor", "Operativo", "Infraestructura", None),
]


def initialize_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(TRAINING_DB) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS equipos (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL UNIQUE,
                tipo TEXT NOT NULL,
                estado TEXT NOT NULL,
                departamento TEXT NOT NULL,
                usuario_asignado TEXT
            );
            """
        )
        count = connection.execute("SELECT COUNT(*) FROM equipos").fetchone()[0]
        if count == 0:
            connection.executemany(
                """
                INSERT INTO equipos
                    (id, nombre, tipo, estado, departamento, usuario_asignado)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                EQUIPOS,
            )


def query_is_safe(sql: str) -> tuple[bool, str]:
    normalized = sql.strip()
    if not normalized:
        return False, "Escribe una consulta antes de ejecutar."
    if len(normalized) > 2_000:
        return False, "La consulta supera el máximo permitido para este laboratorio."
    without_final_semicolon = normalized[:-1].strip() if normalized.endswith(";") else normalized
    if ";" in without_final_semicolon:
        return False, "Ejecuta una sola consulta a la vez."
    if not re.match(r"^(SELECT|WITH)\b", without_final_semicolon, flags=re.IGNORECASE):
        return False, "En esta etapa solo se permiten consultas SELECT."
    return True, ""


def readonly_authorizer(action, _arg1, _arg2, _database, _trigger):
    allowed = {
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_READ,
        sqlite3.SQLITE_FUNCTION,
        sqlite3.SQLITE_RECURSIVE,
    }
    return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY


def normalized_rows(columns: list[str], rows: list[sqlite3.Row]) -> list[list[object]]:
    return [[row[column] for column in columns] for row in rows]


def evaluate_lesson(lesson_id: int, columns: list[str], rows: list[sqlite3.Row]) -> dict:
    actual_rows = normalized_rows(columns, rows)

    if lesson_id == 2:
        expected_columns = ["nombre", "tipo", "estado"]
        expected_rows = [
            ["NB-VTA-04", "Notebook", "Fuera de servicio"],
            ["PC-RRHH-02", "Escritorio", "En mantenimiento"],
            ["PC-SOP-01", "Notebook", "Operativo"],
            ["SRV-ARCH-01", "Servidor", "Operativo"],
            ["SW-CORE-01", "Switch", "Operativo"],
        ]
        if columns != expected_columns:
            return {"passed": False, "message": "La consulta funciona, pero revisa las tres columnas solicitadas y su orden."}
        if actual_rows == expected_rows:
            return {"passed": True, "message": "¡Correcto! Mostraste las columnas solicitadas y ordenaste los equipos por nombre de A a Z."}
        return {"passed": False, "message": "Las columnas son correctas. Ahora ordena las filas alfabéticamente por nombre usando ORDER BY."}

    expected_columns = ["nombre", "estado"]
    expected_rows = [["NB-VTA-04", "Fuera de servicio"]]
    if columns == expected_columns and actual_rows == expected_rows:
        return {"passed": True, "message": "¡Correcto! Seleccionaste las columnas solicitadas y filtraste el equipo fuera de servicio."}
    if columns != expected_columns:
        return {"passed": False, "message": "La consulta funciona, pero revisa cuáles son exactamente las dos columnas solicitadas."}
    return {"passed": False, "message": "Las columnas son correctas. Ahora revisa el filtro aplicado sobre la columna estado."}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(status="ok", service="fenix-sql-lab", version="0.2.0")


@app.get("/api/schema")
def schema():
    with sqlite3.connect(TRAINING_DB) as connection:
        connection.row_factory = sqlite3.Row
        columns = connection.execute("PRAGMA table_info(equipos)").fetchall()
        preview = connection.execute("SELECT * FROM equipos ORDER BY id").fetchall()
    return jsonify(
        table="equipos",
        columns=[{"name": row["name"], "type": row["type"]} for row in columns],
        rows=[dict(row) for row in preview],
    )


@app.post("/api/query")
def execute_query():
    payload = request.get_json(silent=True) or {}
    sql = str(payload.get("sql", ""))
    try:
        lesson_id = int(payload.get("lesson_id", 1))
    except (TypeError, ValueError):
        lesson_id = 1
    if lesson_id not in {1, 2}:
        return jsonify(ok=False, error="La lección seleccionada no existe."), 400

    safe, error = query_is_safe(sql)
    if not safe:
        return jsonify(ok=False, error=error), 400

    started = time.perf_counter()
    try:
        connection = sqlite3.connect(f"file:{TRAINING_DB}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        connection.set_authorizer(readonly_authorizer)
        connection.set_progress_handler(lambda: 1 if time.perf_counter() - started > 1 else 0, 1_000)
        cursor = connection.execute(sql)
        columns = [description[0] for description in cursor.description or []]
        rows = cursor.fetchmany(MAX_ROWS + 1)
        truncated = len(rows) > MAX_ROWS
        rows = rows[:MAX_ROWS]
        evaluation = evaluate_lesson(lesson_id, columns, rows)
        return jsonify(
            ok=True,
            columns=columns,
            rows=normalized_rows(columns, rows),
            row_count=len(rows),
            truncated=truncated,
            elapsed_ms=round((time.perf_counter() - started) * 1_000, 2),
            evaluation=evaluation,
        )
    except sqlite3.Error as exc:
        return jsonify(ok=False, error=f"SQLite: {exc}"), 400
    finally:
        if "connection" in locals():
            connection.close()


initialize_database()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5037, debug=False)
