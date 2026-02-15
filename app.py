
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Netflix Roulette", page_icon="🎬", layout="centered")

st.title("🎬 Netflix Roulette")
st.markdown("Spin the wheel. Let fate choose your movie.")

@st.cache_data
def load_data():
    df = pd.read_csv("netflix_us_movies_only.csv")
    df["listed_in"] = df["listed_in"].fillna("Unknown")
    return df

df = load_data()

# Extract genres
all_genres = sorted(set(
    genre.strip()
    for genres in df["listed_in"]
    for genre in genres.split(",")
))

genre = st.selectbox("Choose Genre (Optional)", ["All"] + all_genres)

if st.button("🎡 Spin"):
    if genre == "All":
        filtered = df
    else:
        filtered = df[df["listed_in"].str.contains(genre, na=False)]
    
    if filtered.empty:
        st.warning("No movies found.")
    else:
        movie = filtered.sample(1).iloc[0]
        
        title = movie["title"]
        year = movie["release_year"]
        director = movie["director"] if pd.notna(movie["director"]) else "Unknown"
        genre_text = movie["listed_in"]
        
        st.success(f"**{title} ({year})**")
        st.write(f"**Director:** {director}")
        st.write(f"**Genre:** {genre_text}")
