
import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Seacom Cable Fault Locator", layout="wide")

# Background
def set_bg():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("background.png");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg()

# Title
st.markdown("<h1 style='text-align: center;'>🌊 Welcome To Seacom Subsea Cable Fault Locator Tool</h1>", unsafe_allow_html=True)

# Load data
df = pd.read_csv("Final data - v6.csv", encoding="utf-8-sig")
df.columns = df.columns.str.strip()

# Inputs
station = st.selectbox("Please Select Cable Landing Station PFE", 
                       ["Mtunzini", "Zafarana", "Mumbai", "Mombasa", "Maputo"])

ground = st.selectbox("Please select PFE Ground", 
                      ["Station Ground", "Ocean Ground"])

voltage = st.number_input("Enter PFE Voltage", min_value=0.0)

# Mapping logic
def get_column(station, ground):
    suffix = "SG" if ground == "Station Ground" else "OG"
    return f"PFE Out {station}_{suffix}"

def get_segment_col(station):
    return f"Segment from {station}"

def get_repeater_col(station):
    return f"Repeater from {station}"

# Calculation
if st.button("Calculate Fault Location"):

    try:
        col_v = get_column(station, ground)
        col_seg = get_segment_col(station)
        col_rep = get_repeater_col(station)

        df_sorted = df.sort_values(by=col_v)

        df_filtered = df_sorted[df_sorted[col_v] <= voltage]

        if len(df_filtered) == 0:
            st.error("Voltage too low")
        else:
            nearest = df_filtered.iloc[-1]

            v_ref = nearest[col_v]
            distance = (voltage - v_ref) / 0.64

            next_rows = df_sorted[df_sorted[col_v] > v_ref]

            if len(next_rows) > 0:
                next_rep = next_rows.iloc[0][col_rep]
            else:
                next_rep = "End of cable"

            st.success("📍 Fault Location Result")

            st.write(f"**Segment:** {nearest[col_seg]}")
            st.write(f"**From Repeater:** {nearest[col_rep]}")
            st.write(f"**Distance:** {round(distance,2)} KM")
            st.write(f"**Direction:** Towards {next_rep}")

    except Exception as e:
        st.error(f"Error: {e}")
