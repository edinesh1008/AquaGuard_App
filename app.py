import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="AquaGuard – Smart Water Monitoring",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------
# LOGIN SYSTEM
# ----------------------------------
APP_USERNAME = "admin"
APP_PASSWORD = "1234"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 AquaGuard Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == APP_USERNAME and password == APP_PASSWORD:
            st.session_state.logged_in = True
            st.success("✅ Login successful")
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# ----------------------------------
# TITLE
# ----------------------------------
st.title("💧 AquaGuard – Smart Community Water Health Monitoring")

# ----------------------------------
# INIT DATA
# ----------------------------------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Village", "Ecoli", "Turbidity", "Temperature",
        "Latitude", "Longitude", "Date", "Risk"
    ])

# ----------------------------------
# RULE-BASED RISK
# ----------------------------------
def rule_risk(ecoli, turbidity):
    if ecoli == "High":
        return "High Risk 🔴"
    elif ecoli == "Medium" or turbidity > 5:
        return "Medium Risk 🟠"
    else:
        return "Low Risk 🟢"

# ----------------------------------
# ML TRAINING
# ----------------------------------
def train_model(df):
    if len(df) < 5:
        return None

    temp = df.copy()

    temp["Ecoli_num"] = temp["Ecoli"].map({"Low":0, "Medium":1, "High":2})
    temp["Risk_num"] = temp["Risk"].map({
        "Low Risk 🟢":0,
        "Medium Risk 🟠":1,
        "High Risk 🔴":2
    })

    temp = temp.dropna()

    if len(temp) < 5:
        return None

    X = temp[["Ecoli_num", "Turbidity", "Temperature"]]
    y = temp["Risk_num"]

    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)
    return model

# ----------------------------------
# SIDEBAR ENTRY
# ----------------------------------
st.sidebar.header("📝 Enter Water Data")

village = st.sidebar.text_input("Village Name")
ecoli = st.sidebar.selectbox("E. coli", ["Low", "Medium", "High"])
turbidity = st.sidebar.number_input("Turbidity (NTU)", min_value=0.0)
temperature = st.sidebar.number_input("Temperature (°C)", min_value=0.0)
lat = st.sidebar.number_input("Latitude", value=12.9716)
lon = st.sidebar.number_input("Longitude", value=77.5946)
date = st.sidebar.date_input("Date", datetime.today())

# ----------------------------------
# SUBMIT DATA
# ----------------------------------
if st.sidebar.button("Submit Data"):
    if village.strip() == "":
        st.sidebar.error("⚠️ Please enter village name")
    else:
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
# CSV UPLOAD
# ----------------------------------
st.sidebar.header("📂 Upload CSV")

uploaded_file = st.sidebar.file_uploader("Upload water data CSV")

if uploaded_file is not None:
    try:
        csv_data = pd.read_csv(uploaded_file)

        required_cols = {"Village","Ecoli","Turbidity","Temperature","Latitude","Longitude","Date","Risk"}
        missing = required_cols - set(csv_data.columns)

        if missing:
            st.sidebar.error(f"CSV missing columns: {missing}")
        else:
            st.session_state.data = pd.concat(
                [st.session_state.data, csv_data],
                ignore_index=True
            )
            st.sidebar.success("✅ CSV Uploaded")

    except Exception as e:
        st.sidebar.error(f"CSV Error: {e}")

# ----------------------------------
# DASHBOARD
# ----------------------------------
data = st.session_state.data

st.header("📊 Live Dashboard")

if not data.empty:

    # METRICS
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Records", len(data))
    c2.metric("High Risk", (data["Risk"].str.contains("High")).sum())
    c3.metric("Safe Areas", (data["Risk"].str.contains("Low")).sum())

    st.divider()

    # TABLE
    st.subheader("📍 Village Table")
    st.dataframe(data, use_container_width=True)

    # ----------------------------------
    # ✅ FIXED HEATMAP
    # ----------------------------------
    st.subheader("🗺️ Risk Heatmap")

    try:
        map_data = data.rename(columns={
            "Latitude": "lat",
            "Longitude": "lon"
        })[["lat", "lon"]].dropna()

        if not map_data.empty:
            st.map(map_data)
        else:
            st.warning("No location data available for heatmap.")

    except Exception as e:
        st.error(f"Map error: {e}")

    # ----------------------------------
    # PIE CHART
    # ----------------------------------
    st.subheader("🥧 Risk Distribution")
    fig = px.pie(data, names="Risk")
    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------
    # ML PREDICTION
    # ----------------------------------
    st.subheader("🤖 ML Prediction")

    model = train_model(data)

    ecoli_num = {"Low":0, "Medium":1, "High":2}[ecoli]

    if model:
        pred = model.predict([[ecoli_num, turbidity, temperature]])[0]
        risk_label = ["Low Risk 🟢","Medium Risk 🟠","High Risk 🔴"][pred]
        st.info(f"Predicted Risk: {risk_label}")
    else:
        st.warning("Need at least 5 valid records to train ML model")

    # ----------------------------------
    # GOVERNMENT REPORT
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
