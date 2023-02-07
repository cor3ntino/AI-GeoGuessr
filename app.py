import os

import tempfile

import numpy as np
import pandas as pd

from PIL import Image
import streamlit as st

from geopy.geocoders import Nominatim
from geopy.distance import great_circle

from utils import load_df, get_insta_link, save_web_image, download_images
from model import Model
from ruler import Ruler
from rankings_handler import read_rankings, update_rankings
from ia_vs_human_handler import read_ia_vs_human, update_ia_vs_human

import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title = "AI GeoGuessr",
    layout = "wide"
)

LINK_DRIVE = "https://docs.google.com/spreadsheets/d/1n6fD4kvYS4ol1Z3M_CDKlzTVX6mqYytCJWsL-NdYC1I/edit?usp=sharing"

IMAGES_DOWNLOADED_PATH = "resources_app/images_downloaded"
IMAGES_RANDOM_PATH = "resources_app/images_random"
IMAGES_GAME_PATH = "resources_app/images_game"

GEOLOCATOR = Nominatim(user_agent="app")

@st.cache(allow_output_mutation=True)
def load_model():
    return Model(), Ruler()

MODEL, RULER = load_model()

CITIES_LIST, _, PLACES_LIST, mapping_countries, _ = load_df("cities-final.tsv")
COUNTRIES_LIST = [country for country in mapping_countries.keys()]
PLACES_LIST = PLACES_LIST[1:]

def show_try():
    st.title("GeoGuessr 🗺️ Try me!")
    st.write("#### Here you can see how the model performs to predict city, country or even a monument just out pictures! Some random images and their predictions are shown below!")
    st.write("#### You can also use it with your favorite pictures from an Instagram post, an image link, or even your own photos from your computer! Enjoy 🔥")

    type_images = st.selectbox(
        "On what kind of images do you want to try this feature on?",
        ["Show me some random pictures 🔀", "I want to use an Instagram picture 🤳", "I want to use an image link 🖼️", "I want to use my own local images 💻"],
        label_visibility="collapsed"
    )

    if type_images == "I want to use my own local images 💻":

        files_images = st.file_uploader(
            "Upload image(s)",
            type=([".jpeg", ".jpg"]),
            accept_multiple_files=True
        )

        for image in files_images:
            st.markdown("---")
            g, d = st.columns(2)

            with g:
                st.image(image)
            with d:
                cities_probs, places_probs = MODEL.predict(Image.open(image))
                res = RULER.get_result(cities_probs, places_probs)
                st.write(res)

    elif type_images == "I want to use an Instagram picture 🤳":

        insta_link = st.text_input("Copy/Paste your Instagram link here...", value="https://www.instagram.com/p/CjIArDfocBM/")

        if "instagram" in insta_link:

            try:
                image_link = get_insta_link(insta_link)
                image = save_web_image(IMAGES_DOWNLOADED_PATH, image_link)

                st.markdown("---")
                g, d = st.columns(2)
                with g:
                    st.image(image)
                with d:
                    cities_probs, places_probs = MODEL.predict(Image.open(image))
                    res = RULER.get_result(cities_probs, places_probs)
                    st.write(res)

            except:
                st.write("##### Looks like your link is broken 😕")

    elif type_images == "I want to use an image link 🖼️":

        link = st.text_input("Copy/Paste the link of your image here...", value="https://www.telegraph.co.uk/content/dam/Travel/Destinations/South%20America/Colombia/AP59243209_Colombia_Travel.jpg")

        try:
            image = save_web_image(IMAGES_DOWNLOADED_PATH, link)

            st.markdown("---")
            g, d = st.columns(2)
            with g:
                st.image(image)
            with d:
                cities_probs, places_probs = MODEL.predict(Image.open(image))
                res = RULER.get_result(cities_probs, places_probs)
                st.write(res)

        except:
                st.write("##### Looks like your link is broken 😕")

    elif type_images == "Show me some random pictures 🔀":

        for entry in os.scandir(IMAGES_RANDOM_PATH):

            image = entry.path

            st.markdown("---")
            g, d = st.columns(2)
            with g:
                st.image(image)
            with d:
                cities_probs, places_probs = MODEL.predict(Image.open(image))
                res = RULER.get_result(cities_probs, places_probs)
                st.write(res)

def download_and_choose():

    with st.spinner("Looking for random pictures on the Web for the next country..."):
        download_images(term=f"random photos of {st.session_state.locations[st.session_state.step]}", images_path=st.session_state.temp_folder.name, nb_images=3)
        download_images(term=f"instagram photos of {st.session_state.locations[st.session_state.step]}", images_path=st.session_state.temp_folder.name, nb_images=3)

        st.success(f"I found some tricky ones 😏")

    images = [entry.path for entry in os.scandir(st.session_state.temp_folder.name)]

    return np.random.choice(images)

def show_image_and_selectbox():
    g, d = st.columns(2)
    with g:
        st.image(st.session_state.image)
    with d:

        if f"placeholder_country_{st.session_state.step}" not in st.session_state:

            st.selectbox(
                "Select a country! Help yourself with the map below!",
                [""] + COUNTRIES_LIST,
                key=f"placeholder_country_{st.session_state.step}"
            )

            st.map()

        else:

            st.write("\n")
            user_res = st.session_state[f"placeholder_country_{st.session_state.step}"]
            st.write(f"##### ➡️ You have selected {user_res}")
            user_res_geo = GEOLOCATOR.geocode(user_res)

            cities_probs, places_probs = MODEL.predict(Image.open(st.session_state.image))
            ai_res = RULER.get_best_country(cities_probs, places_probs)
            st.write(f"##### ➡️ AI has selected {ai_res[0]} with {round(100 * ai_res[1].item(), 1)}% confidence")
            ai_res_geo = GEOLOCATOR.geocode(ai_res[0])

            st.write("\n")
            st.write(f"##### ⏩ Correct location was {st.session_state.locations[st.session_state.step]} ✔️")

            true_res = st.session_state.locations[st.session_state.step].split(", ")[-1]
            true_res_geo = GEOLOCATOR.geocode(true_res)

            st.write("\n")
            user_distance = round(great_circle((user_res_geo.latitude, user_res_geo.longitude), (true_res_geo.latitude, true_res_geo.longitude)).km)
            st.session_state.user_score += user_distance
            if user_distance > 0:
                st.write(f"##### You were at {user_distance} kms from correct location ❌")
            else:
                st.write(f"##### You chose the right country ✅")

            ai_distance = round(great_circle((ai_res_geo.latitude, ai_res_geo.longitude), (true_res_geo.latitude, true_res_geo.longitude)).km)
            st.session_state.ai_score += ai_distance
            if ai_distance > 0:
                st.write(f"##### AI was at {ai_distance} kms from correct location ❌")
            else:
                st.write(f"##### AI chose the right country ✅")

            if user_distance > ai_distance:
                update_ia_vs_human(player="ai")
            elif user_distance < ai_distance:
                update_ia_vs_human(player="user")

            df_geo = pd.DataFrame(
                data = [
                    [user_res_geo.latitude, user_res_geo.longitude, user_res, "User"],
                    [ai_res_geo.latitude, ai_res_geo.longitude, ai_res, "AI"],
                    [true_res_geo.latitude, true_res_geo.longitude, true_res, "Truth"]
                ],
                columns = ["lat", "lon", "country", "player"]
            )

            st.map(df_geo)

def show_game():
    st.title("GeoGuessr 🗺️ Let's play a game!")

    if "add_ranking" in st.session_state:

        temp = st.session_state.add_ranking.split("/")
        if len(temp) == 2:
            name, location = temp
        else:
            name, location = temp[0], " "

        update_rankings(name, location, st.session_state.user_score)

        del st.session_state["add_ranking"]

    if "locations" not in st.session_state:
        st.write("##### Ready to try to tackle the AI? Solo or with a team? Perfect, let's play a short game ♟️.")
        st.write("##### Pictures of 10 places around the 🌎 will be randomly selected on the Web! Try to guess the country and beat the AI 🤖")
        st.write("##### The goal is to be as close as possible to the correct country, and your score is the sum of the difference of kilometers throught 10 pictures! Try to minimize your score & win!")
        st.write("##### Here, contrary to the 'Trying Mode', AI always guess a country, even if its confidence is really low; so you may see it makes huge mistakes when the picture in difficult. But, ifyou like this feature and we implement it in the future, we would only keep high confidence results, like in the 'Trying Mode'.")
        st.write("##### Start and continue the game by click on the button below.")

        # Select 8 cities and 2 places
        st.session_state.locations = []
        for _ in range(4):
            country = np.random.choice(COUNTRIES_LIST)
            city = CITIES_LIST[np.random.choice(mapping_countries[country])]
            st.session_state.locations += [city]
        st.session_state.locations += [np.random.choice(PLACES_LIST).item()]
        for _ in range(4):
            country = np.random.choice(COUNTRIES_LIST)
            city = CITIES_LIST[np.random.choice(mapping_countries[country])]
            st.session_state.locations += [city]
        st.session_state.locations += [np.random.choice(PLACES_LIST).item()]

        st.session_state.show_button = True
        st.session_state.step = -1
        st.session_state.user_score = 0
        st.session_state.ai_score = 0

    _, _, c, _, _ = st.columns(5)
    with c:
        if st.session_state.show_button or \
            (not st.session_state.show_button and st.session_state.step == 9):
            st.button("Next picture 🖼️", key="next_picture")
            st.session_state.show_button = False
        else:
            st.session_state.show_button = True

    if st.session_state.next_picture:
        st.session_state.step += 1

    st.markdown("---")

    if st.session_state.step >= 0 :
        _, l1, _, r1, _ = st.columns(5)
        with l1:
            st.write(f"###### Your Score: {st.session_state.user_score}")
        with r1:
            st.write(f"###### AI Score: {st.session_state.ai_score}")

        st.markdown("---")

    else:

        _, l2, _, r2, _ = st.columns(5)
        scores_ia_vs_human = read_ia_vs_human()
        with l2:
            st.write(f"###### AI won: {scores_ia_vs_human[0]}")
        with r2:
            st.write(f"###### Human won: {scores_ia_vs_human[1]}")

        st.markdown("---")

        _, _, c3, _, _ = st.columns(5)
        with c3:
            st.write("##### Current Top-100")
        df_rankings = read_rankings()
        df_rankings.sort_values(by="Points",inplace=True)
        df_rankings.reset_index(drop=True, inplace=True)
        st.table(df_rankings[:100])#st.dataframe(df_rankings[:100], use_container_width=True)

    if st.session_state.next_picture:

        if st.session_state.step > 9:
            st.write(f"##### Game is over, let's count points! 💯")

            st.write(f"##### You have {st.session_state.user_score} point(s) and AI has {st.session_state.ai_score} point(s).")

            if st.session_state.user_score < st.session_state.ai_score:
                st.write("##### ➡️ Human wins 🧠 It's not tomorrow Terminators will take over.")
            else:
                st.write("##### ➡️ AI wins 🤖 Looks like machines will annihilate humans.")

            del st.session_state.locations

            st.markdown("---")

            update_rankings("AI GeoGuessr 🤖", " ", st.session_state.ai_score)

            st.write(f"##### To add your score to the rankings 🏆, enter your name, or team name, and your location, separated with character '/'")
            st.write(f"##### Example: 'AI Team / Paris, France'")

            st.text_input("Your name, or team name, and your location, as in example above ⬆️ and press 'Enter'", key="add_ranking")

            st.markdown("---")

            st.write(f"##### To start a new game, just click the button 🔄")

        else:

            if (key := f"placeholder_country_{st.session_state.step - 1}") in st.session_state:
                del st.session_state[key]

            st.session_state.temp_folder = tempfile.TemporaryDirectory(dir=IMAGES_GAME_PATH)

            st.session_state.image = download_and_choose()

            show_image_and_selectbox()

    elif st.session_state.step >= 0:

        show_image_and_selectbox()

        if (key := "temp_folder") in st.session_state:
            st.session_state[key].cleanup()
            del st.session_state[key]

#%% Side bar
st.sidebar.title("AI GeoGuessr")
st.sidebar.write("The main goal of this project is to be able to identify both cities, countries, or even famous monuments!")
st.sidebar.write(f"List of available locations is on [Google Drive]({LINK_DRIVE}).")
st.sidebar.markdown("---")

page_names_to_funcs = {
    "Try me 🖼️": show_try,
    "Play against me 🤖": show_game,
}
selected_page = st.sidebar.selectbox("Select your favorite mode 🥳", page_names_to_funcs.keys())
st.sidebar.write("""You can either:
- Try this feature on your images 🖼️
- Play a small game against the AI 🤖
""")

page_names_to_funcs[selected_page]()
