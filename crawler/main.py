# main.py
import subprocess

def main():
    # Initialize the database
    subprocess.run(["python", "init_db.py"])
    
    # Run the crawler
    subprocess.run(["python", "run_crawler.py"])

if __name__ == "__main__":
    main()
