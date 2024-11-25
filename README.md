# CineSight Backend

This backend consists of two main components: `imdb_api/` and `scraper/`.

## Scraper

The scraper is currently not usable due to IMDB having changed their page structure. However, in the `scraper/results` directory, there are already fetched JSON results from the scraper. These consist of the top 100 movies of each year, storing information such as the IMDB link, title, rating, the user comments and many more. As these files are very large, GitHub LFS was used in this project. To ensure the API works as intended, follow these steps:

1. Install Git LFS locally:
   ```sh
   git lfs install
    ```
2.  Fetch the LFS files by running:
    ```sh 
    git lfs pull
    ```
## API

The API is working and the top 100 movies and their user comments from 1980 - 2022 can be fetched. For more details on setting up and running the API, please refer to this [README](/imdb_api/README.md). 