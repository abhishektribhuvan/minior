import serial
import json
import csv
import threading
import time
import os
import io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI()

# --- CONFIGURATION ---
SERIAL_PORT = "COM3"  # <--- CHANGE TO YOUR ESP32 PORT
BAUD_RATE = 115200
CSV_FILE = "calibration_1000.csv"

# Global state variables
latest_reading = {"x": 0.0, "y": 0.0, "z": 0.0}
is_calibrating = False
calibration_count = 0

# --- BACKGROUND USB LISTENER ---
def serial_worker():
    global latest_reading, is_calibrating, calibration_count
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"[*] Connected to {SERIAL_PORT}")
    except Exception:
        print(f"[!] Could not open {SERIAL_PORT}. Close Arduino IDE!")
        return

    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line.startswith('{') and line.endswith('}'):
                    data = json.loads(line)
                    # Store absolute values so negatives don't cancel out
                    latest_reading = {
                        "x": abs(data['x']),
                        "y": abs(data['y']),
                        "z": abs(data['z'])
                    }
                    
                    # ACTION 1 LOGIC: If triggered, save absolute values to CSV until we hit 1000
                    if is_calibrating and calibration_count < 1000:
                        with open(CSV_FILE, mode='a', newline='') as file:
                            csv.writer(file).writerow([abs(data['x']), abs(data['y']), abs(data['z'])])
                        calibration_count += 1
                        if calibration_count >= 1000:
                            is_calibrating = False # Stop recording when done
                            print("[*] Calibration Complete: 1000 readings saved.")
        except Exception:
            time.sleep(0.01)

@app.on_event("startup")
def startup():
    threading.Thread(target=serial_worker, daemon=True).start()

# --- ACTION 1: TRIGGER CALIBRATION ---
@app.post("/api/action1_calibrate")
def trigger_calibration():
    global is_calibrating, calibration_count
    
    # Wipe the old CSV and start fresh
    with open(CSV_FILE, mode='w', newline='') as file:
        csv.writer(file).writerow(["x", "y", "z"])
        
    calibration_count = 0
    is_calibrating = True
    
    # Wait until the background thread finishes reading 1000 values
    while is_calibrating:
        time.sleep(0.5)
        
    return {"message": "Successfully recorded 1000 readings"}

# --- ACTION 2: GET LIVE DATA & AVERAGES ---
@app.get("/api/action2_live")
def get_live_data():
    averages = {"avg_x": 0, "avg_y": 0, "avg_z": 0}
    
    # Calculate the flat line averages from the CSV
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if not df.empty:
            averages = {
                "avg_x": df['x'].abs().mean(),
                "avg_y": df['y'].abs().mean(),
                "avg_z": df['z'].abs().mean()
            }
            
    return {"live": latest_reading, "averages": averages}

# --- ACTION 3: GET DISTRIBUTION GRAPH (Magnitude) ---
@app.get("/api/action3_distribution")
def get_distribution():
    if not os.path.exists(CSV_FILE):
        return Response(content="No data", status_code=404)

    df = pd.read_csv(CSV_FILE)
    
    # Compute magnitude: sqrt(x^2 + y^2 + z^2)
    df['magnitude'] = np.sqrt(df['x']**2 + df['y']**2 + df['z']**2)
    
    sns.set_theme(style="darkgrid")
    fig, ax = plt.subplots(figsize=(10, 5))
    
    sns.histplot(df['magnitude'], kde=True, ax=ax, color='#6C63FF', edgecolor='white', linewidth=0.5)
    ax.set_title("Normal Distribution: Vibration Magnitude  √(x² + y² + z²)", fontsize=14, fontweight='bold')
    ax.set_xlabel("Magnitude", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.axvline(df['magnitude'].mean(), color='red', linestyle='--', linewidth=2, label=f"Mean: {df['magnitude'].mean():.2f}")
    ax.legend(fontsize=11)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120)
    plt.close()
    buf.seek(0)
    
    return Response(content=buf.getvalue(), media_type="image/png")