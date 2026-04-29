# 🚀 Predictive Motor Anomaly Detection System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-FF4B4B?logo=streamlit&logoColor=white)
![C++](https://img.shields.io/badge/C++-Firmware-00599C?logo=c%2B%2B&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

A full-stack, real-time hardware telemetry and machine learning diagnostic dashboard designed for **Predictive Maintenance**. 

This system reads high-frequency vibration data from physical hardware (ESP32/Microcontroller), streams it to an asynchronous Python backend, and visualizes system health in real-time. It uses **Statistical Z-Score Analysis** to detect mechanical anomalies before catastrophic failure occurs.

---

## 🏗️ System Architecture

1. **Hardware Edge Node (C++ / PlatformIO):** An ESP32 interfaces with an accelerometer (e.g., MPU6050) to capture 3-axis (X, Y, Z) vibration telemetry.
2. **Asynchronous Backend (FastAPI):** A background daemon thread reads serial USB data in real-time, calculates rolling averages, and handles statistical anomaly math.
3. **Interactive Frontend (Streamlit & Plotly.js):** A responsive dashboard utilizing client-side JavaScript injection for completely flicker-free, 60FPS live charting and system status monitoring.

---

## ✨ Key Features

* **Real-time Hardware Telemetry:** Directly interfaces with microcontrollers via Serial COM ports.
* **Automated Calibration Phase:** Records a 1000-sample baseline to compute the Gaussian Mean ($\mu$) and Standard Deviation ($\sigma$) for specific motor operating states.
* **Live Z-Score Anomaly Detection:** Calculates dynamic Z-Scores on the fly. If the vibration on any axis exceeds the $3\sigma$ threshold ($|Z| > 3$), the system triggers an immediate visual anomaly alert.
* **High-Performance UI:** Bypasses standard Streamlit server-side rendering bottlenecks by injecting pure HTML/JS Plotly graphs, resulting in a zero-latency, Task Manager-style scrolling UI.
* **Distribution Analytics:** Automatically generates and serves KDE (Kernel Density Estimation) distribution graphs to verify sensor normality.

---

## 🧠 Methodology: How It Works

The system utilizes the **Z-Score statistical method** for lightweight, real-time anomaly detection, making it highly suitable for edge computing where deep learning models might be too slow.

1. **Baseline Setup:** The system reads $N=1000$ normal operating values to find $\mu$ (mean) and $\sigma$ (standard deviation).
2. **Formula:** For every new live reading $x$, the Z-Score is calculated as:  
   $$Z = \frac{|x| - \mu}{\sigma}$$
3. **Decision Rule:** Following the Empirical Rule (68-95-99.7), 99.7% of normal data falls within 3 standard deviations. Therefore, if **$|Z| > 3$**, the system flags an Anomaly.

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.9+
* PlatformIO (for firmware flashing)
* Microcontroller connected via USB

### 1. Hardware Setup (Firmware)
1. Open the `/firmware` directory in VS Code with the PlatformIO extension.
2. Connect your ESP32/Microcontroller.
3. Build and Upload the code to the board.

### 2. Software Setup (Backend & Frontend)
1. Navigate to the `/software` directory:
   ```bash
   cd software
   ```
2. Install the required dependencies (ensure you are using a virtual environment):
   ```bash
   pip install fastapi uvicorn streamlit pandas numpy matplotlib seaborn pyserial
   ```
3. **Configure your Port:** Open `main.py` and update the `SERIAL_PORT` variable to match your microcontroller's port (e.g., `COM3` on Windows, `/dev/ttyUSB0` on Linux).

### 3. Running the Application
You will need two terminal windows to run the backend and frontend simultaneously.

**Terminal 1 (Backend):**
```bash
uvicorn main:app --reload
```
*(The API will start at http://127.0.0.1:8000. You can view the auto-generated Swagger UI at `/docs`)*

**Terminal 2 (Frontend):**
```bash
streamlit run web.py
```

---

## 🗺️ Future Roadmap
While currently functional and accurate for Gaussian data, planned architecture upgrades include:
- [ ] **Database Migration:** Replace CSV-based state management with a robust Time-Series Database (e.g., InfluxDB / SQLite).
- [ ] **Advanced ML Models:** Implement **Isolation Forests** or **Autoencoders** to detect anomalies in non-linear, multi-dimensional vibration patterns.
- [ ] **Dockerization:** Wrap the FastAPI and Streamlit apps into a `docker-compose` environment for one-click deployment.
- [ ] **Environment Variables:** Migrate hardcoded serial configurations to `.env` files for cross-platform compatibility.

---
*Designed and built for predictive maintenance analysis.*
