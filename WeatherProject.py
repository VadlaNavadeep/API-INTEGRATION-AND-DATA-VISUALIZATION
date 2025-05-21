
# --- Import Required Libraries ---
import streamlit as st                 # Streamlit for building the web UI
import requests                        # For making HTTP requests to the weather API
import pandas as pd                    # For data manipulation
import datetime                        # For working with dates
import random                          # To generate mock data
import matplotlib.pyplot as plt        # For plotting charts
import os                              # For accessing environment variables
from dotenv import load_dotenv         # For loading variables from .env file

# --- Load Environment Variables ---
load_dotenv()  # Reads API keys from a .env file in the same directory

# --- Constants and Settings ---
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"  # API endpoint for current weather
UNITS = "metric"  # Use Celsius units
CACHE_TTL = 600   # Cache data for 10 minutes to avoid unnecessary API calls
DEFAULT_CITIES = ["Mumbai", "New York", "Tokyo", "Paris", "Sydney"]  # Sidebar shortcuts

# Emojis to represent weather conditions for a friendly UI
WEATHER_EMOJIS = {
    "clear": "☀️",
    "clouds": "☁️",
    "rain": "🌧️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
    "drizzle": "🌦️",
    "fog": "🌁",
    "haze": "😶‍🌫️"
}

# --- Streamlit App Config ---
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌦️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Helper Function: Get API Key from .env ---
def get_api_key():
    api_key = os.getenv("OPENWEATHER_API_KEY")  # Read key from environment
    if not api_key:
        st.error("API key not found. Please check your .env file.")
        st.stop()
    return api_key

# --- Helper Function: Fetch Weather Data from API ---
@st.cache_data(ttl=CACHE_TTL)
def fetch_weather_data(city_name):
    api_key = get_api_key()
    params = {'q': city_name, 'appid': api_key, 'units': UNITS}
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        if response.status_code == 404:
            st.error(f"City '{city_name}' not found.")
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
        return None

# --- Helper Function: Display Weather Info ---
def display_weather_card(data):
    weather = data["weather"][0]
    main = data["main"]
    wind = data["wind"]
    condition = weather["main"].lower()
    emoji = WEATHER_EMOJIS.get(condition, "🌫️")
    st.subheader(f"{emoji} Current Weather in {data['name']}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Temperature", f"{main['temp']:.1f} °C")
        st.metric("Humidity", f"{main['humidity']}%")
    with col2:
        st.metric("Feels Like", f"{main['feels_like']:.1f} °C")
        st.metric("Pressure", f"{main['pressure']} hPa")
    with col3:
        st.metric("Wind Speed", f"{wind['speed']} m/s")
        st.metric("Conditions", weather["description"].title())

# --- Helper Function: Generate Fake Historical Data ---
def generate_mock_history(base_temp, base_humidity, days=5):
    dates = [(datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days, 0, -1)]
    return pd.DataFrame({
        "Date": dates,
        "Temperature": [round(base_temp + random.uniform(-3, 3), 1) for _ in dates],
        "Humidity": [max(30, min(100, base_humidity + random.randint(-15, 15))) for _ in dates],
        "Precipitation": [round(random.uniform(0, 10), 1) for _ in dates]
    })

# --- Helper Function: Plot Data Using Matplotlib ---
def create_matplotlib_visualizations(df):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
    ax1.plot(df["Date"], df["Temperature"], 'r-o')
    ax1.fill_between(df["Date"], df["Temperature"], alpha=0.1, color='red')
    ax1.set_title("Temperature Trend (°C)")
    ax1.grid(True)
    ax2.plot(df["Date"], df["Humidity"], 'b-o')
    ax2.fill_between(df["Date"], df["Humidity"], alpha=0.1, color='blue')
    ax2.set_title("Humidity Trend (%)")
    ax2.grid(True)
    ax3.bar(df["Date"], df["Precipitation"], color='skyblue')
    ax3.set_title("Precipitation (mm)")
    ax3.grid(True)
    plt.tight_layout()
    st.pyplot(fig)

# --- Main App Function ---
def main():
    st.title("🌦️🌍 Weather Dashboard")

    if "city" not in st.session_state:
        st.session_state.city = "Mumbai"

    with st.sidebar:
        st.header("Quick Access")
        for city in DEFAULT_CITIES:
            if st.button(city):
                st.session_state.city = city

    city = st.text_input("Enter city name:", st.session_state.city).strip()
    st.session_state.city = city

    if st.button("Get Weather"):
        with st.spinner("Fetching weather data..."):
            weather_data = fetch_weather_data(city)
            if weather_data:
                display_weather_card(weather_data)
                st.divider()
                st.subheader("📊 Let's look at some recent trends!")
                mock_data = generate_mock_history(
                    base_temp=weather_data["main"]["temp"],
                    base_humidity=weather_data["main"]["humidity"]
                )
                create_matplotlib_visualizations(mock_data)
                st.download_button(
                    label="📥 Download Data",
                    data=mock_data.to_csv(index=False),
                    file_name=f"{city}_weather.csv"
                )
            else:
                st.info("Please enter a valid city name to view the weather data.")

# --- Run the App ---
if __name__ == "__main__":
    main()
