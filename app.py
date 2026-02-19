import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="AquaGuard Advanced", layout="wide")
st.title("💧 AquaGuard – Smart Water Risk & Outbreak Monitoring")

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_data():
    return pd.read_csv("aquaguard_balanced_india_dataset.csv")

if "data" not in st.session_state:
    try:
        st.session_state.data = load_data()
    except:
        st.session_state.data = pd.DataFrame()

data = st.session_state.data

# =============================
# DASHBOARD METRICS
# =============================
st.header("📊 Risk Status Dashboard")

if not data.empty:
    high = (data["Risk"] == "High Risk 🔴").sum()
    med = (data["Risk"] == "Medium Risk 🟡").sum()
    low = (data["Risk"] == "Low Risk 🟢").sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("🔴 High Risk Areas", high)
    c2.metric("🟡 Medium Risk Areas", med)
    c3.metric("🟢 Safe Areas", low)

# =============================
# OUTBREAK PROBABILITY MODEL
# =============================
def outbreak_probability(df):
    score_map = {
        "Low Risk 🟢": 0.2,
        "Medium Risk 🟡": 0.5,
        "High Risk 🔴": 0.9
    }
    scores = df["Risk"].map(score_map).fillna(0.3)
    return round(scores.mean() * 100, 2)

prob = outbreak_probability(data) if not data.empty else 0

st.header("📈 Outbreak Probability")

st.metric("Predicted Outbreak Probability", f"{prob}%")

# =============================
# OUTBREAK TREND GRAPH
# =============================
st.subheader("📉 Outbreak Growth Simulation")

days = st.slider("Simulation Days", 7, 60, 30)

base = prob / 100
growth = [min(100, (base * (1.06 ** i)) * 100) for i in range(days)]

sim_df = pd.DataFrame({
    "Day": range(1, days + 1),
    "Outbreak Risk %": growth
})

fig_sim = px.line(sim_df, x="Day", y="Outbreak Risk %")
st.plotly_chart(fig_sim, use_container_width=True)

# =============================
# RISK MAP
# =============================
st.header("🗺️ Risk Visualization Map")

if not data.empty:
    map_df = data.rename(columns={"Latitude": "lat", "Longitude": "lon"})
    st.map(map_df[["lat", "lon"]])

# =============================
# ADVANCED COLORED MAP
# =============================
st.subheader("🎯 Risk Level Distribution")

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
# ALERT HISTORY
# =============================
st.header("🚨 Alert History")

if "alerts" not in st.session_state:
    st.session_state.alerts = []

def log_alert(probability):
    if probability > 70:
        level = "HIGH ALERT 🔴"
    elif probability > 40:
        level = "MEDIUM ALERT 🟡"
    else:
        level = "SAFE 🟢"

    st.session_state.alerts.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Status": level,
        "Probability": probability
    })

log_alert(prob)

alert_df = pd.DataFrame(st.session_state.alerts)
st.dataframe(alert_df, use_container_width=True)

# =============================
# PREVENTION RECOMMENDATION
# =============================
st.header("🛡️ Prevention Recommendations")

if prob > 70:
    st.error("High outbreak risk detected")
    st.markdown("""
**Immediate Actions**
- Boil water before consumption  
- Chlorinate contaminated sources  
- Issue public advisory  
- Conduct field inspection  
- Deploy medical teams  
""")

elif prob > 40:
    st.warning("Moderate risk detected")
    st.markdown("""
**Preventive Actions**
- Increase monitoring frequency  
- Alert vulnerable populations  
- Prepare treatment facilities  
""")

else:
    st.success("Water quality currently safe")
    st.markdown("""
**Routine Actions**
- Continue periodic testing  
- Maintain sanitation  
- Community awareness  
""")

# =============================
# WATER QUALITY TABLE (EXPANDED)
# =============================
st.header("📋 Detailed Water Quality Table")

# simulate extra parameters for evaluation demo
if not data.empty:
    demo = data.copy()
    np.random.seed(42)

    demo["pH"] = np.round(np.random.uniform(6.5, 8.5, len(demo)), 2)
    demo["Temperature"] = np.round(np.random.uniform(24, 32, len(demo)), 1)
    demo["Salinity"] = np.round(np.random.uniform(0.1, 0.9, len(demo)), 2)
    demo["Alkalinity"] = np.round(np.random.uniform(80, 140, len(demo)), 1)
    demo["Dissolved_O2"] = np.round(np.random.uniform(5, 9, len(demo)), 2)
    demo["Bacterial_Load"] = np.random.choice(
        ["Low", "Moderate", "High"], len(demo)
    )

    st.dataframe(demo, use_container_width=True)
