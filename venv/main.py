from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
import sqlite3
from models import RequestCreate, RequestResponse
from typing import List
from datetime import datetime
from contextlib import closing

app = FastAPI()

# Connexion à la base de données SQLite
DATABASE_FILE = "test.db"

# Fonction pour créer la table si elle n'existe pas
def create_table():
    with closing(sqlite3.connect(DATABASE_FILE)) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY,
            author INTEGER,
            status TEXT DEFAULT 'pending',
            resolved_by INTEGER,
            request_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            vacation_start_date TIMESTAMP,
            vacation_end_date TIMESTAMP
        )
        """)
        conn.commit()

create_table()

# Fonction pour obtenir un curseur à la base de données
def get_db():
    with closing(sqlite3.connect(DATABASE_FILE)) as conn:
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            conn.close()

# Routes pour les travailleurs
@app.post('/workers/new_request', response_model=RequestResponse)
def make_new_request(request_data: RequestCreate, db: sqlite3.Cursor = Depends(get_db)):
    try:
        print("Received request data:", request_data.dict())

        insert_query = """
        INSERT INTO requests (author, vacation_start_date, vacation_end_date)
        VALUES (?, ?, ?)
        """
        db.execute(insert_query, (request_data.author, request_data.vacation_start_date, request_data.vacation_end_date))
        db.connection.commit()

        last_inserted_id = db.lastrowid
        print("Last inserted ID:", last_inserted_id)

        select_query = "SELECT * FROM requests WHERE id = ?"
        db.execute(select_query, (last_inserted_id,))
        result = db.fetchone()
        print("Result:", result)

        if result:
            return dict(zip([desc[0] for desc in db.description], result))
        else:
            raise HTTPException(status_code=404, detail="Request not found")

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Routes pour récupérer les demandes des travailleurs
@app.get('/workers/requests', response_model=List[RequestResponse])
def get_worker_requests(worker_id: int, status: str = None, db: sqlite3.Cursor = Depends(get_db)):
    try:
        print("Received request to get worker requests. Worker ID:", worker_id, "Status:", status)

        select_query = "SELECT * FROM requests WHERE author = ?"
        params = [worker_id]

        if status:
            select_query += " AND status = ?"
            params.append(status)

        db.execute(select_query, tuple(params))
        results = db.fetchall()

        print("Results:", results)

        return [dict(zip([desc[0] for desc in db.description], result)) for result in results] if results else []

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
