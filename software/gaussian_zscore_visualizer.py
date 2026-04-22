import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

# ==========================================
# 1. GENERATE MOTOR VIBRATION DATASET
# ==========================================
# Simulating 1,000 readings of a healthy motor (e.g., 10 minutes of data)
np.random.seed(42) 
mu_actual = 3.0    # Mean vibration (Baseline)
sigma_actual = 1.0 # Standard deviation (Normal fluctuation)
num_readings = 1000 

# Generate 1,000 normally distributed vibration readings
vibration_data = np.random.normal(loc=mu_actual, scale=sigma_actual, size=num_readings)

# ==========================================
# 2. CALCULATE DEVIATIONS (Xi - mu)
# ==========================================
# Find the exact center of this specific 1,000-reading sample
mu_calculated = np.mean(vibration_data)
deviations = vibration_data - mu_calculated

# ==========================================
# 3. DEFINE ADAPTED HIGH-RESOLUTION BINS
# ==========================================
# Because we only have 1,000 readings, we widen the bins from 0.1 to 0.2.
# This prevents "empty bins" and jagged noise, creating ~40 micro-bars.
bin_width = 0.2
bin_edges = np.arange(-4.0, 4.0 + bin_width, bin_width)

# ==========================================
# 4. PLOT USING SEABORN AND MATPLOTLIB
# ==========================================
sns.set_theme(style="darkgrid") 
plt.figure(figsize=(14, 8))

# Plot the Histogram
# Notice the bars will look slightly more uneven than the 50,000 reading version.
# This is authentic real-world data variance.
ax = sns.histplot(
    deviations, 
    bins=bin_edges, 
    color="cornflowerblue", 
    edgecolor="white", 
    linewidth=0.5,
    stat="count",
    alpha=0.8,
    label=f"Count of Readings per {bin_width}g Deviation"
)

# ==========================================
# 5. OVERLAY THE THEORETICAL GAUSSIAN CURVE
# ==========================================
# Generate 1,000 points for an ultra-smooth theoretical line
x_axis = np.linspace(-4.5, 4.5, 1000)

# The math to perfectly scale the probability density curve to match the new bin width
y_axis = norm.pdf(x_axis, 0, np.std(deviations)) * num_readings * bin_width

plt.plot(x_axis, y_axis, color="crimson", linewidth=3, label="Theoretical Gaussian")

# ==========================================
# 6. FORMAT THE GRAPH LABELS & Z-SCORE ZONES
# ==========================================
plt.title("Motor Vibration Deviations (1,000 Readings) - Notice the Variance", fontsize=18, fontweight='bold', pad=15)
plt.xlabel("Deviation from Mean ($X_i - \mu$)", fontsize=14, fontweight='bold')
plt.ylabel("Number of Occurrences", fontsize=14, fontweight='bold')

# Mark the specific Z-Score Thresholds (The Anomaly Boundaries)
plt.axvline(0, color='black', linestyle='-', linewidth=1.5, label="Mean (0 Deviation)")

# 3 Standard Deviation limits (The 99.7% Rule Boundary)
plt.axvline(3.0, color='orange', linestyle='--', linewidth=2, label="+3σ (Anomaly Limit)")
plt.axvline(-3.0, color='orange', linestyle='--', linewidth=2, label="-3σ (Anomaly Limit)")

plt.legend(fontsize=12, loc="upper right")
plt.tight_layout()

# Show the plot
plt.show()