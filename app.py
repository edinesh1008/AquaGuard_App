import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AquaGuard", layout="wide")
st.title("💧 AquaGuard – Water Risk Monitoring")

# -----------------------------
# LOAD YOUR FILE
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("india_water_data.csv")
    return df

try:
    data = load_data()
except Exception as e:
    st.error(f"❌ File not found or error: {e}")
    st.stop()

# -----------------------------
# STANDARDIZE RISK (COLOR)
# -----------------------------
def normalize_risk(x):
    x = str(x).upper()
    if "HIGH" in x:
        return "High Risk 🔴"
    elif "WARN" in x:
        return "Medium Risk 🟡"
    else:
        return "Low Risk 🟢"

data["Risk"] = data["Risk_Level"].apply(normalize_risk)

# -----------------------------
# METRICS
# -----------------------------
st.header("📊 Overview")

c1, c2, c3 = st.columns(3)
c1.metric("Total Records", len(data))
c2.metric("High Risk", (data["Risk"].str.contains("High")).sum())
c3.metric("Safe", (data["Risk"].str.contains("Low")).sum())

# =============================
# 🗺️ MAP
# =============================
st.header("🗺️ Risk Map")

map_df = data.rename(columns={
    "Latitude": "lat",
    "Longitude": "lon"
})

st.map(map_df[["lat", "lon"]])

# =============================
# 🎯 COLORED MAP
# =============================
st.header("🎯 Risk Visualization")

fig_map = px.scatter_mapbox(
    data,
    lat="Latitude",
    lon="Longitude",
    color="Risk",
    hover_name="Village",
    zoom=3,
    height=550,
    color_discrete_map={
        "Low Risk 🟢": "green",
        "Medium Risk 🟡": "yellow",
        "High Risk 🔴": "red"
    }
)

fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map, use_container_width=True)

# =============================
# 📊 BAR GRAPH
# =============================
st.header("📊 Risk Distribution")

risk_counts = data["Risk"].value_counts().reset_index()
risk_counts.columns = ["Risk", "Count"]

fig_bar = px.bar(
    risk_counts,
    x="Risk",
    y="Count",
    color="Risk",
    color_discrete_map={
        "Low Risk 🟢": "green",
        "Medium Risk 🟡": "yellow",
        "High Risk 🔴": "red"
    }
)

st.plotly_chart(fig_bar, use_container_width=True)

# =============================
# 📋 TABLE
# =============================
st.header("📋 Data Table")
st.dataframe(data, use_container_width=True)
