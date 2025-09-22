import streamlit as st
import requests
import json
from datetime import datetime, timedelta

# Load API key from Streamlit Secrets (secure - set this in Streamlit Cloud dashboard)
WEATHER_API_KEY = st.secrets.get("WEATHER_API_KEY", "YOUR_WEATHERAPI_KEY_HERE")  # Fallback for local testing

# Crop to pesticide mapping (expand as needed)
pesticide_suggestions = {
    "wheat": "Fungicide XYZ (e.g., Carbendazim) - Protects against rust and smut.",
    "rice": "Insecticide ABC (e.g., Imidacloprid) - Controls stem borers and leaf folders.",
    "maize": "Herbicide DEF (e.g., Atrazine) - Manages weeds like grass and broadleaf.",
    "cotton": "Pesticide GHI (e.g., Endosulfan) - Targets bollworms and aphids.",
    "sugarcane": "Pesticide JKL (e.g., Chlorpyrifos) - Fights borers and termites.",
    # Add more: e.g., "potato": "Some pesticide"
}

# Streamlit App
st.set_page_config(page_title="10-Day Weather & Pesticide Chatbot", page_icon="???", layout="centered")

st.title("??? 10-Day Weather Forecast & Pesticide Chatbot for Ludhiana Farmers")
st.markdown("---")

# Initialize session state for chat history and conversation flow
if "messages" not in st.session_state:
    st.session_state.messages = []
if "step" not in st.session_state:
    st.session_state.step = 0  # 0: Greeting, 1: After forecast (ask crop), 2: After pesticide
if "crop" not in st.session_state:
    st.session_state.crop = ""

# Function to fetch 10-day forecast
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_10day_forecast():
    city = "Ludhiana"
    days = 10
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days={days}"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            forecast_list = []
            for i in range(days):
                day_data = data["forecast"]["forecastday"][i]
                date = day_data["date"]
                max_temp = day_data["day"]["maxtemp_c"]
                min_temp = day_data["day"]["mintemp_c"]
                avg_temp = day_data["day"]["avgtemp_c"]
                condition = day_data["day"]["condition"]["text"]
                forecast_list.append({
                    "date": date,
                    "max_temp": max_temp,
                    "min_temp": min_temp,
                    "avg_temp": avg_temp,
                    "condition": condition
                })
            return forecast_list
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching forecast: {e}")
        return None

# Function to get pesticide suggestion
def get_pesticide_suggestion(crop):
    crop_lower = crop.lower().strip()
    if crop_lower in pesticide_suggestions:
        return pesticide_suggestions[crop_lower]
    else:
        return "No specific suggestion available for this crop. Consult a local expert for tailored advice."

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input and logic
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot response logic based on step
    if st.session_state.step == 0:
        # Greet and fetch 10-day forecast
        forecast_data = get_10day_forecast()
        if forecast_data:
            forecast_msg = "**10-Day Weather Forecast for Ludhiana (starting today):\\n\\n"
            for day in forecast_data:
                forecast_msg += f"- **{day['date']}**: Max {day['max_temp']}°C / Min {day['min_temp']}°C | Avg {day['avg_temp']:.1f}°C | {day['condition']}\\n"
            forecast_msg += "\\nWhich crop are you growing? (e.g., wheat, rice, maize) I can suggest suitable pesticides based on the weather trends."
            st.session_state.messages.append({"role": "assistant", "content": forecast_msg})
            st.session_state.step = 1
        else:
            error_msg = "Sorry, I couldn\\'t fetch the 10-day forecast right now. Please try again later.\\n\\nWhich crop are you growing?"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.session_state.step = 1

    elif st.session_state.step == 1:
        # User provides crop
        st.session_state.crop = prompt
        pesticide = get_pesticide_suggestion(st.session_state.crop)
        pesticide_msg = f"**Suggested Pesticide for {st.session_state.crop} (considering upcoming weather):**\\n{pesticide}\\n\\n*Note: Weather forecast suggests planning applications during milder conditions. Always follow local guidelines and safety instructions.*\\n\\nThank you for using the chatbot! If you need more help, refresh the page."
        st.session_state.messages.append({"role": "assistant", "content": pesticide_msg})
        st.session_state.step = 2

    elif st.session_state.step == 2:
        # Conversation ended
        end_msg = "Our conversation has ended. Refresh the page to start a new one with the latest 10-day forecast and crop advice."
        st.session_state.messages.append({"role": "assistant", "content": end_msg})

    # Rerun to display bot response
    st.rerun()

# Initial greeting if no messages
if not st.session_state.messages:
    greeting = "Hello! ?? I\\'m your AI assistant for farmers in Ludhiana, Punjab. I provide 10-day weather forecasts and suggest pesticides based on your crop.\\n\\nType anything to get started (e.g., \\'Hi\\' or \\'Start\\')."
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    st.rerun()

# Sidebar for info
with st.sidebar:
    st.markdown("### About")
    st.markdown("- **Weather Source:** WeatherAPI (10-day forecast)")
    st.markdown("- **Crops Supported:** Wheat, Rice, Maize, Cotton, Sugarcane (add more in code)")
    st.markdown("- **Disclaimer:** Forecasts are estimates; pesticide suggestions are general. Consult agricultural experts.")

# Footer (optional: add your contact for farmers)
st.markdown("---")
st.markdown("*Built for Ludhiana farmers. Questions? Contact [your-email@example.com](mailto:your-email@example.com). ??*")	
