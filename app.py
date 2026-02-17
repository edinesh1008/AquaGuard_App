import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AquaGuard Lite",
    layout="wide"
)

st.title("💧 AquaGuard – Water Risk Monitoring")

# -----------------------------
# INIT DATA
# -----------------------------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Village", "Ecoli", "Turbidity",
        "Latitude", "Longitude", "Date", "Risk"
    ])

# -----------------------------
# RISK PREDICTION
# -----------------------------
def predict_risk(ecoli, turbidity):
    if ecoli == "High":
        return "High Risk 🔴", "red"
    elif ecoli == "Medium" or turbidity > 5:
        return "Medium Risk 🟡", "yellow"
    else:
        return "Low Risk 🟢", "green"

# -----------------------------
# SIDEBAR INPUT
# -----------------------------
st.sidebar.header("📝 Enter Water Data")

village = st.sidebar.text_input("Village Name")
ecoli = st.sidebar.selectbox("E. coli Level", ["Low", "Medium", "High"])
turbidity = st.sidebar.number_input("Turbidity (NTU)", min_value=0.0)
lat = st.sidebar.number_input("Latitude", value=12.9716)
lon = st.sidebar.number_input("Longitude", value=77.5946)
date = st.sidebar.date_input("Date", datetime.today())

# -----------------------------
# SUBMIT
# -----------------------------
if st.sidebar.button("Predict & Add"):

    if village.strip() == "":
        st.sidebar.error("Enter village name")
    else:
        risk_label, risk_color = predict_risk(ecoli, turbidity)

        new_row = pd.DataFrame([{
            "Village": village,
            "Ecoli": ecoli,
            "Turbidity": turbidity,
            "Latitude": lat,
            "Longitude": lon,
            "Date": date,
            "Risk": risk_label,
            "Color": risk_color
        }])

        st.session_state.data = pd.concat(
            [st.session_state.data, new_row],
            ignore_index=True
        )

        st.sidebar.success(f"Prediction: {risk_label}")

# -----------------------------
# MAIN DASHBOARD
# -----------------------------
data = st.session_state.data

if not data.empty:

    st.header("🗺️ Risk Map")

    # rename for streamlit map safety
    map_data = data.rename(columns={
        "Latitude": "lat",
        "Longitude": "lon"
    })

    st.map(map_data[["lat", "lon"]])

    # -----------------------------
    # COLORED SCATTER MAP (BETTER)
    # -----------------------------
    st.header("🎯 Risk Visualization")

    fig = px.scatter_mapbox(
        data,
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

    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # BAR GRAPH
    # -----------------------------
    st.header("📊 Risk Distribution")

    risk_counts = data["Risk"].value_counts().reset_index()
    risk_counts.columns = ["Risk", "Count"]

    fig2 = px.bar(
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

    st.plotly_chart(fig2, use_container_width=True)

    # -----------------------------
    # TABLE
    # -----------------------------
    st.header("📋 Data Table")
    st.dataframe(data, use_container_width=True)

else:
    st.info("Enter water data from sidebar to begin.")
