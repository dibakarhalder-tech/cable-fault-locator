
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

# Load main data
df = pd.read_csv("Final data - v7.csv", encoding="utf-8-sig")
df.columns = df.columns.map(str).str.strip()

# Inputs
station = st.selectbox("Please Select Cable Landing Station PFE",
                       ["Mtunzini", "Zafarana", "Mumbai", "Mombasa", "Maputo"])

ground = st.selectbox("Please select PFE Ground",
                      ["Station Ground", "Ocean Ground"])

voltage = st.number_input("Enter PFE Voltage", min_value=0.0)

# Column mapping
def get_column(station, ground):
    suffix = "SG" if ground == "Station Ground" else "OG"
    return f"PFE Out {station}_{suffix}"

def get_segment_col(station):
    return f"Segment from {station}"

def get_repeater_col(station):
    return f"Repeater from {station}"

def get_distance_col(station):
    return f"Distance from {station}"

def get_span_col(station):
    return f"Span length {station}"

# 🔴 NEW: Fault coordinate function
def get_fault_coordinates(route_df, station, fault_distance):

    dist_col = f"Distance_{station}"
    lat_col = f"Latitude_{station}"
    lon_col = f"Longitude_{station}"

    df = route_df[[dist_col, lat_col, lon_col]].copy()
    df = df.dropna()
    df = df.sort_values(by=dist_col)

    for i in range(len(df) - 1):

        d1 = df.iloc[i][dist_col]
        d2 = df.iloc[i + 1][dist_col]

        if d1 <= fault_distance <= d2:

            lat1 = df.iloc[i][lat_col]
            lon1 = df.iloc[i][lon_col]

            lat2 = df.iloc[i + 1][lat_col]
            lon2 = df.iloc[i + 1][lon_col]

            ratio = (fault_distance - d1) / (d2 - d1)

            lat = lat1 + ratio * (lat2 - lat1)
            lon = lon1 + ratio * (lon2 - lon1)

            return lat, lon

    return None, None


# ===================== MAIN CALCULATION =====================

if st.button("Calculate Fault Location"):

    try:
        col_v = get_column(station, ground)
        col_seg = get_segment_col(station)
        col_rep = get_repeater_col(station)
        col_dist = get_distance_col(station)

        df_sorted = df.sort_values(by=col_v)
        df_filtered = df_sorted[df_sorted[col_v] <= voltage]

        if len(df_filtered) == 0:
            st.error("Voltage too low")
        else:
            nearest = df_filtered.iloc[-1]

            v_ref = nearest[col_v]
            distance = (voltage - v_ref) / 0.64
            remaining_distance = distance
            base_distance = nearest[col_dist]

            total_distance = base_distance + remaining_distance
            col_span = get_span_col(station)

            next_rows = df_sorted[df_sorted[col_v] > v_ref]

            if len(next_rows) > 0:
                next_row = next_rows.iloc[0]
                next_rep = next_row[col_rep]
                span_length = next_row[col_span]

                if remaining_distance >= span_length:
                    st.success("📍 Fault Location Result")
                    st.write(f"**Segment:** {nearest[col_seg]}")
                    st.write(f"⚠️ Fault is located at repeater: {next_rep}")
                    st.write(f"**Distance from Cable Landing Station:** {round(base_distance + span_length,2)} KM")
                    st.stop()
            else:
                next_rep = "End of cable"

            st.success("📍 Fault Location Result")
            st.write(f"**Segment:** {nearest[col_seg]}")
            st.write(f"**From Reference:** {nearest[col_rep]}")
            st.write(f"**Distance:** {round(distance,2)} KM")
            st.write(f"**Direction:** Towards {next_rep}")
            st.write(f"**Distance from Cable Landing Station:** {round(total_distance,2)} KM")

            # ===================== MAP SECTION =====================

            import plotly.graph_objects as go

            route_df = pd.read_csv("cable_route_v7.csv", encoding="utf-8-sig")

            # 🔥 CLEAN DATA
            route_df.columns = route_df.columns.map(str).str.strip()
            route_df.columns = route_df.columns.str.replace(" ", "_")

            for col in route_df.columns:
                if "Distance_" in col or "Latitude" in col or "Longitude" in col:
                    route_df[col] = pd.to_numeric(route_df[col], errors='coerce')

            # 🔴 GET FAULT LAT/LON
            fault_lat, fault_lon = get_fault_coordinates(route_df, station, total_distance)

            fig = go.Figure()

            def draw_cable(lat_col, lon_col, name, color):
                df_temp = route_df[[lat_col, lon_col]].dropna()

                fig.add_trace(go.Scattermapbox(
                    lat=df_temp[lat_col],
                    lon=df_temp[lon_col],
                    mode='lines',
                    line=dict(width=4, color=color),
                    name=name
                ))

            # Draw routes
            draw_cable("Latitude_Mtunzini", "Longitude_Mtunzini", "Mtunzini Route", "blue")
            draw_cable("Latitude_Mumbai", "Longitude_Mumbai", "Mumbai Route", "cyan")
            draw_cable("Latitude_Mombasa", "Longitude_Mombasa", "Mombasa Route", "green")
            draw_cable("Latitude_Maputo", "Longitude_Maputo", "Maputo Route", "orange")
            draw_cable("Latitude_Dar", "Longitude_Dar", "Dar Route", "purple")
            draw_cable("Latitude_DJI", "Longitude_DJI", "DJI Route", "purple")

            # 🔴 ADD MARKER BEFORE PLOT
            if fault_lat is not None:
                fig.add_trace(go.Scattermapbox(
                    lat=[fault_lat],
                    lon=[fault_lon],
                    mode='markers',
                    marker=dict(size=14, color='red'),
                    name='Fault Location'
                ))

            fig.update_layout(
                mapbox_style="open-street-map",
                mapbox_zoom=3,
                mapbox_center={"lat": -5, "lon": 50},
                height=650
            )

            st.subheader("🌍 SEACOM Cable Map")
            st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Error: {e}")
