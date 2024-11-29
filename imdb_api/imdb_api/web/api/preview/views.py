import pandas as pd
from fastapi import APIRouter
from starlette.responses import JSONResponse

from imdb_api.web.api import movies_df

router = APIRouter()

# This is added bc currently we only fetched movies till 2022 - will be updated in the future
LATEST_YEAR = 2022

@router.get("/")
async def get_preview():
    filtered_movies = movies_df

    filtered_movies = filtered_movies.query("release_year == @LATEST_YEAR")
    
    # Convert to datetime, sort, and get top 10
    filtered_movies['release'] = pd.to_datetime(filtered_movies['release'])
    filtered_movies = filtered_movies.sort_values('release', ascending=False).head(10)
    
    # Convert back to string for JSON
    filtered_movies["release"] = filtered_movies["release"].astype(str)
    
    return_list = filtered_movies[
        ["id", "title", "rating", "cover", "release"]].to_dict(orient="records")

    return JSONResponse(return_list)