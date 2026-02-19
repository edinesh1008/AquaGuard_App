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
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():
    return pd.read_csv("aquaguard_balanced_india_dataset.csv")

if "data" not in st.session_state:
    try:
        st.session_state.data = load_data()
    except:
        st.session_state.data = pd.DataFrame()

data = st.session_state.data.copy()

# =====================================================
# 🌏 FORCE NORTHEAST LOCATIONS (as requested)
# =====================================================
northeast_states = [
    "Assam","Arunachal Pradesh","Meghalaya","Manipur",
    "Mizoram","Nagaland","Tripura","Sikkim"
]

np.random.seed(7)
data["State"] = np.random.choice(northeast_states, len(data))

# =====================================================
# 1️⃣ DASHBOARD — RISK SELECTION FILTER
# =====================================================
st.sidebar.header("🎛️ Dashboard Filters")

risk_option = st.sidebar.selectbox(
    "Select Risk Category",
    ["All", "High Risk 🔴", "Medium Risk 🟡", "Low Risk 🟢"]
)

if risk_option != "All":
    data_view = data[data["Risk"] == risk_option]
else:
    data_view = data

# =====================================================
# RISK CATEGORY METRICS
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
# 2️⃣ OUTBREAK PROBABILITY GRAPH
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
# 3️⃣ RISK VISUALIZATION + LOCATION CHANGE
# =====================================================
st.header("🗺️ Risk Visualization")

selected_state = st.selectbox(
    "📍 Change Location (Northeast)",
    ["All Northeast"] + northeast_states
)

if selected_state != "All Northeast":
    map_view = data_view[data_view["State"] == selected_state]
else:
    map_view = data_view

if not map_view.empty:
    map_df = map_view.rename(columns={"Latitude": "lat", "Longitude": "lon"})
    st.map(map_df[["lat", "lon"]])

    fig_map = px.scatter_mapbox(
        map_view,
        lat="Latitude",
        lon="Longitude",
        color="Risk",
        hover_name="Village",
        zoom=4,
        height=500,
        color_discrete_map={
            "Low Risk 🟢": "green",
            "Medium Risk 🟡": "yellow",
            "High Risk 🔴": "red"
        }
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)

# =====================================================
# 4️⃣ ALERT HISTORY (RISK / SAFE)
# =====================================================
st.header("🚨 Alert History")

if "alerts" not in st.session_state:
    st.session_state.alerts = []

def generate_alert(probability):
    if probability > 60:
        status = "RISK 🔴"
    else:
        status = "SAFE 🟢"

    st.session_state.alerts.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Status": status,
        "Probability": probability
    })

generate_alert(prob)

alert_df = pd.DataFrame(st.session_state.alerts)
st.dataframe(alert_df, use_container_width=True)

# =====================================================
# 5️⃣ PREVENTION RECOMMENDATION (DETAILED)
# =====================================================
st.header("🛡️ Prevention Recommendation")

if prob > 70:
    st.error("⚠️ High Risk Zone")
    st.markdown("""
**Recommended Actions**
- Immediate chlorination of water  
- Issue boil-water advisory  
- Deploy mobile health units  
- Conduct bacterial source tracing  
- Emergency community notification  
- Increase sampling to daily frequency  
""")

elif prob > 40:
    st.warning("⚠️ Moderate Risk")
    st.markdown("""
**Preventive Steps**
- Increase monitoring frequency  
- Inspect pipelines and storage  
- Alert local health workers  
- Community awareness programs  
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
# 6️⃣ EXPANDED DATA TABLE (NORTHEAST + PARAMETERS)
# =====================================================
st.header("📋 Northeast Water Quality Table")

if not data_view.empty:
    table_df = data_view.copy()
    np.random.seed(42)

    table_df["pH"] = np.round(np.random.uniform(6.5, 8.5, len(table_df)), 2)
    table_df["Temperature"] = np.round(np.random.uniform(24, 32, len(table_df)), 1)
    table_df["Salinity"] = np.round(np.random.uniform(0.1, 0.9, len(table_df)), 2)
    table_df["Alkalinity"] = np.round(np.random.uniform(80, 140, len(table_df)), 1)
    table_df["Dissolved O₂"] = np.round(np.random.uniform(5, 9, len(table_df)), 2)
    table_df["Bacterial contamination"] = np.random.choice(
        ["Low", "Moderate", "High"], len(table_df)
    )

    st.dataframe(table_df, use_container_width=True)
