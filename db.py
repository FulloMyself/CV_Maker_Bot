import sqlite3

DATABASE_PATH = 'eme_cv_bot.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            professional_summary TEXT,
            skills TEXT,
            languages TEXT,
            doc_id_path TEXT,
            doc_proof_path TEXT,
            cv_path TEXT,
            submission_date TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    # Work experience table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_experience (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            job_title TEXT,
            company TEXT,
            start_date TEXT,
            end_date TEXT,
            responsibilities TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Education table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS education (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            degree TEXT,
            institution TEXT,
            graduation_year TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Certifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            cert_name TEXT,
            issuer TEXT,
            year TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")