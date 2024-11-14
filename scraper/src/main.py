import json
import locale
import logging
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from pprint import pprint

from src.drivers import close_webdriver
from src.params import MAX_NUMBER_MOVIES
from src.scraping import extract_reviews, scrape_imdb_list, scrape_movie

# For german names of months
locale.setlocale(category=locale.LC_ALL, locale="German")


def scrape_movie_wrapper(movie_link):
    try:
        movie = scrape_movie(movie_link)
        return movie
    except Exception as e:
        close_webdriver()
        logging.exception(f"Skipped {movie_link}")
        print(e)


def main():
    for year in range(1980, 2023):
        url = f"https://www.imdb.com/search/title/?title_type=feature&year={year}-01-01,{year}-12-31&view=simple&count=100"
        links = scrape_imdb_list(url)
        links = links[:MAX_NUMBER_MOVIES] if MAX_NUMBER_MOVIES else links

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(tqdm(executor.map(scrape_movie_wrapper, links), total=len(links)))

        movies = [movie for movie in results if movie is not None]

        json_data = json.dumps(movies, indent=4)

        # In Datei schreiben
        with open(f"../results/top{len(links)}_{year}.json", "w") as file:
            file.write(json_data)


if __name__ == '__main__':
    main()

    #movie = scrape_movie("https://www.imdb.com/title/tt0119472")
    #pprint(movie)
