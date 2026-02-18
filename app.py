import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AquaGuard Advanced", layout="wide")
st.title("💧 AquaGuard – Smart Water Risk & Outbreak Monitoring")

# -----------------------------
# LOAD DEFAULT DATA
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("aquaguard_balanced_india_dataset.csv")

# session data holder
if "data" not in st.session_state:
    try:
        st.session_state.data = load_data()
    except:
        st.session_state.data = pd.DataFrame()

data = st.session_state.data

# -----------------------------
# CSV UPLOAD (Dashboard Upload)
# -----------------------------
st.sidebar.header("📂 Upload New Dataset")

uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded is not None:
    try:
        st.session_state.data = pd.read_csv(uploaded)
        data = st.session_state.data
        st.sidebar.success("✅ Dataset uploaded")
    except Exception as e:
        st.sidebar.error(f"Upload error: {e}")

# -----------------------------
# SAFETY CHECK
# -----------------------------
required_cols = {"Village","Latitude","Longitude","Risk","Date"}

if not data.empty and not required_cols.issubset(set(data.columns)):
    st.error("❌ Dataset missing required columns")
    st.stop()

# -----------------------------
# OUTBREAK PROBABILITY MODEL
# -----------------------------
def outbreak_probability(risk_series):
    score_map = {
        "Low Risk 🟢": 0.2,
        "Medium Risk 🟡": 0.5,
        "High Risk 🔴": 0.9
    }
    scores = risk_series.map(score_map).fillna(0.3)
    return round(scores.mean() * 100, 2)

if not data.empty:
    prob = outbreak_probability(data["Risk"])
else:
    prob = 0

# -----------------------------
# ALERT HISTORY
# -----------------------------
if "alerts" not in st.session_state:
    st.session_state.alerts = []

def generate_alert(prob):
    if prob > 70:
        level = "HIGH ALERT 🔴"
    elif prob > 40:
        level = "MEDIUM ALERT 🟡"
    else:
        level = "LOW ALERT 🟢"

    st.session_state.alerts.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Alert": level,
        "Probability (%)": prob
    })
    return level

alert_level = generate_alert(prob)

# -----------------------------
# METRICS
# -----------------------------
st.header("📊 Dashboard Overview")

c1, c2, c3 = st.columns(3)
c1.metric("Total Records", len(data))
c2.metric("Outbreak Probability", f"{prob}%")
c3.metric("Alert Level", alert_level)

# =============================
# 🗺️ MAP
# =============================
st.header("🗺️ Risk Map")

if not data.empty:
    map_df = data.rename(columns={"Latitude": "lat", "Longitude": "lon"})
    st.map(map_df[["lat", "lon"]])

# =============================
# 🎯 COLORED MAP
# =============================
st.header("🎯 Risk Visualization")

if not data.empty:
    fig_map = px.scatter_mapbox(
        data,
        lat="Latitude",
        lon="Longitude",
        color="Risk",
        hover_name="Village",
        zoom=3,
        height=500,
        color_discrete_map={
            "Low Risk 🟢": "green",
            "Medium Risk 🟡": "yellow",
            "High Risk 🔴": "red"
        }
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)

# =============================
# 📊 OUTBREAK PATTERN SIMULATION
# =============================
st.header("📈 Outbreak Pattern Simulation")

if not data.empty:
    sim_days = st.slider("Simulation Days", 7, 60, 30)

    base = prob / 100
    growth = [min(100, (base * (1.05 ** i)) * 100) for i in range(sim_days)]

    sim_df = pd.DataFrame({
        "Day": range(1, sim_days + 1),
        "Predicted Outbreak %": growth
    })

    fig_sim = px.line(sim_df, x="Day", y="Predicted Outbreak %")
    st.plotly_chart(fig_sim, use_container_width=True)

# =============================
# 📜 ALERT HISTORY
# =============================
st.header("🚨 Alert History")

alert_df = pd.DataFrame(st.session_state.alerts)
if not alert_df.empty:
    st.dataframe(alert_df, use_container_width=True)

# =============================
# 🛡️ PREVENTION RECOMMENDATIONS
# =============================
st.header("🛡️ Prevention Recommendations")

if prob > 70:
    st.error("Immediate action required!")
    st.write("""
    • Boil water before use  
    • Chlorinate water source  
    • Issue public health warning  
    • Inspect contamination source  
    """)

elif prob > 40:
    st.warning("Moderate risk detected")
    st.write("""
    • Increase water quality monitoring  
    • Advise vulnerable groups  
    • Prepare medical response team  
    """)

else:
    st.success("Water condition relatively safe")
    st.write("""
    • Continue routine monitoring  
    • Maintain sanitation practices  
    """)

# =============================
# 📋 DATA TABLE
# =============================
st.header("📋 Data Table")
st.dataframe(data, use_container_width=True)
