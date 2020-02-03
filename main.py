import json
import requests
import pandas as pd
import argparse
import re
import numpy as np
import matplotlib.pyplot as plt
import funciones as func
import os

    #Here are defined the esential parameters of argparse 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("film", help="the title of the film")
    parser.add_argument("web", help="The name of the website whose score you are looking for")

    args = parser.parse_args()
    
    film = str(args.film)   
    web = str(args.web)
    

    #Here we import functions for our "funciones.py"
    df_movies = pd.read_csv("movies_reduced.csv") 
    df_movies = df_movies.drop_duplicates(subset="title")

    df_movies["tmdbRating"] = df_movies["movieId"].apply(func.bring_rating)
    df_movies["year"] = df_movies["title"].apply(func.year_column)
    df_movies["title"] = df_movies["title"].apply(func.clean_title)

    titles_list = df_movies["title"].to_list()

    #Here we make calls to API

    alljsons =[]

    for movie in titles_list[0:10]:
        alljsons.append(func.get_movies(movie))

    #Pandas dataframes and more functions

    df = pd.DataFrame(alljsons)
    df = df.rename(columns={"Title": "title"})

    df = df.merge(df_movies, on="title")

    df = df.drop(["Ratings", "Response", "BoxOffice","Website","movieId","year"], axis=1)

    df["Metascore"] = df["Metascore"].apply(func.convert_to_float)
    df = df[(df["Metascore"] != "N/A")]
    df["Metascore"] = df["Metascore"].apply(func.convert_to_float)
    df["Metascore"] = df["Metascore"] / 10

    df["imdbRating"] = df["imdbRating"].apply(func.convert_to_float)
    df = df[(df["imdbRating"] != "N/A")]

    #Global Info that will fill our report

    df_describe = round(df.describe(include=np.number),2)
    df_describe = df_describe.reset_index(level=None, drop=False, inplace=False, col_level=0, col_fill='')
    df_describe = df_describe.rename(columns={"index": "Stats"})
    print(df_describe)

    #Film Info that will fill our report

    if web == "all":
        df_film = df[["title","Metascore" ,"imdbRating","tmdbRating"]]
        print(df_film[df_film["title"] == film])
    else:
        df_film = df[["title", web]]
        print(df_film[df_film["title"] == film])



    df_film[(df_film["title"] == film)].mean(axis = 0).plot.bar(figsize=(10,7))

    plt.ylabel("Scores")
    plt.xlabel("Webs")
    plt.savefig('foo.png')

    #Functions to generate report and send email!

    func.report(df_describe,film)
    func.email()



        