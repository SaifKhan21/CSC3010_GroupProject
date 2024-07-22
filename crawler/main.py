import random
import subprocess
import os
import time
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import speedtest
import requests

def is_valid_url(url, allowed_domain):
    """Check if the URL belongs to the allowed domain."""
    parsed_url = urlparse(url)
    return allowed_domain in parsed_url.netloc

def get_start_urls(size=5, root_url="https://www.imdb.com"):
    allowed_domain = urlparse(root_url).netloc
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    headers = {'User-Agent': user_agent}

    try:
        response = requests.get(root_url, headers=headers)
        print(f"Response code for {root_url}: {response.status_code}")
        if response.status_code != 200:
            print(f"Failed to access {root_url}, response code: {response.status_code}")
            return []
    except Exception as e:
        print(f"An error occurred while checking the root URL: {e}")
        return []

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f"user-agent={user_agent}")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(root_url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
    except Exception as e:
        print(f"An error occurred while getting the start URLs: {e}")
        driver.quit()
        return []

    urls = [urljoin(root_url, a['href']) for a in soup.find_all('a', href=True) if is_valid_url(urljoin(root_url, a['href']), allowed_domain)]

    if len(urls) == 0:
        print("No valid URLs found.")
        return []

    if size > len(urls):
        size = len(urls)
        print(f"Size is too large, setting it to {size}.")

    full_urls = random.sample(urls, size)
    print(f"Found {len(full_urls)} URLs.")
    return full_urls

def available_threads():
    print("Available threads: ", os.cpu_count())
    return os.cpu_count()

def perform_speed_test():
    try:
        st = speedtest.Speedtest()
        download_speed = st.download() / 1000000
        upload_speed = st.upload() / 1000000

        print("Download Speed: {:.2f} Mbps".format(download_speed))
        print("Upload Speed: {:.2f} Mbps".format(upload_speed))
    except Exception as e:
        print(f"An error occurred while performing the speed test: {e}")
        download_speed = 50
        upload_speed = 50
    return download_speed, upload_speed

def main():
    try:
        random.seed(42)

        subprocess.run(["python", "init_db.py"], check=True)
        print("Database initialized successfully.")

        processes = []
        #_,_ = perform_speed_test()
        start_urls = get_start_urls(int(available_threads()-5), "https://www.imdb.com")
        allowed_domain = 'www.imdb.com'

        for url in start_urls:
            cmd = ["python", "run_crawler.py", url, allowed_domain]
            processes.append(subprocess.Popen(cmd))

        for p in processes:
            p.wait()
            print(f"Process with start_url_index {processes.index(p)} completed.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running a subprocess: {e}")

if __name__ == "__main__":
    main()
