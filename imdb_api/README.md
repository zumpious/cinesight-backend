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

# Endpoints

`/api/movies?year=1980?top=10`

# Data Handling

We are currently using a CSV file containing merged movie data that exceeds 2GB in size. This file is generated from the JSON files returned by the scraper and is not part of the GitHub repository. Please contact a developer for direct access.

We are actively working on a more efficient solution.