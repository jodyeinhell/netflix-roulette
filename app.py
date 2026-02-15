import streamlit as st
import pandas as pd
import random
import json

st.set_page_config(page_title="Netflix Roulette", page_icon="🎬", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("netflix_us_movies_only.csv")
    df["listed_in"] = df["listed_in"].fillna("Unknown")
    return df

df = load_data()

st.markdown("<h1 style='text-align:center;'>🎬 Netflix Roulette</h1>", unsafe_allow_html=True)

# ---------- Genre Selector ----------
all_genres = sorted(set(
    genre.strip()
    for genres in df["listed_in"]
    for genre in genres.split(",")
))

genre = st.selectbox("Choose Genre (Optional)", ["All"] + all_genres)

if genre == "All":
    filtered = df
else:
    filtered = df[df["listed_in"].str.contains(genre, na=False)]

wheel_movies = filtered.sample(50) if len(filtered) >= 50 else filtered
wheel_movies = wheel_movies.to_dict(orient="records")
titles = [m["title"] for m in wheel_movies]

movie_data_json = json.dumps(wheel_movies)

st.components.v1.html(f"""
<div style="display:flex; flex-direction:column; align-items:center; justify-content:center;">

<canvas id="wheel" width="650" height="650"></canvas>

<button id="spinBtn"
style="
    margin-top:25px;
    padding:14px 34px;
    font-size:20px;
    background:linear-gradient(135deg,#e50914,#ff2a2a);
    color:white;
    border:none;
    border-radius:12px;
    cursor:pointer;
    box-shadow:0 0 20px rgba(229,9,20,0.6);
">
🎡 SPIN
</button>

<div id="resultCard"
style="
    margin-top:35px;
    padding:25px;
    width:550px;
    background:#111;
    color:white;
    border-radius:16px;
    display:none;
    text-align:center;
    box-shadow:0 0 35px rgba(229,9,20,0.8);
">
</div>

</div>

<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>

<script>
const movies = {movie_data_json};
const titles = {json.dumps(titles)};

const canvas = document.getElementById("wheel");
const ctx = canvas.getContext("2d");
const spinBtn = document.getElementById("spinBtn");
const resultCard = document.getElementById("resultCard");

const radius = canvas.width / 2;
const slices = movies.length;
const arc = (2 * Math.PI) / slices;

let angle = 0;
let spinning = false;

// ---------- Draw Wheel ----------
function drawWheel() {{
    ctx.clearRect(0,0,canvas.width,canvas.height);

    for (let i=0; i<slices; i++) {{
        const gradient = ctx.createLinearGradient(0,0,650,650);
        gradient.addColorStop(0, i%2==0 ? "#e50914" : "#ff3b3b");
        gradient.addColorStop(1, i%2==0 ? "#1a1a1a" : "#333");

        ctx.beginPath();
        ctx.moveTo(radius, radius);
        ctx.arc(radius, radius, radius-10, i*arc+angle, (i+1)*arc+angle);
        ctx.fillStyle = gradient;
        ctx.fill();

        ctx.save();
        ctx.translate(radius, radius);
        ctx.rotate(i*arc+arc/2+angle);
        ctx.textAlign = "right";
        ctx.fillStyle = "white";
        ctx.font = "bold 11px Arial";
        ctx.shadowColor = "black";
        ctx.shadowBlur = 4;
        ctx.fillText(titles[i].substring(0,24), radius-25, 0);
        ctx.restore();
    }}

    // Glow ring
    if (spinning) {{
        ctx.beginPath();
        ctx.arc(radius, radius, radius-5, 0, 2*Math.PI);
        ctx.strokeStyle = "rgba(229,9,20,0.8)";
        ctx.lineWidth = 8;
        ctx.shadowColor = "#e50914";
        ctx.shadowBlur = 25;
        ctx.stroke();
    }}

    // Center circle
    ctx.beginPath();
    ctx.arc(radius, radius, 90, 0, 2*Math.PI);
    ctx.fillStyle = "#111";
    ctx.fill();

    ctx.fillStyle = "#e50914";
    ctx.font = "bold 18px Arial";
    ctx.textAlign = "center";
    ctx.fillText(spinning ? "SPINNING..." : "READY", radius, radius+6);

    // Pointer
    ctx.beginPath();
    ctx.moveTo(radius, 8);
    ctx.lineTo(radius-16, 55);
    ctx.lineTo(radius+16, 55);
    ctx.fillStyle = "white";
    ctx.fill();
}}

// ---------- Easing Spin ----------
function spin() {{
    if (spinning) return;
    spinning = true;
    resultCard.style.display = "none";

    let start = null;
    const duration = 5000;
    const initialVelocity = Math.random()*10 + 25;

    const drum = new Audio("https://actions.google.com/sounds/v1/drums/drum_roll.ogg");
    drum.loop = true;
    drum.play();

    function animate(timestamp) {{
        if (!start) start = timestamp;
        let progress = timestamp - start;
        let percent = progress / duration;

        if (percent < 1) {{
            let ease = 1 - Math.pow(1-percent,3);
            angle += initialVelocity * (1 - ease);
            drawWheel();
            requestAnimationFrame(animate);
        }} else {{
            drum.pause();
            spinning = false;
            finishSpin();
        }}
    }}

    requestAnimationFrame(animate);
}}

function finishSpin() {{
    const index = Math.floor(((2*Math.PI - (angle % (2*Math.PI))) / (2*Math.PI)) * slices) % slices;
    const selected = movies[index];

    confetti({{
        particleCount: 300,
        spread: 160,
        origin: {{ y: 0.6 }}
    }});

    const winSound = new Audio("https://actions.google.com/sounds/v1/cartoon/concussive_drum_hit.ogg");
    winSound.play();

    resultCard.innerHTML = `
        <h2>${{selected.title}} (${{selected.release_year}}) [${{selected.rating || "NR"}}]</h2>
        <p><strong>Runtime:</strong> ${{selected.duration}}</p>
        <p><strong>Genre:</strong> ${{selected.listed_in}}</p>
        <p><strong>Director:</strong> ${{selected.director || "Unknown"}}</p>
    `;

    resultCard.style.display = "block";
}}

spinBtn.onclick = spin;

drawWheel();
</script>
""", height=1000)
