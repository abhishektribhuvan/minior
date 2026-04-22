import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Motor Diagnostic UI", layout="wide")
st.title("⚙️ B2B Motor Diagnostic Dashboard")

API_URL = "http://127.0.0.1:8000"

col1, col2, col3 = st.columns(3)

# ==========================================
# ACTION 1: CALIBRATE (1000 Readings)
# ==========================================
with col1:
    st.subheader("Step 1: Calibration")
    if st.button("▶ Action 1: Read 1000 Values"):
        with st.spinner("Recording 1000 high-speed readings (Takes ~20 sec)..."):
            res = requests.post(f"{API_URL}/api/action1_calibrate")
            if res.status_code == 200:
                st.success("Calibration Saved to CSV!")

# ==========================================
# ACTION 3: VIEW DISTRIBUTION
# ==========================================
with col3:
    st.subheader("Step 2: Distribution")
    if st.button("▶ Action 3: Show Distribution"):
        res = requests.get(f"{API_URL}/api/action3_distribution")
        if res.status_code == 200:
            st.image(res.content, caption="1000-Reading Bell Curves")

st.divider()

# ==========================================
# ACTION 2: LIVE TASK MANAGER GRAPHS
# ==========================================
st.subheader("Step 3: Live Task Manager View")
start_live = st.button("▶ Action 2: Start Live Stream")

# Create 3 placeholders for our graphs
graph_col1, graph_col2, graph_col3 = st.columns(3)
placeholder_x = graph_col1.empty()
placeholder_y = graph_col2.empty()
placeholder_z = graph_col3.empty()

if start_live:
    # Initialize empty dataframes with columns for the Live line AND the Average line
    df_x = pd.DataFrame(columns=["Live_X", "Avg_X"])
    df_y = pd.DataFrame(columns=["Live_Y", "Avg_Y"])
    df_z = pd.DataFrame(columns=["Live_Z", "Avg_Z"])
    
    # The infinite loop that refreshes the graphs
    while True:
        try:
            res = requests.get(f"{API_URL}/api/action2_live").json()
            
            live = res["live"]
            avg = res["averages"]
            
            # Create a new row of data (Live Value + The Constant Average from the CSV)
            new_x = pd.DataFrame([{"Live_X": live["x"], "Avg_X": avg["avg_x"]}])
            new_y = pd.DataFrame([{"Live_Y": live["y"], "Avg_Y": avg["avg_y"]}])
            new_z = pd.DataFrame([{"Live_Z": live["z"], "Avg_Z": avg["avg_z"]}])
            
            # Append new data, keep only the last 100 points for the "Task Manager" scrolling effect
            df_x = pd.concat([df_x, new_x]).tail(100)
            df_y = pd.concat([df_y, new_y]).tail(100)
            df_z = pd.concat([df_z, new_z]).tail(100)
            
            # Draw the line charts (Streamlit will automatically draw two lines: Live and Avg)
            placeholder_x.line_chart(df_x, color=["#FF0000", "#FFFFFF"]) # Red Live, White Avg
            placeholder_y.line_chart(df_y, color=["#00FF00", "#FFFFFF"]) # Green Live, White Avg
            placeholder_z.line_chart(df_z, color=["#0000FF", "#FFFFFF"]) # Blue Live, White Avg
            
            time.sleep(0.1) # Update the graph 10 times a second
            
        except Exception as e:
            st.error("Lost connection to backend.")
            break