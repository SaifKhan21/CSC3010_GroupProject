import os
import sqlite3

class IMDBDatabase:
    def __init__(self, db_name="imdb_crawler.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        db_file = os.path.join('imdbcrawler', self.db_name)
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._create_table()
        return self

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                crawl_date TEXT,
                content_type TEXT,
                html TEXT,
                html_hash TEXT
            )
        ''')
        self.conn.commit()

    def save_page(self, url, crawl_date, content_type, html, html_hash):
        self.cursor.execute('''
            INSERT OR IGNORE INTO pages (url, crawl_date, content_type, html, html_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (url, crawl_date, content_type, html, html_hash))
        self.conn.commit()

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()
