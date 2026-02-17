import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# ----------------------------------
# Page Config (Mobile Friendly)
# ----------------------------------
st.set_page_config(
    page_title="Smart Water Monitoring",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------
# Simple Login System
# ----------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Water Monitoring Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# ----------------------------------
# Title
# ----------------------------------
st.title("💧 Smart Community Water Health Monitoring")

# ----------------------------------
# Initialize Data
# ----------------------------------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Village", "Ecoli", "Turbidity", "Temperature",
        "Latitude", "Longitude", "Date", "Risk"
    ])

# ----------------------------------
# ML Model (Simple Training)
# ----------------------------------
def train_model(df):
    if len(df) < 5:
        return None

    temp = df.copy()
    temp["Ecoli_num"] = temp["Ecoli"].map({"Low":0,"Medium":1,"High":2})
    temp["Risk_num"] = temp["Risk"].map({
        "Low Risk 🟢":0,
        "Medium Risk 🟠":1,
        "High Risk 🔴":2
    })

    X = temp[["Ecoli_num", "Turbidity", "Temperature"]]
    y = temp["Risk_num"]

    model = RandomForestClassifier()
    model.fit(X, y)
    return model

# ----------------------------------
# Sidebar — Data Entry
# ----------------------------------
st.sidebar.header("📝 Enter Water Data")

village = st.sidebar.text_input("Village Name")
ecoli = st.sidebar.selectbox("E. coli", ["Low","Medium","High"])
turbidity = st.sidebar.number_input("Turbidity", min_value=0.0)
temperature = st.sidebar.number_input("Temperature", min_value=0.0)
lat = st.sidebar.number_input("Latitude", value=12.97)
lon = st.sidebar.number_input("Longitude", value=77.59)
date = st.sidebar.date_input("Date", datetime.today())

# ----------------------------------
# Basic Rule Risk
# ----------------------------------
def rule_risk(ecoli, turbidity):
    if ecoli == "High":
        return "High Risk 🔴"
    elif ecoli == "Medium" or turbidity > 5:
        return "Medium Risk 🟠"
    else:
        return "Low Risk 🟢"

# ----------------------------------
# Submit Data
# ----------------------------------
if st.sidebar.button("Submit Data"):
    if village:
        risk = rule_risk(ecoli, turbidity)

        new_row = pd.DataFrame([{
            "Village": village,
            "Ecoli": ecoli,
            "Turbidity": turbidity,
            "Temperature": temperature,
            "Latitude": lat,
            "Longitude": lon,
            "Date": date,
            "Risk": risk
        }])

        st.session_state.data = pd.concat(
            [st.session_state.data, new_row],
            ignore_index=True
        )

        st.sidebar.success("✅ Data Added")

# ----------------------------------
# CSV Upload
# ----------------------------------
st.sidebar.header("📂 Upload CSV")

uploaded_file = st.sidebar.file_uploader("Upload water data CSV")

if uploaded_file:
    csv_data = pd.read_csv(uploaded_file)
    st.session_state.data = pd.concat(
        [st.session_state.data, csv_data],
        ignore_index=True
    )
    st.sidebar.success("CSV Uploaded")

# ----------------------------------
# Dashboard
# ----------------------------------
data = st.session_state.data

st.header("📊 Live Dashboard")

if not data.empty:

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Records", len(data))
    c2.metric("High Risk", (data["Risk"].str.contains("High")).sum())
    c3.metric("Safe", (data["Risk"].str.contains("Low")).sum())

    st.divider()

    # Table
    st.subheader("📍 Village Table")
    st.dataframe(data, use_container_width=True)

    # ----------------------------------
    # Heatmap
    # ----------------------------------
    st.subheader("🗺️ Risk Heatmap")

    map_data = data[["Latitude","Longitude"]].dropna()

    if not map_data.empty:
        st.map(map_data)

    # ----------------------------------
    # Pie Chart
    # ----------------------------------
    st.subheader("🥧 Risk Distribution")
    fig = px.pie(data, names="Risk")
    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------
    # Train ML
    # ----------------------------------
    model = train_model(data)

    st.subheader("🤖 ML Prediction")

    ecoli_num = {"Low":0,"Medium":1,"High":2}[ecoli]

    if model:
        pred = model.predict([[ecoli_num, turbidity, temperature]])[0]
        risk_label = ["Low Risk 🟢","Medium Risk 🟠","High Risk 🔴"][pred]
        st.info(f"Predicted Risk: {risk_label}")
    else:
        st.warning("Need more data to train ML model")

    # ----------------------------------
    # Government Report
    # ----------------------------------
    st.subheader("📄 Government Report")

    if st.button("Generate Report"):
        summary = data["Risk"].value_counts()
        st.write("### Risk Summary")
        st.write(summary)

        csv = data.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Full Report",
            csv,
            "water_quality_report.csv",
            "text/csv"
        )

else:
    st.info("Enter or upload data to begin.")
