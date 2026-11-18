import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Weather App",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ Weather Forecast App")
st.write("Check current weather and five-day forecasts for any city.")

# Weather descriptions
def weather_description(code):
    weather = {
        0: ("Clear Sky", "☀️"),
        1: ("Mainly Clear", "🌤️"),
        2: ("Partly Cloudy", "⛅"),
        3: ("Overcast", "☁️"),
        45: ("Foggy", "🌫️"),
        48: ("Foggy", "🌫️"),
        51: ("Light Drizzle", "🌦️"),
        53: ("Drizzle", "🌦️"),
        55: ("Heavy Drizzle", "🌧️"),
        61: ("Light Rain", "🌦️"),
        63: ("Moderate Rain", "🌧️"),
        65: ("Heavy Rain", "🌧️"),
        71: ("Light Snow", "🌨️"),
        73: ("Snow", "❄️"),
        75: ("Heavy Snow", "❄️"),
        80: ("Rain Showers", "🌦️"),
        81: ("Rain Showers", "🌧️"),
        82: ("Heavy Showers", "⛈️"),
        95: ("Thunderstorm", "⛈️"),
        96: ("Thunderstorm with Hail", "⛈️"),
        99: ("Heavy Thunderstorm", "⛈️")
    }
    return weather.get(code, ("Unknown", "🌡️"))


# City search
city = st.text_input(
    "Enter your city name",
    placeholder="Example: Bengaluru"
)

if st.button("Get Weather", type="primary"):

    if not city.strip():
        st.warning("Please enter a city name.")

    else:
        try:
            with st.spinner("Fetching weather information..."):

                # Find city coordinates
                geo_url = "https://geocoding-api.open-meteo.com/v1/search"

                geo_response = requests.get(
                    geo_url,
                    params={
                        "name": city.strip(),
                        "count": 1,
                        "language": "en",
                        "format": "json"
                    },
                    timeout=15
                )

                geo_response.raise_for_status()
                geo_data = geo_response.json()

                if not geo_data.get("results"):
                    st.error("City not found. Please try another city.")

                else:
                    place = geo_data["results"][0]

                    latitude = place["latitude"]
                    longitude = place["longitude"]

                    # Get weather information
                    weather_url = "https://api.open-meteo.com/v1/forecast"

                    weather_response = requests.get(
                        weather_url,
                        params={
                            "latitude": latitude,
                            "longitude": longitude,
                            "current": (
                                "temperature_2m,"
                                "relative_humidity_2m,"
                                "apparent_temperature,"
                                "weather_code,"
                                "wind_speed_10m"
                            ),
                            "daily": (
                                "weather_code,"
                                "temperature_2m_max,"
                                "temperature_2m_min,"
                                "precipitation_probability_max"
                            ),
                            "forecast_days": 5,
                            "timezone": "auto"
                        },
                        timeout=20
                    )

                    weather_response.raise_for_status()
                    data = weather_response.json()

                    current = data["current"]
                    daily = data["daily"]

                    description, emoji = weather_description(
                        current["weather_code"]
                    )

                    st.success(
                        f"Weather for {place['name']}, "
                        f"{place.get('country', '')}"
                    )

                    st.subheader(f"{emoji} {description}")

                    # Current weather
                    col1, col2, col3, col4 = st.columns(4)

                    col1.metric(
                        "Temperature",
                        f"{current['temperature_2m']} °C"
                    )

                    col2.metric(
                        "Feels Like",
                        f"{current['apparent_temperature']} °C"
                    )

                    col3.metric(
                        "Humidity",
                        f"{current['relative_humidity_2m']}%"
                    )

                    col4.metric(
                        "Wind Speed",
                        f"{current['wind_speed_10m']} km/h"
                    )

                    st.subheader("📅 Five-Day Forecast")

                    forecast_rows = []

                    for i in range(len(daily["time"])):
                        desc, icon = weather_description(
                            daily["weather_code"][i]
                        )

                        forecast_rows.append({
                            "Date": daily["time"][i],
                            "Weather": f"{icon} {desc}",
                            "Max Temp (°C)": daily["temperature_2m_max"][i],
                            "Min Temp (°C)": daily["temperature_2m_min"][i],
                            "Rain Chance (%)": daily[
                                "precipitation_probability_max"
                            ][i]
                        })

                    st.dataframe(
                        pd.DataFrame(forecast_rows),
                        use_container_width=True,
                        hide_index=True
                    )

                    st.caption("Weather data provided by Open-Meteo.")

        except requests.exceptions.RequestException as e:
            st.error(f"Unable to connect to weather service: {e}")

        except Exception as e:
            st.error(f"Something went wrong: {e}")