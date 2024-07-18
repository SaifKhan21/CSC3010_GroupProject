import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class IMDBDatabase:
    def __init__(self, db_name="imdb_crawler.db", similarity_threshold=0.9):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.html_vectorizer = TfidfVectorizer()
        self.similarity_threshold = similarity_threshold

    def __enter__(self):
        db_file = self.db_name
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._create_table()
        self.update_local_data_and_matrices()
        return self

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                url_hash TEXT PRIMARY KEY,
                url TEXT UNIQUE,
                date_time DATETIME,
                content_type TEXT,
                content_length INTEGER,
                title TEXT,
                html TEXT,
                html_hash TEXT UNIQUE,
                metadata TEXT
            )
        ''')
        self.conn.commit()

    def get_all_data(self):
        self.cursor.execute('''
            SELECT * FROM pages
        ''')
        return self.cursor.fetchall()

    def update_local_data_and_matrices(self):
        self.cursor.execute('SELECT html FROM pages')
        html_pages = [row[0] for row in self.cursor.fetchall()]
        if html_pages:
            self.html_tfidf_matrix = self.html_vectorizer.fit_transform(html_pages)
        else:
            self.html_tfidf_matrix = None

    def compute_cosine_similarity(self, new_html):
        if self.html_tfidf_matrix is not None:
            new_html_tfidf = self.html_vectorizer.transform([new_html])
            cosine_similarities = cosine_similarity(new_html_tfidf, self.html_tfidf_matrix)
            return cosine_similarities.max()
        else:
            return None

    def save_page(self, url_hash, url, date_time, content_type, content_length, title, html, html_hash, metadata):
        similarity = self.compute_cosine_similarity(html)
        if similarity is None or similarity < self.similarity_threshold:
            self.cursor.execute('''
                INSERT OR IGNORE INTO pages (url_hash, url, date_time, content_type, content_length, title, html, html_hash, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (url_hash, url, date_time, content_type, content_length, title, html, html_hash, metadata))
        else:
            self.cursor.execute('''
                UPDATE pages SET date_time = ?, content_type = ?, content_length = ?, title = ?, html = ?, html_hash = ?, metadata = ?
                WHERE url_hash = ?
            ''', (date_time, content_type, content_length, title, html, html_hash, metadata, url_hash))
        self.conn.commit()

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()
