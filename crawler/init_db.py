# init_db.py
from imdbcrawler.spiders.ImdbCrawler import IMDBDatabase

def initialize_database():
    with IMDBDatabase() as db:
        db._create_table()

if __name__ == "__main__":
    initialize_database()
    print("Database initialized.")
