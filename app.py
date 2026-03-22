from fileinput import filename
import streamlit as st
import random
import base64
import os
import datetime
import time
import numpy as np
import plotly.graph_objects as go
import streamlit.components.v1 as components
import json

# --- THE AUTO-ANIMATING WAVEFORM ENGINE (SCROLL FIX) ---
def build_auto_wave_chart(probs, num_qubits, max_state):

    states = [format(i, f'0{num_qubits}b') for i in range(2**num_qubits)]
    
    bars_html = ""
    for s in states:
        p = probs.get(s, 0.0)
        height_pct = p * 100
        
        if s == max_state and p > 0:
            color, shadow = "#00FFCC", "0 0 15px #00FFCC"
        elif p > 0.4:
            color, shadow = "#FFD700", "0 0 15px #FFD700"
        elif p > 0.005:
            color, shadow = "#ff4b4b", "0 0 15px #ff4b4b"
        else:
            color, shadow = "#555555", "none"

        bars_html += f"""
        <div style="display: flex; flex-direction: column; align-items: center; width: 100%; min-width: 60px;">
            <div style="height: 160px; width: 80px; background: rgba(255,255,255,0.2); border-radius: 6px; position: relative; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); box-shadow: inset 0 0 100px rgba(0,0,0,1);">
                <div class="bar-fill" data-height="{height_pct}%" style="position: absolute; bottom: 0; left: 0; width: 100%; height: 0%; background: {color}; box-shadow: {shadow}; transition: height 3s cubic-bezier(0.6, 0.8, 0.2, 1);"></div>
            </div>
            <div style="color: {color}; font-family: 'Orbitron', sans-serif; font-size: 14px; margin-top: 12px; font-weight: bold;">|{s}⟩</div>
            <div style="color: #FFF; font-family: 'JetBrains Mono', monospace; font-size: 12px; margin-top: 4px;">{height_pct:.1f}%</div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @font-face {{ 
                font-family: 'Orbitron'; 
                src: url('{assets_b64.get("orbitron.ttf", "")}') format('truetype'); 
            }}
            @font-face {{ 
                font-family: 'JetBrains Mono'; 
                src: url('{assets_b64.get("jetbrains.ttf", "")}') format('truetype'); 
            }}
            body {{ margin: 0; background: transparent; overflow: hidden; height: 100vh; width: 100vw; display: flex; justify-content: center; }}
            #scroll-container {{
                display: flex; overflow-x: auto; overflow-y: hidden; 
                max-width: 100%; height: 100%; padding-top: 10px; padding-bottom: 20px; 
                gap: 100px; box-sizing: border-box; align-items: flex-start;
            }}
            ::-webkit-scrollbar {{ height: 10px; }}
            ::-webkit-scrollbar-track {{ background: rgba(0, 0, 0, 0.3); border-radius: 5px; }}
            ::-webkit-scrollbar-thumb {{ background: rgba(255, 215, 0, 0.4); border-radius: 5px; border: 1px solid rgba(255, 215, 0, 0.2); }}
        </style>
    </head>
    <body>
        <div id="scroll-container">
            {bars_html}
        </div>
        <script>
            setTimeout(() => {{
                document.querySelectorAll('.bar-fill').forEach(fill => {{
                    fill.style.height = fill.getAttribute('data-height');
                }});
            }}, 50);
        </script>
    </body>
    </html>
    """

# --- THE UNIFIED SIDE-SCROLLING THREE.JS ENGINE (SCROLL FIX) ---
def build_all_threejs_blochs(state_vec, num_qubits):
    bloch_data = []
    for i in range(num_qubits):
        trace_qubits = [j for j in range(num_qubits) if j != i]
        reduced_rho = partial_trace(state_vec, trace_qubits)
        x_v, y_v, z_v = [reduced_rho.expectation_value(Pauli(p)).real for p in ['X', 'Y', 'Z']]
        vec_len = np.sqrt(x_v**2 + y_v**2 + z_v**2)
        if vec_len < 0.01: x_v, y_v, z_v = 0, 0, 0.001
        bloch_data.append({"id": i, "x": round(x_v,4), "y": round(y_v,4), "z": round(z_v,4)})
    
    data_json = json.dumps(bloch_data)
   
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="{assets_b64.get('three.min.js', '')}"></script>
        <style>
            @font-face {{ 
                font-family: 'Orbitron'; 
                src: url('{assets_b64.get("orbitron.woff2", "")}') format('woff2'); 
            }}
            
            body {{ 
                margin: 0; 
                overflow: hidden; 
                background: transparent; 
                user-select: none; 
                font-family: 'Orbitron', sans-serif; 
                height: 100vh; 
                width: 100vw; 
                display: flex; 
                justify-content: center; 
            }}
            
            ::-webkit-scrollbar {{ height: 12px; }}
            ::-webkit-scrollbar-track {{ background: rgba(0, 0, 0, 0.3); border-radius: 6px; }}
            ::-webkit-scrollbar-thumb {{ background: rgba(255, 215, 0, 0.4); border-radius: 6px; border: 1px solid rgba(255, 215, 0, 0.2); }}
            ::-webkit-scrollbar-thumb:hover {{ background: rgba(255, 215, 0, 0.8); }}

            #wrapper {{ 
                display: flex; 
                overflow-x: auto; 
                overflow-y: hidden; 
                max-width: 100%; 
                height: 100%; 
                padding: 10px 20px 20px 20px; 
                box-sizing: border-box; 
                gap: 80px; /* Internal spacing between spheres */
                align-items: center; 
            }}
            
            .q-container {{ position: relative; min-width: 350px; height: 350px; flex: 0 0 auto; }}
            .label {{ position: absolute; color: #FFD700; font-size: 11px; text-shadow: 0 0 8px rgba(0,0,0,1); font-weight: bold; transform: translate(-50%, -50%); transition: opacity 0.2s; pointer-events: none; }}
            .q-title {{ position: absolute; top: -10px; left: 50%; transform: translateX(-50%); color: #FF0000; font-size: 16px; text-shadow: 0 0 10px rgba(255,0,0,0.5); pointer-events: none; width: 100%; text-align: center; }}
        </style>
    </head>
    <body>
        <div id="wrapper"></div>
        <script>
            const qData = {data_json};
            const scenes = [];
            const renderers = [];
            const cameras = [];
            const updateLabelsArr = [];
            const pulseData = [];

            const wrapper = document.getElementById('wrapper');

            qData.forEach(q => {{
                const cont = document.createElement('div');
                cont.className = 'q-container';
                
                cont.innerHTML = `
                    <div class="q-title">QUBIT ${{q.id}}</div>
                    <div id="lX_${{q.id}}" class="label">X</div><div id="lnX_${{q.id}}" class="label">-X</div>
                    <div id="lY_${{q.id}}" class="label">Y</div><div id="lnY_${{q.id}}" class="label">-Y</div>
                    <div id="lZ_${{q.id}}" class="label">Z (|0&gt;)</div><div id="lnZ_${{q.id}}" class="label">-Z (|1&gt;)</div>
                `;
                wrapper.appendChild(cont);

                const scene = new THREE.Scene();
                scenes.push(scene);

                const camera = new THREE.PerspectiveCamera(45, 350 / 350, 0.1, 1000);
                camera.position.set(4.0, 3.0, 5.5);
                camera.lookAt(0, 0, 0);
                cameras.push(camera);

                const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
                renderer.setSize(350, 350);
                cont.appendChild(renderer.domElement);
                renderers.push(renderer);

                const sphereMat = new THREE.MeshBasicMaterial({{ color: 0xffffff, wireframe: true, transparent: true, opacity: 0.05 }});
                scene.add(new THREE.Mesh(new THREE.SphereGeometry(2, 24, 24), sphereMat));

                const circlePoints = [];
                for (let i = 0; i <= 64; i++) {{
                    const a = (i/64)*Math.PI*2;
                    circlePoints.push(new THREE.Vector3(Math.cos(a)*2, Math.sin(a)*2, 0));
                }}
                const cGeo = new THREE.BufferGeometry().setFromPoints(circlePoints);
                const lMat = new THREE.LineBasicMaterial({{ color: 0xffffff, transparent: true, opacity: 0.2 }});
                
                const eq = new THREE.LineLoop(cGeo, lMat); eq.rotation.x = Math.PI/2; scene.add(eq);
                scene.add(new THREE.LineLoop(cGeo, lMat));
                const m2 = new THREE.LineLoop(cGeo, lMat); m2.rotation.y = Math.PI/2; scene.add(m2);

                const dir = new THREE.Vector3(q.y, q.z, q.x); 
                const magnitude = dir.length(); 
                const normalizedDir = dir.clone().normalize();
                const arrowLength = Math.max(0.1, magnitude * 2); 
                const hLen = Math.min(0.4, arrowLength * 0.3);
                const hWid = Math.min(0.2, hLen * 0.5);

                const arrow = new THREE.ArrowHelper(normalizedDir, new THREE.Vector3(0,0,0), arrowLength, 0xFFD700, hLen, hWid);
                scene.add(arrow);

                const tipLight = new THREE.PointLight(0xFFD700, 2, 3);
                scene.add(tipLight);

                pulseData.push({{
                    magnitude: magnitude,
                    arrow: arrow,
                    tipLight: tipLight,
                    normalizedDir: normalizedDir,
                    arrowLength: arrowLength
                }});

                const pts = {{
                    [`lX_${{q.id}}`]:  new THREE.Vector3(0, 0, 2.3),  [`lnX_${{q.id}}`]: new THREE.Vector3(0, 0, -2.3),
                    [`lY_${{q.id}}`]:  new THREE.Vector3(2.3, 0, 0),  [`lnY_${{q.id}}`]: new THREE.Vector3(-2.3, 0, 0),
                    [`lZ_${{q.id}}`]:  new THREE.Vector3(0, 2.3, 0),  [`lnZ_${{q.id}}`]: new THREE.Vector3(0, -2.3, 0)
                }};

                updateLabelsArr.push(() => {{
                    Object.keys(pts).forEach(id => {{
                        const v = pts[id].clone().applyMatrix4(scene.matrixWorld);
                        const dist = v.distanceTo(camera.position);
                        v.project(camera);
                        const el = document.getElementById(id);
                        if(el) {{
                            el.style.left = `${{(v.x * .5 + .5) * 350}}px`;
                            el.style.top = `${{(v.y * -.5 + .5) * 350}}px`;
                            el.style.opacity = dist > 6.0 ? 0.2 : 1.0;
                        }}
                    }});
                }});
            }});

            let frameCount = 0;
            function animate() {{
                requestAnimationFrame(animate);
                frameCount += 0.05;

                scenes.forEach((scene, i) => {{
                    scene.rotation.y += 0.006;
                    
                    const pd = pulseData[i];
                    const pulseSpeed = 1.0 + (pd.magnitude * 2.0);
                    const pulseIntensity = 0.5 + (Math.sin(frameCount * pulseSpeed) * 0.5 * pd.magnitude);
                    
                    pd.arrow.line.material.color.setHSL(0.12, 1.0, 0.4 + (pulseIntensity * 0.3));
                    pd.tipLight.intensity = pulseIntensity * 2.5;
                    
                    const tipPos = pd.normalizedDir.clone().multiplyScalar(pd.arrowLength);
                    pd.tipLight.position.copy(tipPos);

                    renderers[i].render(scene, cameras[i]);
                    updateLabelsArr[i]();
                }});
            }}
            animate();
        </script>
    </body>
    </html>
    """
    return html_code

try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector, partial_trace, Pauli
except ImportError:
    st.error("Qiskit not installed. Please check your dependencies.")
    st.stop()

st.set_page_config(page_title="QuantumLens v4.0", layout="wide", initial_sidebar_state="expanded")
st.sidebar.title("QuantumLens")
NUM_QUBITS = st.sidebar.slider("CORE QUBIT COUNT", min_value=1, max_value=10, value=2, help="Warning: High qubit counts may cause computer Brain lag.")
st.sidebar.caption(f"v1 - {NUM_QUBITS}-Qubit Engine")

if 'qc' not in st.session_state or st.session_state.qc.num_qubits != NUM_QUBITS:
    st.session_state.qc = QuantumCircuit(NUM_QUBITS)
    st.session_state.last_result = None
    st.session_state.log = [f"System Online: {NUM_QUBITS}-Qubit Engine Initialized..."]

if 'tutorial_step' not in st.session_state:
    st.session_state.tutorial_step = 0 
if 'booted' not in st.session_state:
    st.session_state.booted = False
if 'is_glitching' not in st.session_state:
    st.session_state.is_glitching = False

def add_log(msg):
    """Appends a time-stamped message to the system log in the session state."""
    t = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.log.append(f"[{t}] {msg}")

@st.cache_resource
def load_offline_assets():
    # This gets the folder WHERE your script actually lives
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # This joins it to the 'assets' folder
    assets_dir = os.path.join(script_dir, "assets")
    
    files = ["bg.jpg", "orbitron.ttf", "jetbrains.ttf", "three.min.js"]
    encoded = {}
    
    for filename in files:
        filepath = os.path.join(assets_dir, filename)
        # Check if file exists before trying to open it
        if not os.path.exists(filepath):
            print(f"CRITICAL ERROR: {filename} NOT FOUND at {filepath}")
            encoded[filename] = ""
            continue
            
        try:
            with open(filepath, "rb") as f:
                if filename.endswith(".js"): mime = "text/javascript"
                elif filename.endswith(".ttf"): mime = "font/ttf"
                else: mime = "image/jpeg"
                
                encoded[filename] = f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"
        except Exception as e:
            encoded[filename] = ""
    return encoded

assets_b64 = load_offline_assets()

bg_image_css = f"url('{assets_b64.get('bg.jpg', '')}')" if assets_b64.get('bg.jpg') else "none"
custom_css = f"""
<style>
/* 1. THE CRITICAL OFFLINE FONT FIX */
@font-face {{ 
    font-family: 'Orbitron Local'; 
    src: url('{assets_b64.get('orbitron.ttf', '')}') format('truetype'); 
    font-weight: normal; 
}}
@font-face {{ 
    font-family: 'JetBrains Mono Local'; 
    src: url('{assets_b64.get('jetbrains.ttf', '')}') format('truetype'); 
    font-weight: normal; 
}}

/* 2. APPLY TO HEADERS */
h1, h2, h3, .stHeader, [data-testid="stHeader"] h1, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, h4 {{
    font-family: 'Orbitron Local', 'Orbitron', sans-serif !important;
    color: #FFD700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    text-shadow: 2px 2px 10px rgba(255, 215, 0, 0.4) !important;
    font-weight: 800 !important;
}}

/* 3. APPLY TO BODY/CODE */
html, body, [data-testid="stMarkdownContainer"] p, .stCode, .stText, [class*="css"], .circuit-code {{
    font-family: 'JetBrains Mono Local', 'JetBrains Mono', monospace !important;
}}

.circuit-code {{
    background-color: rgba(0, 0, 0, 0.6) !important;
    backdrop-filter: blur(15px) saturate(180%) !important;
    color: #FFD700 !important;
    padding: 20px !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255, 215, 0, 0.3) !important;
    line-height: 1 !important;
    overflow-x: auto;
}}

html, body, [data-testid="stMarkdownContainer"] p, .stCode, .stText, [class*="css"] {{
    font-family: 'JetBrains Mono', 'JetBrains Mono Local', monospace !important;
}}

h1, h2, h3, .stHeader, [data-testid="stHeader"] h1, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, h3 {{
    font-family: 'Orbitron', 'Orbitron Local', sans-serif !important;
    color: #FFD700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    text-shadow: 2px 2px 10px rgba(255, 215, 0, 0.4) !important;
    font-weight: 800 !important;
}}

[data-testid="stAppViewContainer"] {{
    background: linear-gradient(rgba(10, 15, 20, 0.6), rgba(5, 10, 15, 0.8)), {bg_image_css};
    background-size: cover; background-attachment: fixed; background-position: center;
    color: #E0E0E0;
}}

.bg-glitch-layer {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: linear-gradient(rgba(10, 15, 20, 0.6), rgba(5, 10, 15, 0.8)), {bg_image_css};
    background-size: cover; background-position: center;
    z-index: 0; pointer-events: none; opacity: 0; mix-blend-mode: screen;
    animation: bg_glitch_anim 7s infinite linear;
}}
@keyframes bg_glitch_anim {{
    0%, 93% {{ opacity: 0; transform: scale(1.04) translate(0,0); filter: brightness(1) hue-rotate(0deg); }}
    94% {{ opacity: 0.8; transform: scale(1.07) translate(-10px, 5px); filter: brightness(2) hue-rotate(90deg); clip-path: polygon(0 20%, 100% 20%, 100% 30%, 0 30%); }}
    95% {{ opacity: 0; }}
    96% {{ opacity: 0.9; transform: scale(1.02) translate(10px, -5px); filter: invert(0.8) hue-rotate(-90deg); clip-path: polygon(0 60%, 100% 60%, 100% 75%, 0 75%); }}
    97%, 100% {{ opacity: 0; transform: scale(1.04) translate(0,0); }}
}}
.vignette {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: radial-gradient(circle, transparent 45%, rgba(0,0,0,0.95) 120%);
    pointer-events: none; z-index: 10;
}}
.heat-shimmer {{
    position: fixed; top: 40%; left: 50%; width: 600px; height: 800px;
    transform: translate(-50%, -50%);
    background: radial-gradient(ellipse, rgba(255, 215, 0, 0.15) 0%, rgba(255, 140, 0, 0.05) 40%, transparent 70%);
    mix-blend-mode: screen; filter: blur(25px); z-index: 0; pointer-events: none;
    animation: core_random_glow 8s infinite;
}}

@keyframes breathe {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.01); }} 100% {{ transform: scale(1); }} }}
@keyframes core_random_glow {{
    0%, 100% {{ opacity: 0.3; transform: translate(-50%, -50%) scale(1); }}
    10% {{ opacity: 0.7; transform: translate(-50%, -50%) scale(1.02); }}
    20% {{ opacity: 0.2; transform: translate(-50%, -50%) scale(0.98); }}
    30% {{ opacity: 0.6; transform: translate(-50%, -50%) scale(1.05); }}
    40% {{ opacity: 0.4; transform: translate(-50%, -50%) scale(1.01); }}
    50% {{ opacity: 0.9; transform: translate(-50%, -50%) scale(1.03); }}
    60% {{ opacity: 0.3; transform: translate(-50%, -50%) scale(0.95); }}
    70% {{ opacity: 0.8; transform: translate(-50%, -50%) scale(1.08); }}
    80% {{ opacity: 0.5; transform: translate(-50%, -50%) scale(1); }}
    90% {{ opacity: 0.2; transform: translate(-50%, -50%) scale(1.02); }}
}}
@keyframes typing {{ from {{ width: 0 }} to {{ width: 100% }} }}
@keyframes blink-caret {{ from, to {{ border-color: transparent }} 50% {{ border-color: #FFD700; }} }}
@keyframes pulse_shimmer {{
    0% {{ opacity: 0.4; border-color: rgba(255, 215, 0, 0.1); }}
    50% {{ opacity: 0.8; border-color: rgba(255, 215, 0, 0.4); box-shadow: 0 0 10px rgba(255,215,0,0.2) }}
    100% {{ opacity: 0.4; border-color: rgba(255, 215, 0, 0.1); }}
}}
.shimmer-box {{
    animation: pulse_shimmer 3s infinite ease-in-out !important;
    border: 1px dashed rgba(255, 215, 0, 0.5) !important;
    background-color: rgba(0, 0, 0, 0.4) !important;
}}

.hud-box {{
    animation: breathe 6s infinite ease-in-out;
    background: linear-gradient(135deg, rgba(20,20,30,0.6), rgba(10,10,15,0.8));
    backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 16px;
    padding: 1.5rem; transition: all 0.2s ease-in-out; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
}}
.hud-box:hover {{
    transform: translateY(-2px); border: 1px solid rgba(255, 215, 0, 0.4);
    background: linear-gradient(135deg, rgba(30,30,40,0.7), rgba(15,15,20,0.9));
    box-shadow: 0 8px 25px rgba(255, 215, 0, 0.15);
}}

div.stButton > button {{
    transition: all 0.2s ease-in-out !important;
    font-family: 'Orbitron', 'Orbitron Local', sans !important;
    text-transform: uppercase !important; letter-spacing: 1.5px !important;
    background: linear-gradient(135deg, rgba(255,69,0,0.1), rgba(255,215,0,0.1)) !important;
    border: 1px solid rgba(255, 120, 0, 0.4) !important; border-radius: 8px !important;
}}
div.stButton > button > div > p {{
    background: linear-gradient(90deg, #FF4500, #FFD700);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important;
}}
div.stButton > button:hover {{
    transform: scale(1.05) !important;
    background: linear-gradient(135deg, rgba(255,69,0,0.3), rgba(255,215,0,0.3)) !important;
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.5) !important; border: 1px solid #FFD700 !important;
}}
div.stButton > button:active {{
    transform: scale(0.95) !important; background: #FFF !important;
    box-shadow: 0 0 40px #FFF !important; transition: all 0.05s !important;
}}

.briefing-text div.stButton {{ animation: delayedReveal 3s ease forwards; opacity: 0; }}
@keyframes delayedReveal {{ 0%, 70% {{ opacity: 0; transform: translateY(10px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}

.briefing-text {{
    background: linear-gradient(135deg, rgba(0,0,0,0.85), rgba(0,0,0,0.6));
    padding: 35px; border-radius: 15px; border-left: 5px solid #FFD700;
    margin-bottom: 20px; border-top: 1px solid rgba(255,255,255,0.1);
    border-right: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 8px 30px rgba(0,0,0,0.8); transition: all 0.3s ease;
}}
.briefing-text:hover {{ box-shadow: 0 10px 40px rgba(0,0,0,0.9); border-left: 5px solid #FF4500; }}

[data-testid="stSidebar"] {{
    background: rgba(10, 15, 25, 0.3) !important;
    backdrop-filter: blur(30px) saturate(150%) !important;
    -webkit-backdrop-filter: blur(30px) saturate(150%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.15) !important; box-shadow: 5px 0 30px rgba(0, 0, 0, 0.6) !important;
}}
[data-testid="stSidebar"] > div:first-child {{ background-color: transparent !important; }}
#MainMenu, footer {{visibility: hidden;}}
header {{background: transparent !important;}}

</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("""<div class="vignette"></div><div class="bg-glitch-layer"></div><div class="heat-shimmer"></div>""", unsafe_allow_html=True)

if not st.session_state.booted:
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: #050505 !important; }
    header, [data-testid="stSidebar"], .vignette, .bg-glitch-layer, .heat-shimmer { display: none !important; }
    .term-text { font-family: 'JetBrains Mono', monospace; color: #2ecc71; text-shadow: 0 0 8px rgba(46, 204, 113, 0.4); font-size: 1.1rem; margin-bottom: 0.5rem; }
    .term-error { color: #e74c3c; text-shadow: 0 0 8px rgba(231, 76, 60, 0.6); }
    .term-blink { animation: blinker 1s steps(2, start) infinite; padding-left: 4px; }
    @keyframes blinker { to { visibility: hidden; } }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("<h1 style='color:#2ecc71;font-family:Orbitron;text-shadow:0 0 10px #2ecc71;'>SYSTEM BOOT</h1>", unsafe_allow_html=True)
    st.divider()
    term_ph, prog_ph, warn_ph = st.empty(), st.empty(), st.empty()
    lines = []
    logs = ["Initializing quantum entanglement matrix...", "Calibrating superconducting qubits... [OK]", "Bypassing firewall protocols... [ACCESS GRANTED]", "Loading Wavefunction protocols..."]
    for i, p in enumerate([15, 42, 78, 92]):
        lines.append(f"> {logs[i]}")
        term_ph.markdown(f"<div class='term-text'>{'<br>'.join(lines)}</div>", unsafe_allow_html=True)
        bar = "█" * (p // 5) + "░" * (20 - (p // 5))
        prog_ph.markdown(f"<div class='term-text'>[{bar}] {p}% <span class='term-blink'>_</span></div>", unsafe_allow_html=True)
        time.sleep(0.35)
    warn_ph.markdown("<div class='term-text term-error'><br>⚠ WARNING: QUANTUM INSTABILITY DETECTED<br>⚠ STABILIZING CORE TEMPERATURE...</div>", unsafe_allow_html=True)
    time.sleep(1.8)
    warn_ph.empty()
    lines.append("> Core stabilized. Handshake confirmed.")
    term_ph.markdown(f"<div class='term-text'>{'<br>'.join(lines)}</div>", unsafe_allow_html=True)
    prog_ph.markdown(f"<div class='term-text'>[{'█'*20}] 100%</div>", unsafe_allow_html=True)
    time.sleep(1.0)
    st.session_state.booted = True
    st.rerun()

if st.session_state.is_glitching:
    st.markdown("""
    <style>
    body, [data-testid="stAppViewContainer"] { animation: glitch_flicker 0.4s linear infinite; }
    @keyframes glitch_flicker {
        0% { filter: invert(0) hue-rotate(0deg); }
        10% { filter: invert(1) hue-rotate(180deg); opacity: 0.8; }
        20% { filter: invert(0); transform: translateX(10px); }
        30% { transform: translateX(-10px); }
        40% { transform: scale(1.05); }
        100% { filter: invert(0); opacity: 0; }
    }
    .blackout { position:fixed; top:0; left:0; width:100vw; height:100vh; background:black; z-index:99999; animation: fadeToBlack 0.8s forwards; }
    @keyframes fadeToBlack { 0% {opacity: 0;} 100% {opacity: 1;} }
    </style>
    <div class="blackout"></div>
    """, unsafe_allow_html=True)
    time.sleep(1.1)
    st.session_state.is_glitching = False
    st.session_state.tutorial_step = 1
    st.rerun()

if st.session_state.tutorial_step < 5:
    st.markdown(f"""
        <style>
        @font-face {{ 
            font-family: 'Orbitron'; 
            src: url('{assets_b64.get('orbitron.ttf', '')}') format('truetype'); 
        }}
        @font-face {{ 
            font-family: 'JetBrains Mono'; 
            src: url('{assets_b64.get('jetbrains.ttf', '')}') format('truetype'); 
        }}
        .briefing-text h2 {{
            font-family: 'Orbitron', sans-serif !important;
            color: #FFD700 !important;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
            margin-top: 0;
        }}
        .briefing-text p {{
            font-family: 'JetBrains Mono', monospace !important;
            color: #E0E0E0 !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='briefing-text'>", unsafe_allow_html=True)
        
        # --- STEP 0: INITIALIZATION ---
        if st.session_state.tutorial_step == 0:
            st.markdown(f"""
            <div style="font-family:'Orbitron', sans-serif; font-size: 2.2rem; color:#FFF; text-shadow: 0 0 20px rgba(255,215,0,0.8); white-space: nowrap; overflow: hidden; border-right: 0.15em solid #FFD700; display: inline-block; animation: typing 2.5s steps(35, end) forwards, blink-caret 0.75s step-end infinite;">
                INITIALIZING MISSION CRITICAL SYSTEMS
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<p style="margin-top:15px;">Welcome, Lead Researcher. QuantumLens v4.0 is now online.</p>', unsafe_allow_html=True)
            
            if st.button("PROCEED TO BRIEFING"):
                st.session_state.is_glitching = True
                st.rerun()

        # --- STEP 1: SUPERPOSITION ---
        elif st.session_state.tutorial_step == 1:
            st.markdown("<h2>I. THE SUPERPOSITION PRINCIPLE</h2>", unsafe_allow_html=True)
            st.markdown('<p>In classical logic, a bit is binary. In this lab, a Qubit exists as a linear combination of |0⟩ and |1⟩.</p>', unsafe_allow_html=True)
            st.markdown('<p style="color: #00FFCC !important; font-size: 0.9rem;">TELEMETRY: Hadamard (H) Gate active.</p>', unsafe_allow_html=True)
            if st.button("DECODE ENTANGLEMENT"):
                st.session_state.tutorial_step = 2
                st.rerun()

        # --- STEP 2: ENTANGLEMENT ---
        elif st.session_state.tutorial_step == 2:
            st.markdown("<h2>II. QUANTUM ENTANGLEMENT</h2>", unsafe_allow_html=True)
            st.markdown('<p>By engaging the <b>CX-Gate</b>, we link the fates of Q_0 and Q_1.</p>', unsafe_allow_html=True)    
            st.markdown('<p style="color: #ff4b4b !important; font-size: 0.9rem;">WARNING: Measuring one entangled qubit affects the other.</p>', unsafe_allow_html=True)
            if st.button("DECODE MEASUREMENT"):
                st.session_state.tutorial_step = 3
                st.rerun()

        # --- STEP 3: COLLAPSE ---
        elif st.session_state.tutorial_step == 3:
            st.markdown("<h2>III. WAVEFUNCTION COLLAPSE</h2>", unsafe_allow_html=True)
            st.markdown('<p>The Observer Effect is final. When you hit MEASURE, the superposition vanishes.</p>', unsafe_allow_html=True)
            if st.button("INITIALIZE LAB"):
                st.session_state.tutorial_step = 5 
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("SKIP SYSTEM BRIEFING"):
            st.session_state.tutorial_step = 5
            st.rerun()
        st.divider()

# --- 4. ENGINE MATH & LOGIC ---
state = Statevector.from_instruction(st.session_state.qc)
probs = state.probabilities_dict()
max_state = max(probs, key=probs.get) if probs else "0" * NUM_QUBITS

if st.session_state.last_result:
    collapse_probs = {format(i, f'0{NUM_QUBITS}b'): 0.0 for i in range(2**NUM_QUBITS)}
    collapse_probs[st.session_state.last_result] = 1.0
else:
    collapse_probs = probs

st.header("QUANTUM STATE VISUALIZATION")
st.subheader("WAVE FUNCTION FIELD")
wave_html = build_auto_wave_chart(collapse_probs, NUM_QUBITS, max_state)
components.html(wave_html, height=260)

# --- 5. SIDEBAR ---
with st.sidebar:  
    adv_mode = st.toggle("ADVANCED RESEARCH MODE", value=False)
    st.divider()
    
    st.subheader("1. Target Select")
    target = st.radio("Target:", list(range(NUM_QUBITS)), horizontal=True, format_func=lambda x: f"Qubit {x}")
    
    st.subheader("2. Apply Gates")
    c1, c2 = st.columns(2)
    with c1:
        if st.button('Hadamard (H)', use_container_width=True):
            with st.spinner("Calibrating Phase..."): time.sleep(0.15)
            st.session_state.qc.h(target)
            st.session_state.last_result = None
            add_log(f"H-Gate on Q_{target}")
            st.rerun()
        if st.button('X-Gate', use_container_width=True):
            st.session_state.qc.x(target)
            st.session_state.last_result = None
            add_log(f"X-Gate on Q_{target}")
            st.rerun()
    with c2:
        if st.button('Z-Gate', use_container_width=True):
            st.session_state.qc.z(target)
            st.session_state.last_result = None
            add_log(f"Z-Gate on Q_{target}")
            st.rerun()
            
    if not adv_mode and NUM_QUBITS > 1:
        if st.button('CX-Gate (Entangle)', use_container_width=True):
            st.session_state.qc.cx(0, 1)
            st.session_state.last_result = None
            add_log("Entanglement: Q_0 ↔ Q_1")
            st.rerun()
            
    if adv_mode:
        st.divider()
        st.markdown("### CUSTOM ROUTING")
        c_q = st.selectbox("Control Qubit", list(range(NUM_QUBITS)), index=0)
        t_q = st.selectbox("Target Qubit", list(range(NUM_QUBITS)), index=1 if NUM_QUBITS > 1 else 0)
        
        if st.button("EXECUTE CX-GATE", use_container_width=True):
            if c_q == t_q: 
                st.error("Target & Control must differ.")
            else:
                st.session_state.qc.cx(c_q, t_q)
                st.session_state.last_result = None
                add_log(f"CX-Gate: Q_{c_q} → Q_{t_q}")
                st.rerun()
                
        st.markdown("### CONTINUOUS ROTATION")
        theta = st.slider("Theta (θ)", 0.0, 2.0, 0.5, step=0.1, format="%f π")
        if st.button("APPLY RY-ROTATION", use_container_width=True):
            st.session_state.qc.ry(theta * np.pi, target)
            st.session_state.last_result = None
            add_log(f"RY({theta}π) on Q_{target}")
            st.rerun()
    
    st.divider()
    st.subheader("3. Execute")
    if st.button('MEASURE WAVEFUNCTION', type="primary", use_container_width=True):
        with st.spinner("Collapsing Wavefunction..."): 
            time.sleep(0.3)
        res = random.choices(list(probs.keys()), weights=list(probs.values()))[0]
        st.session_state.last_result = res
        
        st.session_state.qc = QuantumCircuit(NUM_QUBITS)
        for i, bit in enumerate(reversed(res)):
            if bit == '1': st.session_state.qc.x(i)
                
        add_log(f"COLLAPSE: |{res}>")
        st.rerun()

    if st.button('Reset System', use_container_width=True):
        st.session_state.qc = QuantumCircuit(NUM_QUBITS)
        st.session_state.last_result = None
        st.session_state.log = ["System Rebooted..."]
        st.rerun()

    st.divider()
    st.subheader("System Log")
    st.code("\n".join(st.session_state.log[-15:]), language="text")

# --- 6. MAIN AREA ---
st.markdown("### AMPLITUDE TELEMETRY")

telemetry_html = '<style>::-webkit-scrollbar { height: 10px; } ::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.3); border-radius: 5px; } ::-webkit-scrollbar-thumb { background: rgba(255, 215, 0, 0.4); border-radius: 5px; border: 1px solid rgba(255, 215, 0, 0.2); } ::-webkit-scrollbar-thumb:hover { background: rgba(255, 215, 0, 0.8); }</style><div style="display: flex; width: 100%; justify-content: center;"><div style="display: flex; overflow-x: auto; gap: 60px; padding-bottom: 20px; padding-top: 10px; max-width: 100%;">'

for i in range(2 ** NUM_QUBITS):
    state_str = format(i, f'0{NUM_QUBITS}b') 
    p = collapse_probs.get(state_str, 0.0) 
    
    coeff = state.data[i] if i < len(state.data) else 0j
    real_part, imag_part = round(coeff.real, 3), round(coeff.imag, 3)
    shimmer_class = "shimmer-box" if p < 0.01 else ""
    
    if state_str == max_state and p > 0:
        box_color, opacity = "#00FFCC", "1.0"
    elif p > 0.4: box_color, opacity = "#FFD700", "1.0"
    elif p > 0.005: box_color, opacity = "#ff4b4b", "1.0"
    else: box_color, opacity = "#555555", "0.4"
    
    telemetry_html += f'<div class="hud-box {shimmer_class}" style="min-width: 180px; flex: 0 0 auto; border-top: 3px solid {box_color}; padding: 15px; opacity: {opacity}; transition: opacity 0.3s ease;"><span style="color: {box_color}; font-family: \'Orbitron\'; font-size: 0.9rem;">|{state_str}⟩</span><br><span style="font-family: \'JetBrains Mono\'; font-size: 1.5rem; font-weight: bold; color: #FFFFFF;">{p*100:.1f}%</span><br><hr style="border: 0; border-top: 1px solid rgba(255, 215, 0, 0.05); margin: 8px 0;"><code style="font-size: 0.8rem; color: {box_color}; background: none;">ψ: {real_part} + {imag_part}j</code></div>'

telemetry_html += "</div>"
st.markdown(telemetry_html, unsafe_allow_html=True)

st.divider()
st.subheader("3D HOLOGRAPHIC CONSOLE")

def build_plotly_bloch(state_vec, qubit_idx, num_qubits):
    trace_qubits = [i for i in range(num_qubits) if i != qubit_idx]
    reduced_rho = partial_trace(state_vec, trace_qubits)
    x_v, y_v, z_v = [reduced_rho.expectation_value(Pauli(p)).real for p in ['X', 'Y', 'Z']]

    fig = go.Figure()
    
    phi = np.linspace(0, 2*np.pi, 40)
    theta = np.linspace(0, np.pi, 40)
    phi, theta = np.meshgrid(phi, theta)
    x_s = (np.sin(theta) * np.cos(phi)).flatten()
    y_s = (np.sin(theta) * np.sin(phi)).flatten()
    z_s = np.cos(theta).flatten()

    fig.add_trace(go.Mesh3d(
        x=x_s, y=y_s, z=z_s,
        alphahull=0, 
        color='#00FFFF',
        opacity=0.15,
        hoverinfo='skip'
    ))

    u_line = np.linspace(0, 2 * np.pi, 100)
    cx, cy, cz = np.cos(u_line), np.sin(u_line), np.zeros(100)
    
    fig.add_trace(go.Scatter3d(x=cx, y=cy, z=cz, mode='lines', line=dict(color='#00FFFF', width=3), hoverinfo='skip'))
    fig.add_trace(go.Scatter3d(x=cx, y=cz, z=cy, mode='lines', line=dict(color='#00FFFF', width=3), hoverinfo='skip'))
    fig.add_trace(go.Scatter3d(x=cz, y=cx, z=cy, mode='lines', line=dict(color='#00FFFF', width=3), hoverinfo='skip'))

    for pt, lbl in [([1.3,0,0], 'X'), ([0,1.3,0], 'Y'), ([0,0,1.3], 'Z')]:
        fig.add_trace(go.Scatter3d(x=[-pt[0], pt[0]], y=[-pt[1], pt[1]], z=[-pt[2], pt[2]], mode='lines', line=dict(color='#FFFFFF', width=2, dash='dash'), hoverinfo='skip'))
        fig.add_trace(go.Scatter3d(x=[pt[0]*1.1], y=[pt[1]*1.1], z=[pt[2]*1.1], mode='text', text=[lbl], textfont=dict(color='#FFD700', family='Orbitron', size=14), hoverinfo='skip'))

    if np.sqrt(x_v**2 + y_v**2 + z_v**2) < 0.01: x_v, y_v, z_v = 0, 0, 0.001 

    fig.add_trace(go.Scatter3d(x=[0, x_v], y=[0, y_v], z=[0, z_v], mode='lines', line=dict(color='#FFD700', width=8), name='Vector'))
    fig.add_trace(go.Scatter3d(x=[x_v], y=[y_v], z=[z_v], mode='markers', marker=dict(size=10, color='#FF0000', symbol='diamond'), name='Tip'))

    fig.update_layout(
        title=dict(text=f"QUBIT {qubit_idx}", font=dict(color='#FF0000', family='Orbitron', size=18)),
        scene=dict(
            xaxis=dict(showbackground=False, visible=False, range=[-1.5, 1.5]), 
            yaxis=dict(showbackground=False, visible=False, range=[-1.5, 1.5]),
            zaxis=dict(showbackground=False, visible=False, range=[-1.5, 1.5]), 
            aspectmode="cube", 
            camera=dict(eye=dict(x=1.3, y=1.3, z=1.0))
        ),
        margin=dict(l=0, r=0, b=0, t=30), 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        showlegend=False, 
        height=450
    )
    return fig

if adv_mode:
    st.markdown("<br><h4 style='color:#FFD700; text-align:center; font-family:\"Orbitron\", sans-serif; letter-spacing: 2px;'>ADVANCED QUBIT ANALYSIS</h4>", unsafe_allow_html=True)
    
    for i in range(NUM_QUBITS):
        st.markdown(f"<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        fig = build_plotly_bloch(state, i, NUM_QUBITS)
        st.plotly_chart(fig, use_container_width=True)
else:
    html_source = build_all_threejs_blochs(state, NUM_QUBITS)
    components.html(html_source, height=450)

st.divider()
st.subheader("QUANTUM CIRCUIT BLUEPRINT")
st.markdown("<div class='circuit-code'>", unsafe_allow_html=True)
st.code(st.session_state.qc.draw('text'), language="text")
st.markdown("</div>", unsafe_allow_html=True)