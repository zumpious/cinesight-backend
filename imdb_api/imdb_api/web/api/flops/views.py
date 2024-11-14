import json
from os.path import dirname, join

import pandas as pd
from fastapi import APIRouter
from starlette.responses import JSONResponse

from imdb_api.web.api import movies_df

router = APIRouter()


@router.get("/")
async def count_flops(year: int = None, rating: float = None):
    filtered_movies = movies_df

    if year is not None:
        filtered_movies = filtered_movies.query("release_year == @year")

    if rating is not None:
        filtered_movies = filtered_movies.query("@rating <= rating <= @rating + 0.9")

    filtered_movies["release"] = filtered_movies["release"].astype(str)

    flops = 0
    success = 0

    for index, movie in filtered_movies.iterrows():
        difference = movie['boxoffice'] - movie['budget']

        if difference > 0:
            success += 1
        else:
            flops += 1

    data = {'flops': flops,
            'success': success}

    return JSONResponse(data)
