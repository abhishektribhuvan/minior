import streamlit as st
import requests

st.set_page_config(page_title="Motor Diagnostic UI", layout="wide")
st.title("⚙️ B2B Motor Diagnostic Dashboard")

API_URL = "http://127.0.0.1:8000"

MAX_POINTS = 100  # scrolling window size (like Task Manager)

col1, col2, col3 = st.columns(3)

# ==========================================
# ACTION 1: CALIBRATE (1000 Readings)
# Deletes ALL previous data, then reads fresh
# ==========================================
with col1:
    st.subheader("Step 1: Calibration")
    if st.button("▶ Action 1: Read 1000 Values"):

        with st.spinner("🗑️ Clearing old data & recording 1000 fresh readings (~20 sec)..."):
            try:
                res = requests.post(f"{API_URL}/api/action1_calibrate", timeout=60)
                if res.status_code == 200:
                    st.success("✅ Calibration Complete! 1000 new readings saved.")
                else:
                    st.error(f"Backend error: {res.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Backend not running! Start `uvicorn main:app` first.")

# ==========================================
# ACTION 3: VIEW DISTRIBUTION
# ==========================================
with col3:
    st.subheader("Step 2: Distribution")
    if st.button("▶ Action 3: Show Distribution"):
        try:
            res = requests.get(f"{API_URL}/api/action3_distribution", timeout=10)
            if res.status_code == 200:
                st.image(res.content, caption="Vibration Magnitude Distribution √(x² + y² + z²)")
            else:
                st.error(f"Backend error: {res.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Backend not running!")

st.divider()


# ==========================================
# LIVE CHART — Pure JS, polls API directly from browser
# Plotly.react() updates chart in-place = zero flicker
# ==========================================
import streamlit.components.v1 as components

LIVE_CHART_HTML = f"""
<!DOCTYPE html>
<html>
<head>
<script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: transparent; font-family: 'Segoe UI', sans-serif; }}
  #chart {{ width: 100%; height: 420px; }}
  #status {{ color: #a0a0a0; font-size: 13px; padding: 8px 12px; }}
  #controls {{ display: flex; gap: 12px; margin-bottom: 8px; }}
  #controls button {{
    padding: 8px 24px; border: none; border-radius: 6px; cursor: pointer;
    font-size: 14px; font-weight: 600; transition: all 0.2s;
  }}
  #btnStart {{
    background: linear-gradient(135deg, #00c853, #00e676); color: #fff;
  }}
  #btnStart:hover {{ transform: scale(1.04); box-shadow: 0 4px 16px rgba(0,200,80,0.3); }}
  #btnStop {{
    background: linear-gradient(135deg, #ff1744, #ff5252); color: #fff;
  }}
  #btnStop:hover {{ transform: scale(1.04); box-shadow: 0 4px 16px rgba(255,50,50,0.3); }}
  #btnStart:disabled, #btnStop:disabled {{
    opacity: 0.4; cursor: not-allowed; transform: none; box-shadow: none;
  }}
</style>
</head>
<body>

<div id="controls">
  <button id="btnStart" onclick="startStream()">▶ Start Live Stream</button>
  <button id="btnStop" onclick="stopStream()" disabled>⏹ Stop Live Stream</button>
</div>
<div id="chart"></div>
<div id="status">⏸ Click "Start Live Stream" to begin.</div>

<script>
const API = "{API_URL}";
const MAX = {MAX_POINTS};
let dataX = [], dataY = [], dataZ = [];
let avgX = 0, avgY = 0, avgZ = 0;
let timer = null;
let chartReady = false;

// ── Initialize empty chart ──
const layout = {{
  title: {{ text: 'Live Vibration — X · Y · Z  (Scroll to Zoom)', font: {{ color: '#fff', size: 16 }} }},
  paper_bgcolor: '#1a1a2e',
  plot_bgcolor: '#16213e',
  font: {{ color: '#a0a0a0' }},
  height: 420,
  margin: {{ l: 50, r: 30, t: 60, b: 50 }},
  legend: {{
    orientation: 'h', yanchor: 'bottom', y: 1.02, xanchor: 'center', x: 0.5,
    font: {{ color: '#fff', size: 13 }}, bgcolor: 'rgba(0,0,0,0.3)'
  }},
  xaxis: {{
    title: 'Reading #', showgrid: true, gridcolor: '#2a2a4a', gridwidth: 1,
    range: [0, MAX],
    rangeslider: {{ visible: true, bgcolor: '#0f0f23', thickness: 0.08 }}
  }},
  yaxis: {{
    title: 'Sensor Value', showgrid: true, gridcolor: '#2a2a4a', gridwidth: 1
  }},
  dragmode: 'zoom',
  shapes: [],
  annotations: []
}};

const traces = [
  {{ y: [], mode: 'lines', name: 'X-Axis', line: {{ color: 'rgba(255,60,60,1)', width: 2 }},
     fill: 'tozeroy', fillcolor: 'rgba(255,60,60,0.08)' }},
  {{ y: [], mode: 'lines', name: 'Y-Axis', line: {{ color: 'rgba(60,255,60,1)', width: 2 }},
     fill: 'tozeroy', fillcolor: 'rgba(60,255,60,0.08)' }},
  {{ y: [], mode: 'lines', name: 'Z-Axis', line: {{ color: 'rgba(60,120,255,1)', width: 2 }},
     fill: 'tozeroy', fillcolor: 'rgba(60,120,255,0.08)' }}
];

const config = {{ scrollZoom: true, displayModeBar: true, responsive: true }};

Plotly.newPlot('chart', traces, layout, config).then(() => {{ chartReady = true; }});

// ── Smooth update function ──
async function fetchAndUpdate() {{
  try {{
    const res = await fetch(API + '/api/action2_live');
    const data = await res.json();

    const live = data.live;
    const avg = data.averages;
    avgX = avg.avg_x; avgY = avg.avg_y; avgZ = avg.avg_z;

    dataX.push(live.x); dataY.push(live.y); dataZ.push(live.z);
    if (dataX.length > MAX) {{ dataX.shift(); dataY.shift(); dataZ.shift(); }}

    // Build avg lines as shapes + annotations
    const shapes = [];
    const annotations = [];
    const avgLines = [
      {{ val: avgX, color: 'rgba(255,60,60,0.6)', label: 'Avg X', fontColor: 'rgba(255,60,60,1)', pos: 'left' }},
      {{ val: avgY, color: 'rgba(60,255,60,0.6)', label: 'Avg Y', fontColor: 'rgba(60,255,60,1)', pos: 'right' }},
      {{ val: avgZ, color: 'rgba(60,120,255,0.6)', label: 'Avg Z', fontColor: 'rgba(60,120,255,1)', pos: 'center' }}
    ];
    avgLines.forEach(a => {{
      if (a.val !== 0) {{
        shapes.push({{
          type: 'line', x0: 0, x1: 1, xref: 'paper', y0: a.val, y1: a.val,
          line: {{ color: a.color, width: 1.5, dash: 'dash' }}
        }});
        annotations.push({{
          x: a.pos === 'left' ? 0.02 : a.pos === 'right' ? 0.98 : 0.5,
          xref: 'paper', xanchor: a.pos === 'right' ? 'end' : 'start',
          y: a.val, yanchor: 'bottom',
          text: a.label + ': ' + a.val.toFixed(2),
          showarrow: false, font: {{ color: a.fontColor, size: 11 }}
        }});
      }}
    }});

    // Plotly.react = in-place update, NO DOM replacement
    Plotly.react('chart', [
      {{ ...traces[0], y: [...dataX] }},
      {{ ...traces[1], y: [...dataY] }},
      {{ ...traces[2], y: [...dataZ] }}
    ], {{ ...layout, shapes, annotations }}, config);

    document.getElementById('status').innerHTML =
      '📡 Live — X: ' + live.x.toFixed(2) + '  |  Y: ' + live.y.toFixed(2) +
      '  |  Z: ' + live.z.toFixed(2) +
      '  (Avg X: ' + avgX.toFixed(2) + ', Y: ' + avgY.toFixed(2) + ', Z: ' + avgZ.toFixed(2) + ')';

  }} catch(e) {{
    document.getElementById('status').innerHTML = '❌ Backend not running! Start uvicorn main:app first.';
    stopStream();
  }}
}}

function startStream() {{
  if (timer) return;
  dataX = []; dataY = []; dataZ = [];
  document.getElementById('btnStart').disabled = true;
  document.getElementById('btnStop').disabled = false;
  document.getElementById('status').innerHTML = '📡 Connecting...';
  fetchAndUpdate();
  timer = setInterval(fetchAndUpdate, 1000);
}}

function stopStream() {{
  if (timer) {{ clearInterval(timer); timer = null; }}
  document.getElementById('btnStart').disabled = false;
  document.getElementById('btnStop').disabled = true;
  document.getElementById('status').innerHTML = '⏸ Live stream stopped. Click "Start Live Stream" to begin.';
}}
</script>
</body>
</html>
"""

components.html(LIVE_CHART_HTML, height=540, scrolling=False)