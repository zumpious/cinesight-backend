"""imdb_api API package."""
import html
import json
import os
from cpi import inflate
import pandas as pd
import gender_guesser.detector as gender
from os.path import dirname, join

# Heavy lifting only once
# this will be refactored in the future
script_dir = dirname(dirname(dirname(dirname(dirname(__file__)))))

dfs = []

for year in range(1980, 2023):
    print(year)
    rel_path = f'scraper/results/top100_{year}.json'
    abs_file_path = join(script_dir, rel_path)

    print(abs_file_path)
    temp = pd.read_json(abs_file_path, orient=str)
    dfs.append(temp)

movies_df = pd.concat(dfs, ignore_index=True)
movies_df['id'] = movies_df['link'].apply(lambda x: x.split('/')[-1].strip())

movies_df = movies_df.dropna(subset=['release'])
movies_df['release'] = pd.to_datetime(movies_df['release'])
movies_df = movies_df.loc[movies_df['release'] <= pd.to_datetime('2022-12-31')]
movies_df['release_year'] = movies_df['release'].dt.year.astype(int)
movies_df = movies_df.dropna()
movies_df['boxoffice_inflated'] = movies_df.apply(lambda row: inflate(row['boxoffice'], row['release_year'], to=2022), axis=1)
movies_df['budget_inflated'] = movies_df.apply(lambda row: inflate(row['budget'], row['release_year'], to=2022), axis=1)

gd = gender.Detector(case_sensitive=False)

movies_df['director_gender'] = movies_df['directors'].apply(lambda x: str(x[0].split(" ")[0])).map(lambda x: gd.get_gender(x))
movies_df['top_actor_gender'] = movies_df['actors'].apply(lambda x: str(x[0].split(" ")[0])).map(lambda x: gd.get_gender(x))

movies_df['title'] = movies_df['title'].apply(lambda title: html.unescape(title))
