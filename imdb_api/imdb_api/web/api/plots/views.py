import io
import json
from os.path import dirname, join
import numpy as np
import pandas as pd
import plotly.express as px
from fastapi import APIRouter
from starlette.responses import JSONResponse, HTMLResponse
import plotly.graph_objects as go

from imdb_api.web.api import movies_df

from wordcloud import WordCloud, STOPWORDS

router = APIRouter()


@router.get("/budgetrating")
async def get_plot():
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x=movies_df["budget_inflated"],
                   y=movies_df["rating"],
                   mode='markers',
                   hovertext=movies_df['title']
                   ))

    fig.update_layout(
        xaxis_title='Budget',
        yaxis_title='Rating',
        dragmode="zoom",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                x=1,
                y=1,
                yanchor="bottom",
                showactive=True,
                buttons=list(
                    [
                        dict(
                            label="Budget",
                            method="update",
                            args=[{"x": [movies_df["budget"]]}],
                        ),
                        dict(
                            label="Budget (inflated)",
                            method="update",
                            args=[{"x": [movies_df["budget_inflated"]]}],
                        ),
                        dict(
                            label="Box Office",
                            method="update",
                            args=[{"x": [movies_df["boxoffice"]]}],
                        ),
                        dict(
                            label="Box Office (inflated)",
                            method="update",
                            args=[{"x": [movies_df["boxoffice_inflated"]]}],
                        ),
                    ]
                ),
            )
        ]
    )

    buffer = io.StringIO()
    fig.write_html(buffer)

    html_string = buffer.getvalue()
    modified_html_string = html_string.replace("<head>",
                                               "<head><style>.modebar-container{display: none !important;}</style>")
    html_bytes = modified_html_string.encode()

    return HTMLResponse(content=html_bytes, status_code=200)


@router.get("/directorsgender")
async def get_plot():
    fig = go.Figure()

    gender_counts = movies_df['director_gender'].value_counts()
    gender_dict = gender_counts.to_dict()

    gender_mapping = {
        'andy': 'Andy',
        'mostly_male': 'Mostly Male',
        'unknown': 'Unknown',
        'female': 'Female',
        'male': 'Male',
        'mostly_female': 'Mostly Female'
    }

    gender_dict_with_names = {gender_mapping[key]: value for key, value in
                              gender_dict.items()}

    sorted_gender_dict = dict(
        sorted(gender_dict_with_names.items(), key=lambda item: item[1], reverse=True))

    fig.add_trace(go.Bar(
        x=list(sorted_gender_dict.keys()),
        y=list(sorted_gender_dict.values())
    ))

    fig.update_layout(
        xaxis_title='Gender',
        yaxis_title='Count',
        dragmode=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )

    buffer = io.StringIO()
    fig.write_html(buffer)

    html_string = buffer.getvalue()
    modified_html_string = html_string.replace("<head>",
                                               "<head><style>.modebar-container{display: none !important;}</style>")
    html_bytes = modified_html_string.encode()

    return HTMLResponse(content=html_bytes, status_code=200)


@router.get("/directorsgenderanimated")
async def get_directors_plot():
    gender_counts_per_year = movies_df.groupby(
        ['release_year', 'director_gender']).size().reset_index(name='count')

    # Alle eindeutigen Geschlechter extrahieren
    all_genders = movies_df['director_gender'].unique()

    # Verwendung des gender_mapping
    gender_mapping = {
        'andy': 'Andy',
        'mostly_male': 'Mostly Male',
        'unknown': 'Unknown',
        'female': 'Female',
        'male': 'Male',
        'mostly_female': 'Mostly Female'
    }

    # Anpassen der Geschlechterbezeichnungen
    gender_counts_per_year['director_gender'] = gender_counts_per_year[
        'director_gender'].map(gender_mapping)

    # Festlegen der Reihenfolge der Geschlechter
    gender_order = ['Male', 'Mostly Male', 'Female', 'Mostly Female', 'Andy', 'Unknown']
    gender_counts_per_year['director_gender'] = pd.Categorical(
        gender_counts_per_year['director_gender'], categories=gender_order,
        ordered=True)

    # Verbreiterung des DataFrames, um fehlende Geschlechter und Anzahl 0 hinzuzufügen
    expanded_gender_counts = gender_counts_per_year.pivot(index='release_year',
                                                          columns='director_gender',
                                                          values='count')
    expanded_gender_counts = expanded_gender_counts.reindex(columns=gender_order,
                                                            fill_value=0)
    expanded_gender_counts = expanded_gender_counts.reset_index().melt(
        id_vars='release_year', value_name='count')

    # Erstellung des animierten Balkendiagramms mit Jahres-Slider
    fig = px.bar(expanded_gender_counts, x='director_gender', y='count',
                 color='director_gender', animation_frame='release_year',
                 range_y=[0, expanded_gender_counts['count'].max()],
                 labels={'director_gender': 'Gender', 'count': 'Count'})

    # Hinzufügen des Liniendiagramms für die Häufigkeiten von Frauen und Männern
    male_counts_per_year = gender_counts_per_year.loc[
        gender_counts_per_year['director_gender'] == 'Male']

    female_counts_per_year = gender_counts_per_year.loc[
        gender_counts_per_year['director_gender'] == 'Female']

    years = range(1980, 2023)  # Jahre von 1980 bis 2022

    for year in years:
        if year not in male_counts_per_year['release_year'].values:
            male_counts_per_year = pd.concat(
                [male_counts_per_year, pd.DataFrame({'release_year': [year], 'count': [0]})],
                ignore_index=True)

        if year not in female_counts_per_year['release_year'].values:
            female_counts_per_year = pd.concat(
                [female_counts_per_year, pd.DataFrame({'release_year': [year], 'count': [0]})],
                ignore_index=True)

    male_counts_per_year = male_counts_per_year.sort_values('release_year')
    female_counts_per_year = female_counts_per_year.sort_values('release_year')

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(x=male_counts_per_year['release_year'],
                   y=male_counts_per_year['count'],
                   mode='lines', name='Male', line=dict(color='blue'))
    )
    fig2.add_trace(
        go.Scatter(x=female_counts_per_year['release_year'],
                   y=female_counts_per_year['count'],
                   mode='lines', name='Female', line=dict(color='red'))
    )


    # Anpassen des Layouts
    fig.update_layout(
        dragmode=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True
    )

    fig2.update_layout(
        yaxis_title="Count",
        xaxis_title="Release Year",
        dragmode=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True
    )

    # Anpassen der Animationseinstellungen
    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500

    # Erzeugen des HTML-Strings und Anpassen des Modusleisten-Stils
    buffer = io.StringIO()
    buffer2 = io.StringIO()
    fig.write_html(buffer, auto_play=False, default_height='50%')
    fig2.write_html(buffer2, default_height='50%')

    html_string = buffer.getvalue()
    html_string2 = buffer2.getvalue()

    html_string = html_string2 + html_string

    modified_html_string = html_string.replace("<head>",
                                               "<head><style>.modebar-container{display: none !important;}</style>")
    html_bytes = modified_html_string.encode()

    return HTMLResponse(content=html_bytes, status_code=200)


@router.get("/budgetboxofficeanimated")
def get_plot():
    movies_df['modified_rating'] = np.power(movies_df['rating'], 6)
    movies_df['ROI'] = (movies_df['boxoffice'] - movies_df['budget']) / movies_df['budget']
    bins = [-np.inf, 0, 1, 5, 20, 100, 1000, np.inf]
    labels = ['<0', '0-1', '1-5', '5-20', '20-100', '100-1000', '>1000']
    movies_df['ROI_category'] = pd.cut(movies_df['ROI'], bins=bins, labels=labels, right=False)

    color_discrete_map = {
        '<0': 'rgb(255,0,0)',
        '0-1': 'rgb(255,162,0)',
        '1-5': 'rgb(82,255,0)',
        '5-20': 'rgb(0,95,255)',
        '20-100': 'rgb(0,232,255)',
        '100-1000': 'rgb(255,0,249)',
        '>1000': 'rgb(136,0,255)'
    }
    category_orders = ['<0', '0-1', '1-5', '5-20', '20-100', '100-1000', '>1000']

    movies_df.sort_values(by=['release_year'], inplace=True)

    key_cols = ["ROI_category", "release_year", "modified_rating"]

    df2 = pd.DataFrame(
        index=pd.MultiIndex.from_product(
            [movies_df[col].unique() for col in key_cols], names=key_cols
        )
    ).merge(movies_df, on=key_cols, how="left")

    #df2["modified_rating"] = df2["modified_rating"].fillna(0)

    fig = px.scatter(df2, x="budget_inflated", y="boxoffice_inflated",
                     animation_frame="release_year", size="modified_rating",
                     color="ROI_category", hover_name="title",
                     log_x=True, size_max=55,
                     range_x=[min(movies_df["budget_inflated"]),
                              max(movies_df["budget_inflated"]) * 1.5],
                     range_y=[-200000000,
                              max(movies_df["boxoffice_inflated"]) * 1.1],
                     custom_data=['budget_inflated', 'boxoffice_inflated',
                                  'rating', 'ROI'],
                     color_discrete_map=color_discrete_map,
                     category_orders={"ROI_category": category_orders},
                     hover_data={'release_year': False,
                                 'modified_rating': False,
                                 'budget_inflated': True,
                                 'boxoffice_inflated': True,
                                 'ROI_category': False,
                                 'rating': True,
                                 'ROI': ':.2f'
                                 }
                     )

    fig.update_layout(
        xaxis_title='Budget',
        yaxis_title='Box Office',
        dragmode='zoom',
        legend_title_text='ROI',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightskyblue')

    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500

    buffer = io.StringIO()
    fig.write_html(buffer, auto_play=False)

    html_string = buffer.getvalue()
    modified_html_string = html_string.replace("<head>",
                                               "<head><style>.modebar-container{display: none !important;}</style>")
    html_bytes = modified_html_string.encode()

    return HTMLResponse(content=html_bytes, status_code=200)

get_plot()

@router.get("/ratingsovertime")
async def get_plot():
    N = len(movies_df['release_year'])
    c = ['hsl(' + str(h) + ',50%' + ',50%)' for h in np.linspace(0, 360, N)]

    color_map = {}
    for year, color in zip(list(movies_df['release_year']), c):
        color_map[year] = color

    mean_values = movies_df.groupby("release_year")["rating"].mean()

    fig = px.box(movies_df, x="release_year", y="rating", color="release_year",
                 color_discrete_map=color_map)

    fig.add_trace(px.line(x=mean_values.index, y=mean_values,
                          color_discrete_sequence=['black']).data[0])

    fig.update_layout(
        xaxis_title='Release Year',
        yaxis_title='Rating',
        dragmode=False,
        xaxis=dict(
            title='Release Year',
            tickmode='linear'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )

    buffer = io.StringIO()
    fig.write_html(buffer)

    html_string = buffer.getvalue()
    modified_html_string = html_string.replace("<head>",
                                               "<head><style>.modebar-container{display: none !important;}</style>")
    html_bytes = modified_html_string.encode()

    return HTMLResponse(content=html_bytes, status_code=200)
