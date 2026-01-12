import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz

st.set_page_config(page_title="Bulk Location Time Finder")

st.title("Bulk Location → Current Local Time")
st.write("Upload a CSV with a column named `Location`")

geolocator = Nominatim(user_agent="location-time-app")
tf = TimezoneFinder()

@st.cache_data
def get_location_data(location):
    try:
        geo = geolocator.geocode(location, timeout=10)
        if not geo:
            return None, None, None, None

        lat, lon = geo.latitude, geo.longitude
        tz = tf.timezone_at(lat=lat, lng=lon)
        if not tz:
            return lat, lon, None, None

        local_time = datetime.now(pytz.timezone(tz))
        return lat, lon, tz, local_time.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None, None, None, None

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if "Location" not in df.columns:
        st.error("CSV must contain a column named 'Location'")
        st.stop()

    results = df["Location"].apply(get_location_data)

    df["Latitude"] = results.apply(lambda x: x[0])
    df["Longitude"] = results.apply(lambda x: x[1])
    df["Timezone"] = results.apply(lambda x: x[2])
    df["Local Time"] = results.apply(lambda x: x[3])

    st.dataframe(df)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "location_times.csv",
        "text/csv"
    )
