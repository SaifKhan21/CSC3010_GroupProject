import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def scrape_movies_by_url(url, headers):
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        movie_data = []

        for box in soup.find_all('div', class_='ipc-metadata-list-summary-item__tc'):
            title_element = box.find('h3', class_='ipc-title__text')
            rating_element = box.find('span', class_='ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating')
            summary_element = box.find('div', class_='ipc-html-content-inner-div')

            title_text = title_element.text.strip() if title_element else "N/A"
            if title_text and title_text[0].isdigit():
                title_text = title_text.split('. ', 1)[-1]


            movie = {
                'Title': title_text,
                'Rating': rating_element['aria-label'] if rating_element else "N/A",
                'Summary': summary_element.text.strip() if summary_element else "N/A"
            }

            movie_data.append(movie)
        if movie_data:
            return movie_data
    elif response.status_code == 403:
        print("Access denied to the website : 403 Forbidden")
    else:
        print(f"Error: Status code {response.status_code}")

    return None


def main():
    url = "https://www.imdb.com/search/title/?genres=action"
    movie_data = scrape_movies_by_url(url, headers)

    if movie_data:
        movie_df = pd.DataFrame(movie_data)
        movie_df.to_csv('movie.csv', index=False)

        print(movie_df.to_string(index=False))

    else:
        print("Failed to fetch data")


if __name__ == '__main__':
    main()
