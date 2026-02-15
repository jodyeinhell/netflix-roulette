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

st.markdown("<h1 style='text-align:center; margin-top:10px;'>Netflix Roulette</h1>", unsafe_allow_html=True)

# ---------- Genre Dropdown ----------
all_genres = sorted(set(
    genre.strip()
    for genres in df["listed_in"]
    for genre in genres.split(",")
))

col1, col2, col3 = st.columns([2,3,2])
with col2:
    genre = st.selectbox(
        "Choose Genre",
        ["All"] + all_genres,
        label_visibility="collapsed"
    )

if genre == "All":
    filtered = df
else:
    filtered = df[df["listed_in"].str.contains(genre, na=False)]

movie_data_json = json.dumps(filtered.to_dict(orient="records"))

st.components.v1.html(f"""
<style>
* {{ font-family: Arial, sans-serif; }}

html, body {{
    margin:0;
    padding:0;
    overflow:hidden;
    background:#0e1117;
    color:white;
}}

#wrapper {{
    height:85vh;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
}}

#wheelContainer {{
    position:relative;
}}

#spinBtn {{
    position:absolute;
    top:50%;
    left:50%;
    transform:translate(-50%,-50%);
    width:110px;
    height:110px;
    border-radius:55px;
    border:1px solid #444;
    background:#1c1f26;
    color:#ccc;
    font-size:15px;
    cursor:pointer;
}}

#spinBtn:hover {{ background:#262a33; }}

#modal {{
    position:fixed;
    top:50%;
    left:50%;
    transform:translate(-50%,-50%);
    display:none;
}}

#modalContent {{
    background:#16181f;
    padding:30px;
    border-radius:18px;
    width:480px;
    text-align:center;
    box-shadow:0 0 30px rgba(170,200,255,0.5);
    position:relative;
}}

#closeBtn {{
    position:absolute;
    top:15px;
    right:20px;
    font-size:20px;
    cursor:pointer;
}}

#spinAgain {{
    margin-top:20px;
    padding:8px 18px;
    background:#1f232b;
    color:white;
    border:1px solid #444;
    border-radius:8px;
    cursor:pointer;
}}
</style>

<div id="wrapper">

<div id="wheelContainer">
    <canvas id="wheel" width="480" height="480"></canvas>
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
let lastTickIndex = null;

const tickAudio = new Audio("https://actions.google.com/sounds/v1/impacts/wood_plank_flicks.ogg");

function generateMovies(){{
    const shuffled=[...allMovies].sort(()=>0.5-Math.random());
    movies=shuffled.slice(0,50);
}}

function drawWheel(glow=false){{
    ctx.clearRect(0,0,canvas.width,canvas.height);
    const arc=(2*Math.PI)/slices;

    for(let i=0;i<slices;i++){{
        ctx.beginPath();
        ctx.moveTo(radius,radius);
        ctx.arc(radius,radius,radius-10,i*arc+angle,(i+1)*arc+angle);
        ctx.fillStyle=(i===winnerIndex && glow)?"#aac8ff":(i%2===0?"#1f232b":"#2a2f38");
        ctx.fill();

        ctx.save();
        ctx.translate(radius,radius);
        ctx.rotate(i*arc+arc/2+angle);
        ctx.textAlign="right";
        ctx.fillStyle="#ddd";
        ctx.font="9px Arial";
        ctx.fillText(movies[i].title.substring(0,18),radius-20,0);
        ctx.restore();
    }}

    ctx.beginPath();
    ctx.arc(radius,radius,65,0,2*Math.PI);
    ctx.fillStyle="#16181f";
    ctx.fill();

    ctx.fillStyle="#aaa";
    ctx.font="bold 14px Arial";
    ctx.textAlign="center";
    ctx.fillText(spinning?"SPINNING":"READY",radius,radius+5);

    // Arrow at top pointing DOWN
    ctx.beginPath();
    ctx.moveTo(radius,0);
    ctx.lineTo(radius-14,35);
    ctx.lineTo(radius+14,35);
    ctx.fillStyle="white";
    ctx.shadowBlur=0;
    ctx.fill();
}}

function spin(){{
    if(spinning) return;
    spinning=true;
    winnerIndex=null;
    generateMovies();

    winnerIndex=Math.floor(Math.random()*slices);

    const arc=(2*Math.PI)/slices;
    const targetRotation=(Math.PI*3/2)-(winnerIndex*arc+arc/2);

    const extraSpins=6*2*Math.PI;
    const finalAngle=targetRotation+extraSpins;

    const duration=4500;
    let start=null;
    const initialAngle=angle;

    function animate(timestamp){{
        if(!start) start=timestamp;
        const progress=timestamp-start;
        const t=Math.min(progress/duration,1);
        const ease=1-Math.pow(1-t,3);

        angle=initialAngle+(finalAngle-initialAngle)*ease;

        const currentIndex=Math.floor(((2*Math.PI-(angle%(2*Math.PI)))/(2*Math.PI))*slices)%slices;
        if(currentIndex!==lastTickIndex){{
            tickAudio.currentTime=0;
            tickAudio.play();
            lastTickIndex=currentIndex;
        }}

        drawWheel(false);

        if(t<1){{
            requestAnimationFrame(animate);
        }}else{{
            angle=finalAngle%(2*Math.PI);
            finish();
        }}
    }}

    requestAnimationFrame(animate);
}}

function finish(){{
    spinning=false;
    drawWheel(true);

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

    modal.style.display="block";
}}

spinBtn.onclick=spin;
closeBtn.onclick=()=>modal.style.display="none";
spinAgain.onclick=()=>{{ modal.style.display="none"; spin(); }};

generateMovies();
drawWheel();
</script>
""", height=720)
