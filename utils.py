import os

from datetime import datetime

import requests
from bs4 import BeautifulSoup

from icrawler.builtin import BingImageCrawler

import pandas as pd

def load_df(file):

    places = ["something"]
    places_readable = ["something"]
    cities = ["city", "something"]

    mapping_countries, mapping_states = {}, {}

    df = pd.read_csv(file, sep="\t")
    compt_cities = 2
    for _, row in df.iterrows():

        if not pd.isnull(row["Rank"]):# and row["Rank"] <= 1000:
            if pd.isnull(row["Potential State"]):
                cities.append(f'{row["City"]}, {row["Country"]}')
            else:
                cities.append(f'{row["City"]}, {row["Potential State"]}, {row["Country"]}')
                mapping_states[f'{row["Potential State"]}, {row["Country"]}'] = mapping_states.get(f'{row["Potential State"]}, {row["Country"]}', []) + [compt_cities]

            mapping_countries[f'{row["Country"]}'] = mapping_countries.get(f'{row["Country"]}', []) + [compt_cities]

            compt_cities += 1

        elif pd.isnull(row["Rank"]):
            places.append(row["Place"])

            if pd.isnull(row["City"]):
                places_readable.append(f'{row["Place"]}, {row["Country"]}')
            else:
                places_readable.append(f'{row["Place"]}, {row["City"]}, {row["Country"]}')

    return cities, places, places_readable, mapping_countries, mapping_states

def get_insta_link(insta_link):

    content = requests.get(insta_link).content

    soup = BeautifulSoup(content, features="html.parser")
    metas = soup.find_all(attrs={"property": "og:image"})

    return metas[0].attrs['content']

def save_web_image(images_path, link):

    nb_files = len([entry for entry in os.scandir(images_path)])
    if nb_files > 30:
        for entry in os.scandir(images_path):
            os.remove(entry.path)

    content = requests.get(link).content

    name = f"{images_path}/{str(datetime.now())}.jpg"

    with open(name, 'wb') as handler:
        handler.write(content)

    return name

def download_images(
    term: str,
    images_path,
    nb_images: int,
    *,
    min_size = (50, 50)
):
    term = term.lower()

    crawler = BingImageCrawler(
        feeder_threads=2,
        parser_threads=2,
        downloader_threads=8,
        storage={"root_dir": images_path},
    )

    crawler.crawl(
        keyword=term,
        max_num=nb_images,
        min_size=min_size,
        file_idx_offset="auto"
    )