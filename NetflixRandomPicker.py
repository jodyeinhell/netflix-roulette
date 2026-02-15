
import pandas as pd
import random
import tkinter as tk
from tkinter import ttk

# Load dataset
df = pd.read_csv("netflix_us_movies_only.csv")

# Clean genre column (listed_in)
df["listed_in"] = df["listed_in"].fillna("Unknown")

# Extract unique genres
all_genres = sorted(set(
    genre.strip()
    for genres in df["listed_in"]
    for genre in genres.split(",")
))

def pick_movie():
    selected_genre = genre_var.get()
    
    if selected_genre == "All":
        filtered = df
    else:
        filtered = df[df["listed_in"].str.contains(selected_genre, na=False)]
    
    if filtered.empty:
        result_label.config(text="No movies found for that genre.")
        return
    
    movie = filtered.sample(1).iloc[0]
    
    title = movie["title"]
    year = movie["release_year"]
    director = movie["director"] if pd.notna(movie["director"]) else "Unknown"
    genre = movie["listed_in"]
    
    result_text = f"{title} ({year})\nDirector: {director}\nGenre: {genre}"
    result_label.config(text=result_text)

# GUI Setup
root = tk.Tk()
root.title("Netflix Random Movie Picker")
root.geometry("500x350")

title_label = tk.Label(root, text="Netflix Random Movie Picker", font=("Helvetica", 16))
title_label.pack(pady=10)

genre_var = tk.StringVar()
genre_dropdown = ttk.Combobox(root, textvariable=genre_var)
genre_dropdown["values"] = ["All"] + all_genres
genre_dropdown.current(0)
genre_dropdown.pack(pady=10)

pick_button = tk.Button(root, text="Pick Random Movie", command=pick_movie)
pick_button.pack(pady=10)

result_label = tk.Label(root, text="", wraplength=450, justify="center")
result_label.pack(pady=20)

root.mainloop()
