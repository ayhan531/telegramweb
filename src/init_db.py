import os
import sqlite3

def init_db():
    """Create the SQLite database and required tables if they don't exist.
    This function is idempotent – it can be called on every start-up.
    """
    # Ensure the data directory exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    db_path = os.path.join(data_dir, "database.sqlite")
    # Connect (this will create the file if missing)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS alarms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                target_price REAL NOT NULL,
                condition TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized at", os.path.abspath(os.path.join(data_dir, "database.sqlite")))
