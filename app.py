import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="AquaGuard Final", layout="wide")
st.title("💧 AquaGuard – Smart Water Risk & Outbreak Monitoring")

# =====================================================
# LOAD DATA (UPDATED FILE NAME)
# =====================================================
@st.cache_data
def load_data():
    return pd.read_csv("aquaguard_northeast_final_dataset.csv")

if "data" not in st.session_state:
    try:
        st.session_state.data = load_data()
    except Exception as e:
        st.error(f"❌ Data load error: {e}")
        st.stop()

data = st.session_state.data.copy()

# =====================================================
# ✅ VERIFY REQUIRED COLUMNS (judge safety)
# =====================================================
required_cols = {
    "Village","State","Latitude","Longitude",
    "Risk","pH","Temperature","Salinity",
    "Alkalinity","Dissolved O2","Bacterial contamination"
}

missing = required_cols - set(data.columns)
if missing:
    st.error(f"❌ Dataset missing columns: {missing}")
    st.stop()

# =====================================================
# 🎛️ SIDEBAR FILTERS
# =====================================================
st.sidebar.header("🎛️ Dashboard Filters")

risk_option = st.sidebar.selectbox(
    "Select Risk Category",
    ["All", "High Risk 🔴", "Medium Risk 🟡", "Low Risk 🟢"]
)

state_option = st.sidebar.selectbox(
    "Select Northeast State",
    ["All"] + sorted(data["State"].unique().tolist())
)

# Apply filters
data_view = data.copy()

if risk_option != "All":
    data_view = data_view[data_view["Risk"] == risk_option]

if state_option != "All":
    data_view = data_view[data_view["State"] == state_option]

# =====================================================
# 📊 RISK DASHBOARD
# =====================================================
st.header("📊 Risk Categories Dashboard")

high = (data_view["Risk"] == "High Risk 🔴").sum()
med = (data_view["Risk"] == "Medium Risk 🟡").sum()
low = (data_view["Risk"] == "Low Risk 🟢").sum()

c1, c2, c3 = st.columns(3)
c1.metric("🔴 High Risk", high)
c2.metric("🟡 Medium Risk", med)
c3.metric("🟢 Safe", low)

# =====================================================
# 📈 OUTBREAK PROBABILITY
# =====================================================
def outbreak_probability(df):
    score_map = {
        "Low Risk 🟢": 0.2,
        "Medium Risk 🟡": 0.5,
        "High Risk 🔴": 0.9
    }
    scores = df["Risk"].map(score_map).fillna(0.3)
    return round(scores.mean() * 100, 2)

prob = outbreak_probability(data_view) if not data_view.empty else 0

st.header("📈 Outbreak Probability")

st.metric("Predicted Probability", f"{prob}%")

days = st.slider("Simulation Days", 7, 60, 30)

base = prob / 100
growth = [min(100, (base * (1.06 ** i)) * 100) for i in range(days)]

sim_df = pd.DataFrame({
    "Day": range(1, days + 1),
    "Outbreak Risk %": growth
})

fig_prob = px.line(sim_df, x="Day", y="Outbreak Risk %",
                   title="Outbreak Probability Trend")
st.plotly_chart(fig_prob, use_container_width=True)

# =====================================================
# 🗺️ RISK VISUALIZATION
# =====================================================
st.header("🗺️ Risk Visualization")

if not data_view.empty:
    map_df = data_view.rename(columns={"Latitude": "lat", "Longitude": "lon"})
    st.map(map_df[["lat", "lon"]])

    fig_map = px.scatter_mapbox(
        data_view,
        lat="Latitude",
        lon="Longitude",
        color="Risk",
        hover_name="Village",
        hover_data=["State"],
        zoom=5,
        height=520,
        color_discrete_map={
            "Low Risk 🟢": "green",
            "Medium Risk 🟡": "yellow",
            "High Risk 🔴": "red"
        }
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)

# =====================================================
# 🚨 ALERT HISTORY
# =====================================================
st.header("🚨 Alert History")

if "alerts" not in st.session_state:
    st.session_state.alerts = []

def generate_alert(probability):
    status = "RISK 🔴" if probability > 60 else "SAFE 🟢"
    st.session_state.alerts.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Status": status,
        "Probability": probability
    })

generate_alert(prob)

st.dataframe(pd.DataFrame(st.session_state.alerts),
             use_container_width=True)

# =====================================================
# 🛡️ PREVENTION RECOMMENDATION
# =====================================================
st.header("🛡️ Prevention Recommendation")

if prob > 70:
    st.error("⚠️ High Risk Zone")
    st.markdown("""
**Recommended Actions**
- Immediate chlorination  
- Boil-water advisory  
- Deploy medical teams  
- Source contamination tracing  
- Emergency public warning  
""")

elif prob > 40:
    st.warning("⚠️ Moderate Risk")
    st.markdown("""
**Preventive Steps**
- Increase monitoring  
- Inspect pipelines  
- Alert health workers  
- Community awareness  
""")

else:
    st.success("✅ Currently Safe")
    st.markdown("""
**Routine Safety**
- Maintain weekly testing  
- Ensure sanitation  
- Continue surveillance  
""")

# =====================================================
# 📋 EXPANDED DATA TABLE
# =====================================================
st.header("📋 Northeast Water Quality Table")

st.dataframe(data_view, use_container_width=True)
