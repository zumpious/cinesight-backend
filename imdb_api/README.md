# imdb_api

This project was generated using fastapi_template.

## Poetry

This project uses poetry. It's a modern dependency management
tool.

To run the project use this set of commands:

```bash
poetry install
poetry run python -m imdb_api
```

## API

When the API is running the following endpoint can be feteched to get any overview over the exisiting API endpoints: 
- `/api/docs`

### API Endpoints

- `/api/movies?year=1980&top=10`: Fetch the top 10 movies of the year 1980.
- `/api/movies/{movie_id}`: Fetch details of a specific movie by its ID.
- `/api/movies/flops`: Fetch the count of flops and successes based on the given year and rating.
- `/api/plots/budgetrating`: Fetch a plot of budget vs rating.
- `/api/plots/directorsgender`: Fetch a plot of director gender distribution.
- `/api/plots/directorsgenderanimated`: Fetch an animated plot of director gender distribution over the years.
- `/api/plots/budgetboxofficeanimated`: Fetch an animated plot of budget vs box office.
- `/api/plots/ratingsovertime`: Fetch a plot of ratings over time.


# Data Handling

We are currently using a CSV file containing merged movie data that exceeds 2GB in size. This file is generated from the JSON files returned by the scraper and is not part of the GitHub repository. Please contact a developer for direct access.

We are actively working on a more efficient solution.