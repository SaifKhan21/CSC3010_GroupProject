# main.py
import subprocess

def main():
    try:
        # Initialize the database
        subprocess.run(["python", "init_db.py"], check=True)
        print("Database initialized successfully.")

        # Run the crawler with different start_url_index values, in parallel
        processes = []
        for i in range(5):
            cmd = ["python", "run_crawler.py", str(i)]
            processes.append(subprocess.Popen(cmd))

        # Wait for all processes to complete
        for p in processes:
            p.wait()
            print(f"Process with start_url_index {processes.index(p)} completed.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running a subprocess: {e}")

if __name__ == "__main__":
    main()
