import sqlite3

def initialize_database():
    # Initialize database with schema
    conn = sqlite3.connect('patents.db')
    cursor = conn.cursor()

    # Create tables
    cursor.executescript('''
    -- Patents table to store basic patent information
    CREATE TABLE IF NOT EXISTS patents (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        abstract TEXT,
        publication_date TEXT,
        inventor TEXT,
        filing_date TEXT,
        assignee TEXT,
        pdf_url TEXT
    );

    -- Highlights table for user annotations
    CREATE TABLE IF NOT EXISTS highlights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patent_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        text_content TEXT,
        page_number INTEGER,
        position_data TEXT,
        color TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patent_id) REFERENCES patents(id)
    );

    -- Annotations table for saving highlighted sentences
    CREATE TABLE IF NOT EXISTS annotations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        color TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Citations table to track patent relationships
    CREATE TABLE IF NOT EXISTS citations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        citing_patent_id TEXT NOT NULL,
        cited_patent_id TEXT NOT NULL,
        citation_type TEXT,
        FOREIGN KEY (citing_patent_id) REFERENCES patents(id),
        FOREIGN KEY (cited_patent_id) REFERENCES patents(id)
    );
    ''')

    # Add sample data
    cursor.execute('''
    INSERT OR IGNORE INTO patents (id, title, abstract, publication_date, inventor)
    VALUES (?, ?, ?, ?, ?)
    ''', (
        'US9123456',
        'Sample Patent Title',
        'This is a sample patent abstract for testing purposes',
        '2023-01-15',
        'John Inventor'
    ))

    conn.commit()
    conn.close()

    print("Database initialized with schema and sample data.")

if __name__ == '__main__':
    initialize_database()