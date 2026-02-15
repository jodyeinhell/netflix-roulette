import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Netflix Roulette", page_icon="🎬", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("netflix_us_movies_only.csv")
    df["listed_in"] = df["listed_in"].fillna("Unknown")
    return df

df = load_data()

st.markdown("<h1 style='text-align:center;'>Netflix Roulette</h1>", unsafe_allow_html=True)

# -------- Genre Selector --------
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

movie_data_json = json.dumps(filtered.to_dict(orient="records"))

st.components.v1.html(f"""
<style>
body {{
    background-color: #111;
    color: white;
}}

#spinBtn {{
    margin-top:25px;
    padding:14px 34px;
    font-size:18px;
    background:#2a2a2a;
    color:white;
    border:1px solid #444;
    border-radius:10px;
    cursor:pointer;
}}

#spinBtn:hover {{
    background:#333;
}}

#modal {{
    position:fixed;
    top:0;
    left:0;
    width:100%;
    height:100%;
    background:rgba(0,0,0,0.7);
    display:none;
    justify-content:center;
    align-items:center;
}}

#modalContent {{
    background:#1a1a1a;
    padding:30px;
    border-radius:14px;
    width:500px;
    text-align:center;
    box-shadow:0 0 30px rgba(150,180,255,0.5);
}}

#closeBtn {{
    position:absolute;
    top:15px;
    right:25px;
    font-size:22px;
    cursor:pointer;
    color:white;
}}
</style>

<div style="display:flex; flex-direction:column; align-items:center;">

<canvas id="wheel" width="650" height="650"></canvas>

<button id="spinBtn">SPIN</button>

</div>

<div id="modal">
    <div id="modalContent">
        <div id="closeBtn">✕</div>
        <div id="resultText"></div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>

<script>
const allMovies = {movie_data_json};
const canvas = document.getElementById("wheel");
const ctx = canvas.getContext("2d");
const spinBtn = document.getElementById("spinBtn");
const modal = document.getElementById("modal");
const resultText = document.getElementById("resultText");
const closeBtn = document.getElementById("closeBtn");

const radius = canvas.width / 2;

let angle = 0;
let slices = 50;
let movies = [];
let spinning = false;

function generateWheelMovies() {{
    const shuffled = [...allMovies].sort(() => 0.5 - Math.random());
    movies = shuffled.slice(0, 50);
}}

function drawWheel(glowColor=null) {{
    ctx.clearRect(0,0,canvas.width,canvas.height);
    const arc = (2 * Math.PI) / slices;

    for (let i=0; i<slices; i++) {{
        ctx.beginPath();
        ctx.moveTo(radius, radius);
        ctx.arc(radius, radius, radius-15, i*arc+angle, (i+1)*arc+angle);
        ctx.fillStyle = i % 2 == 0 ? "#2a2a2a" : "#3a3a3a";
        ctx.fill();

        ctx.save();
        ctx.translate(radius, radius);
        ctx.rotate(i*arc+arc/2+angle);
        ctx.textAlign = "right";
        ctx.fillStyle = "#ddd";
        ctx.font = "10px Arial";
        ctx.fillText(movies[i].title.substring(0,22), radius-30, 0);
        ctx.restore();
    }}

    if (glowColor) {{
        ctx.beginPath();
        ctx.arc(radius, radius, radius-10, 0, 2*Math.PI);
        ctx.strokeStyle = glowColor;
        ctx.lineWidth = 6;
        ctx.shadowColor = glowColor;
        ctx.shadowBlur = 15;
        ctx.stroke();
    }}

    ctx.beginPath();
    ctx.arc(radius, radius, 80, 0, 2*Math.PI);
    ctx.fillStyle = "#1a1a1a";
    ctx.fill();

    ctx.fillStyle = "#aaa";
    ctx.font = "bold 16px Arial";
    ctx.textAlign = "center";
    ctx.fillText(spinning ? "SPINNING..." : "READY", radius, radius+5);

    ctx.beginPath();
    ctx.moveTo(radius, 8);
    ctx.lineTo(radius-16, 55);
    ctx.lineTo(radius+16, 55);
    ctx.fillStyle = "white";
    ctx.fill();
}}

function spin() {{
    if (spinning) return;

    generateWheelMovies();
    spinning = true;
    let velocity = Math.random()*0.4 + 0.35;

    function animate() {{
        angle += velocity;
        velocity *= 0.985;

        drawWheel("rgba(255,255,255,0.15)");

        if (velocity > 0.002) {{
            requestAnimationFrame(animate);
        }} else {{
            spinning = false;
            finishSpin();
        }}
    }}

    animate();
}}

function finishSpin() {{
    const arc = (2 * Math.PI) / slices;
    const index = Math.floor(((2*Math.PI - (angle % (2*Math.PI))) / (2*Math.PI)) * slices) % slices;
    const selected = movies[index];

    drawWheel("rgba(170,200,255,0.6)");

    confetti({{
        particleCount: 200,
        spread: 120
    }});

    resultText.innerHTML = `
        <h2>${{selected.title}} (${{selected.release_year}}) [${{selected.rating || "NR"}}]</h2>
        <p><strong>Runtime:</strong> ${{selected.duration}}</p>
        <p><strong>Genre:</strong> ${{selected.listed_in}}</p>
        <p><strong>Director:</strong> ${{selected.director || "Unknown"}}</p>
    `;

    modal.style.display = "flex";
}}

spinBtn.onclick = spin;
closeBtn.onclick = () => modal.style.display = "none";

generateWheelMovies();
drawWheel();
</script>
""", height=950)
