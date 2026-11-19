
import os
import logging
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from mssql_python import connect

app = Flask(__name__, static_folder=None)
BASE = Path(__file__).resolve().parent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------------
# AZURE SQL CONNECTION
# -----------------------------------

def get_db_connection():
    server = os.environ["SQL_SERVER"]
    database = os.environ["SQL_DATABASE"]

    connection_string = (
        f"Server=tcp:{server},1433;"
        f"Database={database};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Authentication=ActiveDirectoryMSI;"
    )

    return connect(connection_string, timeout=30)


def record_to_dict(row):
    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "notes": row[3] or "",
        "createdAt": (
            row[4].isoformat()
            if row[4] is not None else None
        ),
    }


def validate_record(payload):
    if not isinstance(payload, dict):
        return None, "Expected a JSON object"

    name = payload.get("name", "")
    email = payload.get("email", "")
    notes = payload.get("notes", "")

    if not all(
        isinstance(value, str)
        for value in (name, email, notes)
    ):
        return None, "All fields must be strings"

    name = name.strip()
    email = email.strip()
    notes = notes.strip()

    if not name or len(name) > 100:
        return None, "Name must contain 1-100 characters"

    if (
        not email
        or "@" not in email
        or len(email) > 200
    ):
        return None, "Please provide a valid email"

    if len(notes) > 500:
        return None, "Notes cannot exceed 500 characters"

    return {
        "name": name,
        "email": email,
        "notes": notes,
    }, None


# -----------------------------------
# FRONTEND
# -----------------------------------

@app.get("/")
def home():
    return send_from_directory(BASE, "index.html")


@app.get("/styles.css")
def css():
    return send_from_directory(BASE, "styles.css")


@app.get("/script.js")
def js():
    return send_from_directory(BASE, "script.js")



# -----------------------------------
# HEALTH CHECK
# -----------------------------------

@app.get("/api/health")
def health():
    return jsonify(
        status="ok",
        framework="flask"
    )


@app.get("/api/db-health")
def database_health():
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1")
        cursor.fetchone()

        return jsonify(
            status="ok",
            database="connected"
        )

    except Exception as exc:
        app.logger.error(
            "Database connection failed: %s: %s",
            type(exc).__name__,
            str(exc)
        )

        app.logger.exception(
            "SQL connection traceback"
        )

        return jsonify(
            database="unavailable",
            status="error"
        ), 503

    finally:
        if conn is not None:
            conn.close()



# -----------------------------------
# GET ALL RECORDS
# -----------------------------------

@app.get("/api/records")
def list_records():
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                Id,
                Name,
                Email,
                Notes,
                CreatedAt
            FROM dbo.TestRecords
            ORDER BY Id DESC
        """)

        records = [
            record_to_dict(row)
            for row in cursor.fetchall()
        ]

        return jsonify(records)

    except Exception:
        logger.exception("Failed to retrieve records")
        return jsonify(
            error="Unable to retrieve records"
        ), 500

    finally:
        if conn is not None:
            conn.close()


# -----------------------------------
# GET ONE RECORD
# -----------------------------------

@app.get("/api/records/<int:record_id>")
def get_record(record_id):
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                Id, Name, Email, Notes, CreatedAt
            FROM dbo.TestRecords
            WHERE Id = ?
        """, (record_id,))

        row = cursor.fetchone()

        if row is None:
            return jsonify(
                error="Record not found"
            ), 404

        return jsonify(record_to_dict(row))

    except Exception:
        logger.exception("Failed to retrieve record")
        return jsonify(
            error="Unable to retrieve record"
        ), 500

    finally:
        if conn is not None:
            conn.close()


# -----------------------------------
# CREATE RECORD
# -----------------------------------

@app.post("/api/records")
def create_record():
    data, error = validate_record(
        request.get_json(silent=True)
    )

    if error:
        return jsonify(error=error), 400

    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO dbo.TestRecords
                (Name, Email, Notes)
            OUTPUT
                INSERTED.Id,
                INSERTED.Name,
                INSERTED.Email,
                INSERTED.Notes,
                INSERTED.CreatedAt
            VALUES (?, ?, ?)
        """, (
            data["name"],
            data["email"],
            data["notes"]
        ))

        row = cursor.fetchone()
        result = record_to_dict(row)

        conn.commit()

        return jsonify(result), 201

    except Exception:
        if conn is not None:
            conn.rollback()

        logger.exception("Failed to create record")
        return jsonify(
            error="Unable to create record"
        ), 500

    finally:
        if conn is not None:
            conn.close()


# -----------------------------------
# UPDATE RECORD
# -----------------------------------

@app.put("/api/records/<int:record_id>")
def update_record(record_id):
    data, error = validate_record(
        request.get_json(silent=True)
    )

    if error:
        return jsonify(error=error), 400

    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE dbo.TestRecords
            SET
                Name = ?,
                Email = ?,
                Notes = ?
            OUTPUT
                INSERTED.Id,
                INSERTED.Name,
                INSERTED.Email,
                INSERTED.Notes,
                INSERTED.CreatedAt
            WHERE Id = ?
        """, (
            data["name"],
            data["email"],
            data["notes"],
            record_id
        ))

        row = cursor.fetchone()

        if row is None:
            conn.rollback()
            return jsonify(
                error="Record not found"
            ), 404

        result = record_to_dict(row)
        conn.commit()

        return jsonify(result)

    except Exception:
        if conn is not None:
            conn.rollback()

        logger.exception("Failed to update record")
        return jsonify(
            error="Unable to update record"
        ), 500

    finally:
        if conn is not None:
            conn.close()


# -----------------------------------
# DELETE RECORD
# -----------------------------------

@app.delete("/api/records/<int:record_id>")
def delete_record(record_id):
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM dbo.TestRecords
            OUTPUT DELETED.Id
            WHERE Id = ?
        """, (record_id,))

        deleted = cursor.fetchone()

        if deleted is None:
            conn.rollback()
            return jsonify(
                error="Record not found"
            ), 404

        conn.commit()

        return jsonify(
            message="Record deleted",
            id=record_id
        )

    except Exception:
        if conn is not None:
            conn.rollback()

        logger.exception("Failed to delete record")
        return jsonify(
            error="Unable to delete record"
        ), 500

    finally:
        if conn is not None:
            conn.close()


# -----------------------------------
# APPLICATION STARTUP
# -----------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        debug=False
    )
