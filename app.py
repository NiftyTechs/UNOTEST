"""Simple Flask demo for Azure App Service.

Records are stored in process memory and are intentionally NON-PERSISTENT.
Do not use this demo for real user information or sensitive records.
"""
from itertools import count
from pathlib import Path
from threading import Lock
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder=None)
BASE = Path(__file__).parent
records = []
ids = count(1)
lock = Lock()

@app.get('/')
def home():
    return send_from_directory(BASE, 'index.html')

@app.get('/styles.css')
def css():
    return send_from_directory(BASE, 'styles.css')

@app.get('/script.js')
def js():
    return send_from_directory(BASE, 'script.js')

@app.get('/api/health')
def health():
    return jsonify(status='ok', framework='flask')

@app.get('/api/records')
def list_records():
    with lock:
        return jsonify(list(records))

@app.post('/api/records')
def create_record():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error='Expected JSON object'), 400
    name = payload.get('name', '')
    email = payload.get('email', '')
    notes = payload.get('notes', '')
    if not all(isinstance(v, str) for v in (name, email, notes)):
        return jsonify(error='All fields must be strings'), 400
    name, email, notes = name.strip(), email.strip(), notes.strip()
    if not name or len(name) > 100 or not email or '@' not in email or len(email) > 200 or len(notes) > 300:
        return jsonify(error='Please provide a valid name and email'), 400
    with lock:
        rec = dict(id=next(ids), name=name, email=email, notes=notes)
        records.append(rec)
    return jsonify(rec), 201

@app.delete('/api/records/<int:record_id>')
def delete_record(record_id):
    with lock:
        for i, record in enumerate(records):
            if record['id'] == record_id:
                records.pop(i)
                return jsonify(message='Record deleted')
    return jsonify(error='Record not found'), 404

if __name__ == '__main__':
    app.run(debug=False)
