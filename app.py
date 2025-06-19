import streamlit as st
import pickle
import pandas as pd
import requests
import gdown
import os
import base64
#request modules To fetch api

# Downloading similarity matrix
file_id = '1tDyyZ3d7ZEUDjWv0Iw3Taum4nVOmBfnR'
output = 'similarity.pkl'
url = f'https://drive.google.com/uc?id={file_id}'

if not os.path.exists(output):
    gdown.download(url, output, quiet=False)

with open(output, 'rb') as f:
    similarity = pickle.load(f)

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# --- Fetch Poster ---
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=0e320801c4cc2c20a5c77ae03b3514e1&language=en-US"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=Error"

# --- Recommend Logic ---
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    names, posters, ids = [], [], []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        ids.append(movie_id)
        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))
    return names, posters, ids

# --- Set background + overlay ---
def set_background(image_file):
    with open(image_file, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode()

    css = f"""
    <style>
    # html, body {{
    #     margin: 0;
    #     padding: 0;
    #     overflow-x: hidden;
    }}
    .stApp {{
        background-image: url("data:image/png;base64,{base64_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    .brand-header {{
        position: relative;
         background-position: left;
         margin-right:50%;
        top: 0px;
          left: 0px;
         font-size: 26px;
        font-weight: bold;
         color: white;
         background-color: rgba(0, 0, 0, 0.7);
        padding: 8px;
         border-radius: 6px;
        z-index: 1000;
          text-align: left;
         font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
     background: linear-gradient(to right, #ff2b85, #ff7eb3);
     -webkit-background-clip: text;
     -webkit-text-fill-color: transparent;
     text-shadow: 1px 1px 2px rgba(0,0,0,0.5);

    }}
    .overlay {{
        background-color: rgba(0, 0, 0, 0.7);
        #background-color:white;
        padding: 30px;
        text-align: center;
        border-radius: 10px;
        color: #ccc;
        max-width: 600px;
        margin:20px;
        # margin: 80px auto 20px auto;
    }}
    .title {{
        font-size: 36px;
        font-weight: 800;
        margin-bottom: 10px;
    }}
    .subtitle {{
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 25px;
    }}
    .email-box {{
        border-radius: 30px;
        padding: 10px 20px;
        width: 260px;
        margin-right: 10px;
        font-size: 16px;
    }}
    .get-started-btn {{
        background-color: #ff2b85;
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 30px;
        font-size: 16px;
        cursor: pointer;
    }}
    </style>
    """
    # st.markdown('<div class="brand-header">EchoWatch</div>', unsafe_allow_html=True)

    html = """
    <div class="brand-header">CineSage</div>
    <div class="overlay">
        <div class="title">Your next pick,</div>
        <div class="subtitle">Just a click away!</div>
        <form action="#recommend-section">
            <input type="email" placeholder="Enter your email..." class="email-box"/>
            <button type="submit" class="get-started-btn">Get Started</button>
        </form>
    </div>
    """

    st.markdown(css + html, unsafe_allow_html=True)

# Apply background with header
set_background("bg4.jpg")  # Make sure this file exists in your working directory

# --- Extra Styling ---
recommender_css = """
<style>
.movie-card {
    border: 3px solid black;
    border-radius: 12px;
    margin-bottom: 20px;
    text-align: center;
    background-color: rgba(255,255,255,0.05);
    transition: 0.3s ease;
}
.movie-card:hover {
    border-color: #ff2b85;
    background-color: rgba(255,255,255,0.1);
    transform: scale(1.02);
}
.movie-card img {
    width: 100%;
    height: auto;
    display: block;
}
.movie-title {
    font-size: 16px;
    color: white;
    margin-top: 7px;
    display: inline-block;
}
div[data-baseweb="select"] label {
    color: white !important;
    font-size: 30px !important;
    font-weight: 600 !important;
}
label:has(+ div[data-baseweb="select"]) {
    color: #ff2b85 !important;
    font-size: 20px !important;
    font-weight: 600 !important;
}
button[kind="primary"] {
    background-color: #ff2b85 !important;
    color: white !important;
    font-weight: 600;
    border-radius: 12px;
    padding: 10px 20px;
    font-size: 16px;
    border: none;
    transition: background 0.3s ease;
}
button[kind="primary"]:hover {
    background-color: #e61b70 !important;
}
</style>
"""
st.markdown(recommender_css, unsafe_allow_html=True)

# --- Recommendation Section ---
st.markdown('<div id="recommend-section"></div>', unsafe_allow_html=True)

selected_movie_name = st.selectbox('Select a movie:', movies['title'].values)

if st.button('Recommend'):
    names, posters, ids = recommend(selected_movie_name)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        movie_link = f"https://www.themoviedb.org/movie/{ids[idx]}"
        short_title = names[idx][:40] + "..." if len(names[idx]) > 40 else names[idx]
        with col:
            st.markdown(f"""
                <div style="text-align:center;">
                    <a href="{movie_link}" target="_blank" style="text-decoration:none;">
                        <div class="movie-card">
                            <img src="{posters[idx]}" alt="Movie Poster">
                        </div>
                        <span class="movie-title">{short_title}</span>
                    </a>
                </div>
            """, unsafe_allow_html=True)
