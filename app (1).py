
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
df = pd.read_csv("Final data - v7.csv", encoding="utf-8-sig")
df.columns = df.columns.str.strip()

# Load cable route data
route_df = pd.read_csv("cable_route.csv")
route_df.columns = route_df.columns.str.strip()
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius KM
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


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

def get_distance_col(station):
    return f"Distance from {station}"

def get_span_col(station):
    return f"Span length {station}" 

def get_fault_coordinates(route_df, fault_distance, station):

    distance_col = f"Distance_{station}"

    route_df = route_df.sort_values(by=distance_col)

    for i in range(len(route_df) - 1):

        d1 = route_df.iloc[i][distance_col]
        d2 = route_df.iloc[i+1][distance_col]

        if pd.notna(d1) and pd.notna(d2):

            if d1 <= fault_distance <= d2:

                lat1 = route_df.iloc[i]["Cable route Latitude"]
                lon1 = route_df.iloc[i]["Cable route Longitude"]

                lat2 = route_df.iloc[i+1]["Cable route Latitude"]
                lon2 = route_df.iloc[i+1]["Cable route Longitude"]

                ratio = (fault_distance - d1) / (d2 - d1)

                lat = lat1 + ratio * (lat2 - lat1)
                lon = lon1 + ratio * (lon2 - lon1)

                return lat, lon

    return None, None

# Calculation
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
            remaining_distance = (voltage - v_ref) / 0.64
            base_distance = nearest[col_dist]

            total_distance = base_distance + remaining_distance
            fault_lat, fault_lon = get_fault_coordinates(route_df, total_distance, station)

            col_span = get_span_col(station)
            
            next_rows = df_sorted[df_sorted[col_v] > v_ref]

            if len(next_rows) > 0:
                next_row = next_rows.iloc[0]   # 🔥 IMPORTANT (single row)

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

            import plotly.graph_objects as go

            distance_col = f"Distance_{station}"
            route_filtered = route_df[route_df[distance_col].notna()]

            fig = go.Figure()

            # Cable route (clean)
            fig.add_trace(go.Scattermapbox(
                lat=route_filtered["Cable route Latitude"],
                lon=route_filtered["Cable route Longitude"],
                mode='lines',
                name='Cable Route'
            ))

            # 🔴 Fault marker
            if fault_lat is not None:
                fig.add_trace(go.Scattermapbox(
                    lat=[fault_lat],
                    lon=[fault_lon],
                    mode='markers',
                    marker=dict(size=16, color='red'),
                    name='Fault Location'
                ))

            fig.update_layout(
                mapbox_style="open-street-map",
                mapbox_zoom=6,
                mapbox_center={
                    "lat": fault_lat if fault_lat else route_filtered["Cable route Latitude"].mean(),
                    "lon": fault_lon if fault_lon else route_filtered["Cable route Longitude"].mean()
                },
                height=600
            )

            st.plotly_chart(fig)

            # TEMP marker (to confirm marker is visible)
            

            fig.add_trace(go.Scattermapbox(
                lat=[fault_point["Latitude"]],
                lon=[fault_point["Longitude"]],
                mode='markers',
                marker=dict(size=14, color='red'),
                name="Fault Location"
            ))

    except Exception as e:
        st.error(f"Error: {e}")
