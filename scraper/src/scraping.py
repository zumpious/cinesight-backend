import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from itertools import chain

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

from drivers import get_webdriver, close_webdriver
from src.params import MAX_NUMBER_MOVIES, MAX_NUMBER_REVIEWS
from utils import convert_to_minutes


def extract_ratings(movie_link):
    driver = get_webdriver()

    driver.get(movie_link + "/ratings")
    ratings = {}

    for i in range(0, 10):
        temp = driver.find_element(By.CSS_SELECTOR, f"#chart-bar-1-labels-{i} > tspan:nth-child(1)").text
        temp = temp.split('%')[1].replace('(', '').replace(')', '').replace('.', '').strip()
        if 'Mio' in temp:
            temp = float(temp.split('Mio')[0].replace(',', '.').strip()) * 1000000
        ratings[10 - i] = int(temp)

    return ratings


def extract_reviews(movie_link, max_reviews):
    driver = get_webdriver()
    wait = WebDriverWait(driver, 10)  # 10 Sekunden Timeout

    reviews = []
    # Open Reviews page
    driver.get(movie_link + "/reviews")

    review_counter = 0

    while review_counter < max_reviews:
        all_reviews = driver.find_elements(By.CLASS_NAME, "lister-item")

        for review in all_reviews[review_counter:]:
            review_counter += 1

            # Skippe Reviews ohne Bewertung
            if not review.find_elements(By.CSS_SELECTOR, ".rating-other-user-rating span"):
                continue

            review_rating = review.find_element(By.CSS_SELECTOR, ".rating-other-user-rating span").text
            review_text = review.find_element(By.CSS_SELECTOR, ".text.show-more__control")
            review_text = review_text.get_attribute('innerHTML')
            review_text = " ".join(review_text.replace("<br>", "\n").split("\n"))  # Make review a one-liner

            reviews.append(
                {"rating": review_rating,
                 "text": review_text}
            )

            if review_counter >= max_reviews:
                break

        try:  # Irgendwann gibt es keinen load_more button mehr
            load_more_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".ipl-load-more__button")))
            load_more_button.click()
        except TimeoutException:
            break

    return reviews


def scrape_movie(movie_link):
    driver = get_webdriver()

    movie = {}

    # Open Details page
    driver.get(movie_link)

    json_element = driver.find_element(By.XPATH, "//script[@type='application/ld+json']").get_attribute("innerHTML")
    data = json.loads(json_element)

    movie["link"] = movie_link
    movie["title"] = data.get("alternateName", data["name"])
    movie["cover"] = data["image"]
    movie["age"] = data.get("contentRating", None)
    movie["release"] = data.get("datePublished", None)
    movie["rating"] = data["aggregateRating"]["ratingValue"]
    movie["actors"] = [actor["name"] for actor in data["actor"]]
    movie["directors"] = [director["name"] for director in data["director"]]
    movie["runtime"] = convert_to_minutes(data["duration"])
    movie["genres"] = data["genre"]

    # Extract Origin Country
    movie_origin = driver.find_element(By.XPATH, "//li[@data-testid='title-details-origin']")
    movie_origin = movie_origin.find_element(By.CSS_SELECTOR, ".ipc-metadata-list-item__list-content-item").text
    movie["origin"] = movie_origin

    # Extract Budget
    selector = "//li[@data-testid='title-boxoffice-budget']"
    if driver.find_elements(By.XPATH, selector):
        movie_budget = driver.find_element(By.XPATH, selector)
        movie_budget = movie_budget.find_element(By.CSS_SELECTOR, ".ipc-metadata-list-item__list-content-item").text
        if "$" not in movie_budget:
            # No $ sign in budget. Foreign currency. Can't handle that
            movie_budget = None
        else:
            movie_budget = int(movie_budget.split(" ")[0].replace('.', ''))
    else:
        movie_budget = None

    movie["budget"] = movie_budget

    # Extract Box Office
    selector = "//li[@data-testid='title-boxoffice-cumulativeworldwidegross']"
    if driver.find_elements(By.XPATH, selector):
        movie_boxoffice = driver.find_element(By.XPATH, selector)
        movie_boxoffice = movie_boxoffice.find_element(By.CSS_SELECTOR, ".ipc-metadata-list-item__list-content-item").text
        movie_boxoffice = int(movie_boxoffice.split(" ")[0].replace('.', ''))
    else:
        movie_boxoffice = None
    movie["boxoffice"] = movie_boxoffice

    # Extract Ratings
    ratings = extract_ratings(movie_link)
    movie["ratings"] = ratings

    # Extract Reviews
    reviews = extract_reviews(movie_link, MAX_NUMBER_REVIEWS)
    movie["reviews"] = reviews

    close_webdriver()

    return movie


def scrape_imdb_list(url: str):
    driver = get_webdriver()

    driver.get(url)

    list_name = driver.find_element(By.CSS_SELECTOR, "h1.header").text

    if os.path.exists(f"../links/{list_name}"):
        print("Found list in cache!")
        with open(f'../links/{list_name}', 'r') as f:
            movie_links = f.read().splitlines()

        return movie_links

    total = driver.find_element(By.CSS_SELECTOR, "div.desc span").text
    total = int(total.split("of ")[1].split(" titles.")[0].strip().replace(',', ''))

    page_links = []

    for i in range(0, total, 100):
        page_links.append(url + f"&start={i+1}")

    close_webdriver()

    def scrape_subpage_wrapper(url):
        driver = get_webdriver()
        driver.get(url)

        # Extract links to individual movies
        movie_elements = driver.find_elements(By.CLASS_NAME, "lister-item")

        temp_links = []

        for movie_element in movie_elements:
            title_element = movie_element.find_element(By.CSS_SELECTOR, ".lister-item-header a")
            movie_link = title_element.get_attribute("href").rsplit('/', 1)[0]
            temp_links.append(movie_link)

        close_webdriver()

        return temp_links

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(tqdm(executor.map(scrape_subpage_wrapper, page_links), total=len(page_links)))

    movie_links = list(chain(*results))

    close_webdriver()

    with open(f'../links/{list_name}', 'w') as f:
        for link in movie_links:
            f.write(f"{link}\n")

    return movie_links
