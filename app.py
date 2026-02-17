import streamlit as st
import pandas as pd
import numpy as np

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="AquaGuard AI",
    page_icon="💧",
    layout="wide"
)

# ==============================
# CUSTOM CSS (Premium UI)
# ==============================
st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: bold;
    color: #00B4D8;
}
.metric-card {
    background-color: #0f172a;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">💧 AquaGuard AI – India Water Risk Intelligence</p>', unsafe_allow_html=True)

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    return pd.read_csv("india_water_data.csv")

df = load_data()

# ==============================
# AI RISK SCORE FUNCTION
# ==============================
def ai_risk_score(row):
    score = 0

    if row["Ecoli_Level"] == "High":
        score += 60
    elif row["Ecoli_Level"] == "Medium":
        score += 30

    score += min(row["Turbidity_NTU"], 40)

    return min(score, 100)

df["AI_Risk_%"] = df.apply(ai_risk_score, axis=1)

# ==============================
# SIDEBAR FILTER
# ==============================
st.sidebar.header("🔍 Filter Panel")

risk_filter = st.sidebar.selectbox(
    "Select Risk Level",
    ["ALL", "SAFE", "WARNING", "HIGH RISK"]
)

if risk_filter != "ALL":
    df_filtered = df[df["Risk_Level"] == risk_filter]
else:
    df_filtered = df

# ==============================
# METRICS DASHBOARD
# ==============================
safe_count = (df["Risk_Level"]=="SAFE").sum()
warn_count = (df["Risk_Level"]=="WARNING").sum()
high_count = (df["Risk_Level"]=="HIGH RISK").sum()

col1, col2, col3 = st.columns(3)

col1.metric("🟢 Safe Zones", safe_count)
col2.metric("🟡 Warning Zones", warn_count)
col3.metric("🔴 High Risk Zones", high_count)

# ==============================
# HEATMAP MAP
# ==============================
st.subheader("🗺️ India Risk Heatmap")

st.map(df_filtered[["Latitude","Longitude"]])

# ==============================
# AI RISK DISTRIBUTION
# ==============================
st.subheader("🤖 AI Risk Score Distribution")

st.progress(int(df["AI_Risk_%"].mean()))

st.write(f"### Average AI Risk: {df['AI_Risk_%'].mean():.2f}%")

# ==============================
# DATA TABLE
# ==============================
st.subheader("📋 Detailed Monitoring Data")

st.dataframe(df_filtered, use_container_width=True)

# ==============================
# DOWNLOAD BUTTON
# ==============================
st.download_button(
    "⬇️ Download Full Dataset",
    df.to_csv(index=False),
    file_name="india_water_data.csv",
    mime="text/csv"
)

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.caption("🚀 AquaGuard AI | Makeathon Finals Project | Team Aqua Titans")
