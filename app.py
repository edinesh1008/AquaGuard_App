import streamlit as st
import pandas as pd

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="AquaGuard – Early Warning System",
    page_icon="💧",
    layout="wide"
)

# -----------------------------
# Title
# -----------------------------
st.title("💧 AquaGuard – Smart Water Risk Monitor")
st.markdown("### Community Water Quality Early Warning System")

# -----------------------------
# Sidebar Inputs
# -----------------------------
st.sidebar.header("📊 Enter Water Test Data")

village = st.sidebar.text_input("Village Name")

ecoli = st.sidebar.selectbox(
    "E. coli Level",
    ["Low", "Medium", "High"]
)

turbidity = st.sidebar.slider(
    "Turbidity (NTU)",
    0, 50, 5
)

temperature = st.sidebar.slider(
    "Temperature (°C)",
    0, 50, 25
)

# -----------------------------
# Risk Logic Function
# -----------------------------
def calculate_risk(ecoli, turbidity):
    if ecoli == "High" or turbidity > 25:
        return "HIGH RISK"
    elif ecoli == "Medium" or turbidity > 10:
        return "WARNING"
    else:
        return "SAFE"

risk = calculate_risk(ecoli, turbidity)

# -----------------------------
# Display Result
# -----------------------------
st.header("🚨 Risk Assessment Result")

if risk == "SAFE":
    st.success("🟢 SAFE – Water is Suitable for Use")

elif risk == "WARNING":
    st.warning("🟡 WARNING – Water Needs Treatment")

else:
    st.error("🔴 HIGH RISK – Immediate Action Required")

# -----------------------------
# Recommendations
# -----------------------------
st.subheader("📌 Recommended Action")

if risk == "SAFE":
    st.write("✔ Continue regular monitoring")
    st.write("✔ Maintain sanitation practices")

elif risk == "WARNING":
    st.write("⚠ Boil water before drinking")
    st.write("⚠ Consider chlorination")

else:
    st.write("🚨 Avoid using this water source")
    st.write("🚨 Notify health authorities immediately")

# -----------------------------
# Village Info Display
# -----------------------------
if village:
    st.info(f"📍 Monitoring Location: **{village}**")

# -----------------------------
# Weekly Trend Chart (Demo)
# -----------------------------
st.subheader("📈 Weekly Risk Trend")

data = {
    "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "Risk Score": [1, 1, 2, 2, 3, 2, 1]
}

df = pd.DataFrame(data)
st.line_chart(df.set_index("Day"))

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("AquaGuard © 2026 | Makeathon Finalist Project")
