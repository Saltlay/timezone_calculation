import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz

st.set_page_config(page_title="Bulk Location Time Finder")

st.title("Bulk Location → Current Local Time")
st.write("Add locations manually or upload a CSV. Get current local time instantly.")

geolocator = Nominatim(user_agent="location-time-app")
tf = TimezoneFinder()

@st.cache_data
def process_location(location):
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

# -----------------------------
# INPUT METHODS
# -----------------------------

st.subheader("Option 1: Upload CSV")
uploaded_file = st.file_uploader(
    "CSV must have a column named `Location`",
    type=["csv"]
)

st.subheader("Option 2: Paste multiple locations")
manual_text = st.text_area(
    "Enter one location per line",
    placeholder="New York USA\nBerlin Germany\nMumbai India"
)

st.subheader("Option 3: Add locations manually")
single_location = st.text_input("Enter a single location")

# -----------------------------
# COLLECT DATA
# -----------------------------

locations = []

if uploaded_file:
    df_upload = pd.read_csv(uploaded_file)
    if "Location" in df_upload.columns:
        locations.extend(df_upload["Location"].dropna().tolist())
    else:
        st.error("Uploaded CSV must contain a 'Location' column")

if manual_text:
    manual_locations = [
        loc.strip()
        for loc in manual_text.split("\n")
        if loc.strip()
    ]
    locations.extend(manual_locations)

if single_location:
    locations.append(single_location.strip())

# Remove duplicates
locations = list(dict.fromkeys(locations))

# -----------------------------
# PROCESS DATA
# -----------------------------

if locations and st.button("Get Current Time"):
    results = []

    with st.spinner("Processing locations..."):
        for loc in locations:
            lat, lon, tz, local_time = process_location(loc)
            results.append([loc, lat, lon, tz, local_time])

    result_df = pd.DataFrame(
        results,
        columns=["Location", "Latitude", "Longitude", "Timezone", "Local Time"]
    )

    st.success("Done!")
    st.dataframe(result_df, use_container_width=True)

    st.download_button(
        "Download Results as CSV",
        result_df.to_csv(index=False),
        "location_times.csv",
        "text/csv"
    )
