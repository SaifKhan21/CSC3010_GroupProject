import sqlite3


class IMDBDatabase:
    '''
    Class to interact with the SQLite database for storing crawled IMDb pages.
    The database schema includes a table called 'pages' with the following columns:
    - url: Text (Primary Key)
    - crawl_date: Text
    - content_type: Text
    - html: Text
    - html_hash: Text
    '''
    def __init__(self, db_name="imdb_crawler.db"):
        '''
        Initialize the database connection and cursor.
        :param db_name: Name of the SQLite database file.
        :type db_name: str
        :param conn: SQLite connection object.
        :type conn: sqlite3.Connection
        :param cursor: SQLite cursor object.
        :type cursor: sqlite3.Cursor
        '''
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        '''
        Create the 'pages' table if it does not exist.
        :return: The database object.
        :rtype: IMDBDatabase
        '''
        db_file = self.db_name
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._create_table()
        return self

    def _create_table(self):
        '''
        Create the 'pages' table if it does not exist.
        '''
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                url TEXT PRIMARY KEY,
                crawl_date TEXT,
                content_type TEXT,
                html TEXT,
                html_hash TEXT
            )
        ''')
        self.conn.commit()

    def get_all_data(self):
        '''
        Fetch all rows from the 'pages' table.
        :return: List of rows from the 'pages' table.
        :rtype: List[Tuple]
        '''
        self.cursor.execute('''
            SELECT * FROM pages
        ''')
        return self.cursor.fetchall()

    def save_page(self, url, crawl_date, content_type, html, html_hash):
        '''
        Save a page to the 'pages' table.
        :param url: URL of the page.
        :type url: str
        :param crawl_date: Date when the page was crawled.
        :type crawl_date: str
        :param content_type: Content type of the page.
        :type content_type: str
        :param html: HTML content of the page.
        :type html: str
        :param html_hash: Hash of the HTML content.
        :type html_hash: str
        '''
        self.cursor.execute('''
            INSERT OR IGNORE INTO pages (url, crawl_date, content_type, html, html_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (url, crawl_date, content_type, html, html_hash))
        self.conn.commit()

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()
