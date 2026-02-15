import streamlit as st
import pandas as pd
import random
import json

st.set_page_config(page_title="Netflix Roulette", page_icon="🎬", layout="centered")

@st.cache_data
def load_data():
    df = pd.read_csv("netflix_us_movies_only.csv")
    df["listed_in"] = df["listed_in"].fillna("Unknown")
    return df

df = load_data()

st.title("🎬 Netflix Roulette")

if st.button("🎡 Generate Wheel"):

    # Pick 50 random movies
    wheel_movies = df.sample(50).to_dict(orient="records")
    titles = [m["title"] for m in wheel_movies]

    movie_data_json = json.dumps(wheel_movies)

    st.components.v1.html(f"""
    <canvas id="wheel" width="600" height="600"></canvas>
    <br>
    <button id="spinBtn">SPIN</button>

    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>

    <script>
    const movies = {movie_data_json};
    const titles = {json.dumps(titles)};

    const canvas = document.getElementById("wheel");
    const ctx = canvas.getContext("2d");
    const spinBtn = document.getElementById("spinBtn");

    const radius = canvas.width / 2;
    const slices = 50;
    const arc = (2 * Math.PI) / slices;

    let angle = 0;
    let velocity = 0;

    function drawWheel() {{
        ctx.clearRect(0,0,canvas.width,canvas.height);

        for (let i=0; i<slices; i++) {{
            ctx.beginPath();
            ctx.moveTo(radius, radius);
            ctx.arc(radius, radius, radius, i*arc+angle, (i+1)*arc+angle);
            ctx.fillStyle = i % 2 == 0 ? "#e50914" : "#111";
            ctx.fill();

            ctx.save();
            ctx.translate(radius, radius);
            ctx.rotate(i*arc+arc/2+angle);
            ctx.textAlign = "right";
            ctx.fillStyle = "white";
            ctx.font = "10px Arial";
            ctx.fillText(titles[i].substring(0,20), radius-10, 0);
            ctx.restore();
        }}
    }}

    function spin() {{
        velocity = Math.random() * 0.4 + 0.35;
        animate();
    }}

    function animate() {{
        angle += velocity;
        velocity *= 0.985;  // friction

        drawWheel();

        if (velocity > 0.002) {{
            requestAnimationFrame(animate);
        }} else {{
            finishSpin();
        }}
    }}

    function finishSpin() {{
        const index = Math.floor(((2*Math.PI - (angle % (2*Math.PI))) / (2*Math.PI)) * slices) % slices;
        const selected = movies[index];

        confetti({{
            particleCount: 200,
            spread: 120
        }});

        const audio = new Audio("https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg");
        audio.play();

        alert(
            selected.title + " (" + selected.release_year + ") [" + selected.rating + "]\\n" +
            "Runtime: " + selected.duration + "\\n" +
            "Genre: " + selected.listed_in + "\\n" +
            "Director: " + selected.director
        );
    }}

    spinBtn.onclick = spin;

    drawWheel();
    </script>
    """, height=750)
