streamlit run app.py

import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz
import time

st.set_page_config(page_title="Bulk Location Time Finder", layout="wide")

st.title("Bulk Location → Current Local Time")
st.write("Upload a CSV file with a column named 'Location'")

geolocator = Nominatim(user_agent="bulk-timezone-app")
tf = TimezoneFinder()

@st.cache_data(show_spinner=False)
def geocode_location(location):
    try:
        geo = geolocator.geocode(location, timeout=10)
        if geo:
            return geo.latitude, geo.longitude
    except:
        pass
    return None, None

def get_local_time(lat, lon):
    try:
        tz = tf.timezone_at(lat=lat, lng=lon)
        if not tz:
            return None, None
        local_time = datetime.now(pytz.timezone(tz))
        return tz, local_time.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None, None

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if "Location" not in df.columns:
        st.error("CSV must contain a 'Location' column")
        st.stop()

    progress = st.progress(0)
    results = []

    for i, location in enumerate(df["Location"]):
        lat, lon = geocode_location(location)
        if lat and lon:
            tz, local_time = get_local_time(lat, lon)
        else:
            tz, local_time = None, None

        results.append([lat, lon, tz, local_time])
        progress.progress((i + 1) / len(df))
        time.sleep(0.1)

    df["Latitude"] = [r[0] for r in results]
    df["Longitude"] = [r[1] for r in results]
    df["Timezone"] = [r[2] for r in results]
    df["Local Time"] = [r[3] for r in results]

    st.dataframe(df, use_container_width=True)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "location_times.csv",
        "text/csv"
    )
