import sqlite3
import os
from pathlib import Path

DB_PATH = os.getenv("SQLITE_DB_PATH", "./data/meeting_memory.db")

def get_db_connection(db_path: str = None) -> sqlite3.Connection:
    target_path = db_path or DB_PATH
    Path(os.path.dirname(target_path)).mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = None):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS meetings (
            meeting_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            project TEXT DEFAULT 'General',
            audio_path TEXT,
            transcript_path TEXT,
            summary TEXT,
            topics TEXT,
            risks TEXT,
            open_questions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT,
            FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS decisions (
            decision_id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            title TEXT NOT NULL,
            decision TEXT NOT NULL,
            timestamp TEXT DEFAULT '00:00:00',
            confidence REAL DEFAULT 0.90,
            status TEXT DEFAULT 'Approved',
            is_explicit INTEGER DEFAULT 1,
            FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS decision_reasons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            FOREIGN KEY (decision_id) REFERENCES decisions (decision_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS decision_alternatives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision_id TEXT NOT NULL,
            alternative TEXT NOT NULL,
            FOREIGN KEY (decision_id) REFERENCES decisions (decision_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS decision_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision_id TEXT NOT NULL,
            participant TEXT NOT NULL,
            FOREIGN KEY (decision_id) REFERENCES decisions (decision_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS actions (
            action_id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            description TEXT NOT NULL,
            owner TEXT DEFAULT 'Unassigned',
            due_date TEXT,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Pending',
            timestamp TEXT DEFAULT '00:00:00',
            FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS transcript_chunks (
            chunk_id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            speaker TEXT,
            start_time TEXT,
            end_time TEXT,
            text TEXT NOT NULL,
            FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()
