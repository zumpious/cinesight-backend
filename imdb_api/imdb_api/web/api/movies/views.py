import json
from os.path import dirname, join

import pandas as pd
from fastapi import APIRouter
from starlette.responses import JSONResponse

from imdb_api.web.api import movies_df

from wordcloud import WordCloud, STOPWORDS

router = APIRouter()

stopwords = set(STOPWORDS)
stopwords.update(["movie", "film", "one", "go", "scene", "plot", "character", "actor",
                  "see", "seen", "much", "scenes", "minute", "end", "start", "begin",
                  "hour", "second", "review", "u", "yet", "every", "lot", "s",
                  "etc", "soo", "yes", "no", "you", "amp", "come", "say",
                  "movies",
                  "Gun Maverick", "times", "everything", "little", "something",
                  "make", "another", "many", "let", "wasnt", "wasnt", "put"
                  "audience", "watch", "watching", "seen", "screen", "time"])


@router.get("/{movie_id}")
async def get_movie(movie_id):
    if movie_id not in movies_df['id'].values:
        return "id not found"
    else:
        movie = movies_df.loc[movies_df['id'] == movie_id].iloc[0]

        all_comments = " ".join([review['text'] for review in movie["reviews"]])

        wc = WordCloud(max_words=100, stopwords=stopwords, margin=10,
                       random_state=1, background_color='white').generate(all_comments)

        # Stop generation world cloud svgs on api call
        #svg_string = wc.to_svg("test.svg")
        #with open("svgTest.svg", "w") as svg_file:
        #    svg_file.write(svg_string)

        words = wc.words_

        # Absolute word counts
        for myword in words.keys():
            words[myword] = (words[myword], all_comments.count(myword))

        movie["wordcloud"] = words
        movie['release'] = pd.to_datetime(movie['release'])
        movie['release'] = movie['release'].strftime('%Y-%m-%d %H:%M:%S')

        # remove currently not needed data from the response
        # todo: instead of removing data, we should only include the data we need
        movie = movie.drop("reviews")
        movie = movie.drop("boxoffice_inflated")
        movie = movie.drop("budget_inflated")
        movie = movie.drop("ROI_category")
        movie = movie.drop("director_gender")
        movie = movie.drop("modified_rating")
        movie = movie.drop("top_actor_gender")

        movie = movie.fillna('')

        return JSONResponse(movie.to_dict())

# Broken: http://localhost:8000/api/movies/tt10370710

# tt0081505
# get_movie("tt10370710")


@router.get("/")
async def get_movies(year: int = None, rating: float = None, page: int = 1, page_size: int = 10):
    filtered_movies = movies_df

    if year is not None:
        filtered_movies = filtered_movies.query("release_year == @year")

    if rating is not None:
        filtered_movies = filtered_movies.query("@rating <= rating <= @rating + 0.9")

    total_items = len(filtered_movies)
    total_pages = (total_items + page_size - 1) // page_size
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)

    # Slice the dataframe
    paginated_movies = filtered_movies.iloc[start_idx:end_idx]
    
    # Convert to string and prepare return list
    paginated_movies["release"] = paginated_movies["release"].astype(str)
    return_list = paginated_movies[
        ["id", "title", "rating", "cover", "release"]].to_dict(orient="records")

    response = {
        "movies": return_list,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_items,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }

    return JSONResponse(response)


@router.get("/flops")
async def count_flops(year: int = None, rating: float = None):
    filtered_movies = movies_df

    if year is not None:
        filtered_movies = filtered_movies.query("release_year == @year")

    if rating is not None:
        filtered_movies = filtered_movies.query("@rating <= rating <= @rating + 0.9")

    flops = 0
    success = 0

    for movie in filtered_movies.iterrows():
        difference = movie['boxoffice'] - movie['budget']

        if difference > 0:
            success += 1
        else:
            flops += 1

    data = {'flops': flops,
            'success': success}

    return JSONResponse(data)
