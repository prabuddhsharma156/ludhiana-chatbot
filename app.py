import streamlit as st
import requests
from datetime import datetime, timedelta

# Load API key from Streamlit Secrets (secure - set this in Streamlit Cloud dashboard)
WEATHER_API_KEY = st.secrets.get("WEATHER_API_KEY", "a471efb91f4c4e29ac9135831252209")  # Fallback for local testing

# Crop to pesticide mapping (Hindi descriptions)
pesticide_suggestions = {
    "wheat": "फंगीसाइड XYZ (उदाहरण: कार्बेंडाजिम) - जंग और स्मट से सुरक्षा।",
    "rice": "कीटनाशक ABC (उदाहरण: इमिडाक्लोप्रिड) - तना बोरर और पत्ती फोल्डर नियंत्रण।",
    "maize": "खरपतवारनाशक DEF (उदाहरण: एट्राजीन) - घास और चौड़ी पत्ती वाले खरपतवार प्रबंधन।",
    "cotton": "कीटनाशक GHI (उदाहरण: एंडोसल्फान) - बोलवर्म और एफिड्स पर निशाना।",
    "sugarcane": "कीटनाशक JKL (उदाहरण: क्लोरपायरीफॉस) - बोरर और दीमक से लड़ाई।",
    # Add more: e.g., "potato": "Some pesticide in Hindi"
}

# States and Districts (simple dict - add more as needed)
states_districts = {
    "पंजाब": ["लुधियाना", "अमृतसर", "जालंधर", "पटियाला"],
    "हरियाणा": ["करनाल", "अंबाला", "कुरुक्षेत्र", "सिरसा"],
    "उत्तर प्रदेश": ["लखनऊ", "कानपुर", "आगरा", "वाराणसी"],
    # Add more states: e.g., "महाराष्ट्र": ["मुंबई", "पुणे"]
}

# Crop prices: National average for India (from Agmarknet - update weekly; focused on Ludhiana crops but India-wide)
# Format: {"crop": {"modal_price": 2300, "min_price": 2200, "max_price": 2400, "avg_yield_quintal_per_acre": 20}}
crop_prices = {
    "wheat": {"modal_price": 2300, "min_price": 2200, "max_price": 2400, "avg_yield_quintal_per_acre": 20},  # National avg
    "rice": {"modal_price": 2000, "min_price": 1900, "max_price": 2100, "avg_yield_quintal_per_acre": 25},
    "maize": {"modal_price": 1700, "min_price": 1600, "max_price": 1800, "avg_yield_quintal_per_acre": 18},
    "cotton": {"modal_price": 6000, "min_price": 5800, "max_price": 6200, "avg_yield_quintal_per_acre": 10},
    "sugarcane": {"modal_price": 330, "min_price": 320, "max_price": 340, "avg_yield_quintal_per_acre": 400},
    # Update from agmarknet.gov.in for national/Ludhiana data
}

# Streamlit App (Hindi title and config)
st.set_page_config(page_title="10-दिन मौसम और फसल सलाह चैटबॉट", page_icon="🌤️", layout="centered")

st.title("🌤️ किसानों के लिए 10-दिन मौसम पूर्वानुमान और फसल सलाह चैटबॉट")
st.markdown("---")

# Initialize session state for steps (no chat input - button-based)
if "step" not in st.session_state:
    st.session_state.step = 0  # 0: State, 1: District, 2: Weather, 3: Crop, 4: Pesticide, 5: Prices
if "selected_state" not in st.session_state:
    st.session_state.selected_state = ""
if "selected_district" not in st.session_state:
    st.session_state.selected_district = ""
if "selected_crop" not in st.session_state:
    st.session_state.selected_crop = ""

# Function to fetch 10-day forecast for selected district
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_10day_forecast(district):
    days = 10
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={district},India&days={days}"
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
                # Hindi condition mapping (simple)
                hindi_condition = condition  # Keep English or translate if needed
                weather_emoji = "☀️" if "sunny" in condition.lower() else "🌤️" if "cloudy" in condition.lower() else "🌧️" if "rain" in condition.lower() else "⛅"
                forecast_list.append({
                    "date": date,
                    "max_temp": max_temp,
                    "min_temp": min_temp,
                    "avg_temp": avg_temp,
                    "condition": hindi_condition,
                    "emoji": weather_emoji
                })
            return forecast_list
        else:
            return None
    except Exception as e:
        st.error(f"मौसम डेटा लाने में त्रुटि: {e}")
        return None

# Function to get pesticide suggestion (Hindi)
def get_pesticide_suggestion(crop):
    crop_lower = crop.lower().strip()
    if crop_lower in pesticide_suggestions:
        return pesticide_suggestions[crop_lower]
    else:
        return "इस फसल के लिए कोई विशिष्ट सुझाव उपलब्ध नहीं। स्थानीय विशेषज्ञ से परामर्श लें।"

# Function to display crop prices (National India-wide, Ludhiana crops focus)
def get_crop_prices_display(user_crop):
    if not crop_prices:
        return "मूल्य डेटा अभी उपलब्ध नहीं। agmarknet.nic.in पर नवीनतम जांचें।"
    
    # Build Hindi markdown table for national comparison
    table_lines = ["**भारत के वर्तमान मंडी मूल्य (₹ प्रति क्विंटल) - अपडेट: " + datetime.now().strftime("%Y-%m-%d") + "**",
                   "| फसल | मोडल मूल्य | न्यून-अधिकतम | अनुमानित आय/एकड़ (₹) |",
                   "|------|-------------|-------------|-----------------------|"]
    
    total_revenue_estimate = 0
    crop_lower = user_crop.lower().strip()
    for crop, data in crop_prices.items():
        modal = data["modal_price"]
        min_max = f"{data['min_price']}-{data['max_price']}"
        yield_q = data["avg_yield_quintal_per_acre"]
        revenue = modal * yield_q
        table_lines.append(f"| {crop.capitalize()} | {modal} | {min_max} | {revenue:,} |")
        
        if crop_lower == crop:
            total_revenue_estimate = revenue
    
    table = "\n".join(table_lines)
    
    # Hindi message
    msg = f"{table}\n\n**आपकी फसल ({user_crop}) के लिए:** एकड़ प्रति अनुमानित आय: ₹{total_revenue_estimate:,} (औसत उपज {crop_prices.get(crop_lower, {}).get('avg_yield_quintal_per_acre', 0)} क्विंटल/एकड़ पर आधारित)। अन्य फसलों से तुलना करें!\n\n*नोट: Agmarknet से राष्ट्रीय औसत (स्थिर नमूना—कोड अपडेट करें रीयल-टाइम के लिए)। वास्तविक लाभ = आय - लागत (बीज, श्रम आदि)। स्थानीय मंडी जांचें।*"
    
    return msg

# Main App Logic (Button-based steps)
if st.session_state.step == 0:
    st.header("🌍 अपना राज्य चुनें")
    selected_state = st.selectbox("राज्य:", list(states_districts.keys()))
    if st.button("राज्य चुनें 👆", key="select_state"):
        st.session_state.selected_state = selected_state
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 1:
    st.header(f"📍 {st.session_state.selected_state} में अपना जिला चुनें")
    districts = states_districts.get(st.session_state.selected_state, [])
    selected_district = st.selectbox("जिला:", districts)
    if st.button("जिला चुनें 👆", key="select_district"):
        st.session_state.selected_district = selected_district
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    st.header(f"🌤️ {st.session_state.selected_district} के लिए 10-दिन मौसम पूर्वानुमान")
    forecast_data = get_10day_forecast(st.session_state.selected_district)
    if forecast_data:
        st.markdown("**आज से शुरू 10-दिन मौसम पूर्वानुमान:**")
        for day in forecast_data:
            st.markdown(f"- **{day['date']}** {day['emoji']}: अधिकतम {day['max_temp']}°C / न्यूनतम {day['min_temp']}°C | औसत {day['avg_temp']:.1f}°C | {day['condition']}")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("गेहूं 🌾", key="crop_wheat"):
                st.session_state.selected_crop = "wheat"
                st.session_state.step = 3
                st.rerun()
        with col2:
            if st.button("चावल 🚀", key="crop_rice"):  # Emoji for rice
                st.session_state.selected_crop = "rice"
                st.session_state.step = 3
                st.rerun()
        with col3:
            if st.button("मक्का 🌽", key="crop_maize"):
                st.session_state.selected_crop = "maize"
                st.session_state.step = 3
                st.rerun()
        with col4:
            if st.button("कपास 🧵", key="crop_cotton"):
                st.session_state.selected_crop = "cotton"
                st.session_state.step = 3
                st.rerun()
        with col5:
            if st.button("गन्ना 🪴", key="crop_sugarcane"):
                st.session_state.selected_crop = "sugarcane"
                st.session_state.step = 3
                st.rerun()
    else:
        st.error("मौसम डेटा लाने में त्रुटि। पुनः प्रयास करें।")
        if st.button("वापस जिला चुनें ⬅️", key="back_district"):
            st.session_state.step = 1
            st.rerun()

elif st.session_state.step == 3:
    st.header(f"🌾 {st.session_state.selected_crop} के लिए कीटनाशक सुझाव (मौसम को ध्यान में रखते हुए)")
    pesticide = get_pesticide_suggestion(st.session_state.selected_crop)
    st.markdown(f"**{st.session_state.selected_crop} के लिए सुझाया कीटनाशक:**\n{pesticide}")
    st.markdown("*नोट: मौसम पूर्वानुमान हल्के हालात में स्प्रे की योजना सुझाता है। स्थानीय दिशानिर्देश और सुरक्षा निर्देशों का पालन करें।*")
    if st.button("मूल्य अपडेट देखें 💰", key="show_prices"):
        st.session_state.step = 4
        st.rerun()
    if st.button("नई बातचीत शुरू करें 🔄", key="reset"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.step = 0
        st.rerun()

elif st.session_state.step == 4:
    st.header("💰 फसल मूल्य अपडेट (लुधियाना क्षेत्र, भारत-व्यापी तुलना)")
    prices_msg = get_crop_prices_display(st.session_state.selected_crop)
    st.markdown(prices_msg)
    if st.button("नई बातचीत शुरू करें 🔄", key="reset_prices"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.step = 0
        st.rerun()

# Sidebar for info (Hindi)
with st.sidebar:
    st.markdown("### जानकारी")
    st.markdown("- **मौसम स्रोत:** WeatherAPI (10-दिन पूर्वानुमान)")
    st.markdown("- **समर्थित फसलें:** गेहूं, चावल, मक्का, कपास, गन्ना")
    st.markdown("- **मूल्य स्रोत:** Agmarknet (राष्ट्रीय औसत—कोड में अपडेट करें)")
    st.markdown("- **डिस्क्लेमर:** पूर्वानुमान/मूल्य अनुमानित; सुझाव सामान्य। विशेषज्ञों से परामर्श लें।")

# Footer (Hindi, with your email)
st.markdown("---")
st.markdown("*लुधियाना किसानों के लिए बनाया गया। प्रश्न? संपर्क [prabuddhsharma2020@gmail.com](mailto:prabuddhsharma2020@gmail.com). 🌾*")  # अपना ईमेल यहां डालें!

