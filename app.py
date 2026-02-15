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
* {{
    font-family: Arial, sans-serif;
}}

html, body {{
    margin:0;
    padding:0;
    overflow:hidden;
    background:#0f1117;
    color:white;
}}

#wrapper {{
    height:100vh;
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
}}

#wheelContainer {{
    position:relative;
}}

#spinBtn {{
    position:absolute;
    width:110px;
    height:110px;
    border-radius:55px;
    border:1px solid #444;
    background:#1c1f26;
    color:#ccc;
    font-size:15px;
    cursor:pointer;
}}

#spinBtn:hover {{
    background:#262a33;
}}

#modal {{
    position:fixed;
    top:0;
    left:0;
    width:100%;
    height:100%;
    backdrop-filter: blur(10px);
    background:rgba(0,0,0,0.6);
    display:none;
    justify-content:center;
    align-items:center;
}}

#modalContent {{
    background:#16181f;
    padding:35px;
    border-radius:18px;
    width:480px;
    text-align:center;
    box-shadow:0 0 35px rgba(170,200,255,0.5);
    position:relative;
}}

#modalContent h2 {{
    color:white;
    margin-bottom:10px;
}}

#modalContent p {{
    color:white;
    margin:6px 0;
}}

#closeBtn {{
    position:absolute;
    top:15px;
    right:20px;
    font-size:20px;
    cursor:pointer;
    color:white;
}}

#spinAgain {{
    margin-top:20px;
    padding:10px 20px;
    background:#1f232b;
    color:white;
    border:1px solid #444;
    border-radius:8px;
    cursor:pointer;
}}
</style>

<div id="wrapper">

<h1 style="margin-bottom:10px;">Netflix Roulette</h1>

<div id="wheelContainer">
    <canvas id="wheel" width="520" height="520"></canvas>
    <button id="spinBtn">SPIN</button>
</div>

</div>

<div id="modal">
    <div id="modalContent">
        <div id="closeBtn">✕</div>
        <div id="resultText"></div>
        <button id="spinAgain">Spin Again</button>
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
const spinAgain = document.getElementById("spinAgain");

const radius = canvas.width/2;
let slices = 50;
let movies = [];
let angle = 0;
let spinning = false;
let winnerIndex = null;

function generateMovies(){{
    const shuffled=[...allMovies].sort(()=>0.5-Math.random());
    movies=shuffled.slice(0,50);
}}

function drawWheel(){{
    ctx.clearRect(0,0,canvas.width,canvas.height);
    const arc=(2*Math.PI)/slices;

    for(let i=0;i<slices;i++){{
        ctx.beginPath();
        ctx.moveTo(radius,radius);
        ctx.arc(radius,radius,radius-12,i*arc+angle,(i+1)*arc+angle);
        ctx.fillStyle=i===winnerIndex?"#aac8ff":(i%2===0?"#1f232b":"#2a2f38");
        ctx.fill();

        ctx.save();
        ctx.translate(radius,radius);
        ctx.rotate(i*arc+arc/2+angle);
        ctx.textAlign="right";
        ctx.fillStyle="#ddd";
        ctx.font="9px Arial";
        ctx.fillText(movies[i].title.substring(0,20),radius-25,0);
        ctx.restore();
    }}

    ctx.beginPath();
    ctx.arc(radius,radius,70,0,2*Math.PI);
    ctx.fillStyle="#16181f";
    ctx.fill();

    ctx.fillStyle="#aaa";
    ctx.font="bold 14px Arial";
    ctx.textAlign="center";
    ctx.fillText(spinning?"SPINNING...":"READY",radius,radius+5);

    ctx.beginPath();
    ctx.moveTo(radius,6);
    ctx.lineTo(radius-12,40);
    ctx.lineTo(radius+12,40);
    ctx.fillStyle="white";
    ctx.fill();
}}

function spin(){{
    if(spinning) return;
    spinning=true;
    winnerIndex=null;
    generateMovies();

    let velocity=Math.random()*0.4+0.35;

    function animate(){{
        angle+=velocity;
        velocity*=0.985;
        drawWheel();

        if(velocity>0.002){{
            requestAnimationFrame(animate);
        }}else{{
            finish();
        }}
    }}
    animate();
}}

function finish(){{
    spinning=false;
    const arc=(2*Math.PI)/slices;
    winnerIndex=Math.floor(((2*Math.PI-(angle%(2*Math.PI)))/(2*Math.PI))*slices)%slices;
    drawWheel();

    confetti({{
        particleCount:200,
        spread:130
    }});

    const selected=movies[winnerIndex];

    resultText.innerHTML=`
        <h2>${{selected.title}} (${{selected.release_year}}) [${{selected.rating||"NR"}}]</h2>
        <p><strong>Runtime:</strong> ${{selected.duration}}</p>
        <p><strong>Genre:</strong> ${{selected.listed_in}}</p>
        <p><strong>Director:</strong> ${{selected.director||"Unknown"}}</p>
    `;

    modal.style.display="flex";
}}

spinBtn.onclick=spin;
closeBtn.onclick=()=>modal.style.display="none";
spinAgain.onclick=()=>{{ modal.style.display="none"; spin(); }};

generateMovies();
drawWheel();
</script>
""", height=820)
