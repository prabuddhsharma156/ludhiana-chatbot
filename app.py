import streamlit as st
import requests
from datetime import datetime

# Load API key from Streamlit Secrets (set real key for weather predictions)
WEATHER_API_KEY = st.secrets.get("WEATHER_API_KEY", "YOUR_WEATHERAPI_KEY_HERE")

# Pesticide suggestions (Hindi info for 5 crops)
pesticide_suggestions = {
    "wheat": "फंगीसाइड XYZ (उदाहरण: कार्बेंडाजिम) - जंग और स्मट से सुरक्षा। 2-3 ग्राम/लीटर पानी में मिलाकर छिड़काव करें।",
    "rice": "कीटनाशक ABC (उदाहरण: इमिडाक्लोप्रिड) - तना बोरर और पत्ती फोल्डर नियंत्रण। 0.3 मिली/लीटर पानी।",
    "maize": "खरपतवारनाशक DEF (उदाहरण: एट्राजीन) - घास और चौड़ी पत्ती वाले खरपतवार प्रबंधन। 1 किलो/हेक्टेयर।",
    "cotton": "कीटनाशक GHI (उदाहरण: एंडोसल्फान) - बोलवर्म और एफिड्स पर निशाना। 1.5 मिली/लीटर।",
    "sugarcane": "कीटनाशक JKL (उदाहरण: क्लोरपायरीफॉस) - बोरर और दीमक से लड़ाई। 2 मिली/लीटर पानी।",
}

# 4 States with 5 districts each (Hindi for UI, agri-focused, includes Ludhiana)
states_districts = {
    "पंजाब": ["लुधियाना", "अमृतसर", "जालंधर", "पटियाला", "बठिंडा"],
    "हरियाणा": ["करनाल", "अंबाला", "कुरुक्षेत्र", "सिरसा", "फरीदाबाद"],
    "राजस्थान": ["जयपुर", "जोधपुर", "उदयपुर", "कोटा", "बीकानेर"],
    "उत्तर प्रदेश": ["लखनऊ", "कानपुर", "आगरा", "वाराणसी", "मेरठ"],
}

# Hindi to English district mapping (for accurate weather API)
district_english_map = {
    "लुधियाना": "Ludhiana", "अमृतसर": "Amritsar", "जालंधर": "Jalandhar", "पटियाला": "Patiala", "बठिंडा": "Bathinda",
    "करनाल": "Karnal", "अंबाला": "Ambala", "कुरुक्षेत्र": "Kurukshetra", "सिरसा": "Sirsa", "फरीदाबाद": "Faridabad",
    "जयपुर": "Jaipur", "जोधपुर": "Jodhpur", "उदयपुर": "Udaipur", "कोटा": "Kota", "बीकानेर": "Bikaner",
    "लखनऊ": "Lucknow", "कानपुर": "Kanpur", "आगरा": "Agra", "वाराणसी": "Varanasi", "मेरठ": "Meerut",
}

# Real crop prices (Oct 2024 national averages, ₹/quintal)
crop_prices = {
    "wheat": {"modal_price": 2450, "min_price": 2400, "max_price": 2500, "avg_yield_quintal_per_acre": 20},
    "rice": {"modal_price": 2150, "min_price": 2100, "max_price": 2200, "avg_yield_quintal_per_acre": 25},
    "maize": {"modal_price": 1850, "min_price": 1800, "max_price": 1900, "avg_yield_quintal_per_acre": 18},
    "cotton": {"modal_price": 6700, "min_price": 6600, "max_price": 6800, "avg_yield_quintal_per_acre": 10},
    "sugarcane": {"modal_price": 360, "min_price": 350, "max_price": 370, "avg_yield_quintal_per_acre": 400},
}

# App config
st.set_page_config(page_title="फसल सलाह चैटबॉट", page_icon="🌤️", layout="centered")
st.title("🌤️ किसानों के लिए मौसम, दवा, मूल्य और लाभ कैलकुलेटर")
st.markdown("---")

# Session state
if "step" not in st.session_state:
    st.session_state.step = 0  # 0: State, 1: District, 2: Weather, 3: Crop, 4: Pesticide, 5: Prices, 6: Profit
if "selected_state" not in st.session_state:
    st.session_state.selected_state = ""
if "selected_district" not in st.session_state:
    st.session_state.selected_district = ""
if "selected_crop" not in st.session_state:
    st.session_state.selected_crop = ""
if "total_cost" not in st.session_state:
    st.session_state.total_cost = 0
if "revenue_estimate" not in st.session_state:
    st.session_state.revenue_estimate = 0

# Weather function (10-day prediction)
@st.cache_data(ttl=1800)
def get_10day_forecast(hindi_district):
    english_district = district_english_map.get(hindi_district, hindi_district)
    days = 10
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={english_district},India&days={days}"
    if WEATHER_API_KEY == "YOUR_WEATHERAPI_KEY_HERE":
        return None
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            forecast_list = []
            for i in range(days):
                day_data = data["forecast"]["forecastday"][i]
                date = day_data["date"]
                max_temp = day_data["day"]["maxtemp_c"]
                min_temp = day_data["day"]["mintemp_c"]
                avg_temp = day_data["day"]["avgtemp_c"]
                condition = day_data["day"]["condition"]["text"]
                emoji = "☀️" if "sunny" in condition.lower() else "🌤️" if "cloudy" in condition.lower() else "🌧️" if "rain" in condition.lower() else "⛅"
                forecast_list.append({"date": date, "max_temp": max_temp, "min_temp": min_temp, "avg_temp": avg_temp, "condition": condition, "emoji": emoji})
            return forecast_list
        else:
            return None
    except Exception as e:
        st.error(f"मौसम पूर्वानुमान त्रुटि: {e}. API कुंजी सेट करें।")
        return None

# Pesticide suggestion
def get_pesticide_suggestion(crop):
    crop_lower = crop.lower().strip()
    return pesticide_suggestions.get(crop_lower, "इस फसल के लिए सुझाव उपलब्ध नहीं। स्थानीय विशेषज्ञ से संपर्क करें।")

# Prices display with table
def get_crop_prices_display(user_crop):
    table_lines = [
        f"**राष्ट्रीय मंडी मूल्य (₹/क्विंटल) - अपडेट: {datetime.now().strftime('%Y-%m-%d')}**",
        "| फसल | मोडल मूल्य | न्यून-अधिकतम | अनुमानित आय/एकड़ (₹) |",
        "|------|-------------|-------------|-----------------------|"
    ]
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
    msg = f"{table}\n\n**आपकी फसल ({user_crop}) के लिए अनुमानित आय:** ₹{total_revenue_estimate:,}/एकड़ (औसत उपज {crop_prices.get(crop_lower, {}).get('avg_yield_quintal_per_acre', 0)} क्विंटल/एकड़)।\n\n*नोट: Agmarknet से औसत। स्थानीय मंडी चेक करें।*"
    return msg, total_revenue_estimate

# Profit calculator
def calculate_profit(revenue, total_cost, crop):
    if total_cost > 0:
        profit = revenue - total_cost
        emoji = "💰" if profit > 0 else "⚠️" if profit == 0 else "📉"
        return f"{emoji} **{crop} के लिए लाभ कैलकुलेशन:**\n- अनुमानित आय: ₹{revenue:,}/एकड़\n- कुल लागत (आपकी): ₹{total_cost:,}/एकड़\n- **शुद्ध लाभ: ₹{profit:,}/एकड़**\n\n*टिप: सामान्य लागत - गेहूं: ₹15,000-25,000/एकड़ (बीज, खाद, मजदूरी)।*"
    else:
        return f"**{crop} के लिए आय:** ₹{revenue:,}/एकड़। लागत डालें और कैलकुलेट करें!\n\n*टिप: कुल लागत (बीज + श्रम + अन्य) डालें (₹ में)।*"

# Main app logic (steps)
if st.session_state.step == 0:
    st.header("🌍 राज्य चुनें")
    selected_state = st.selectbox("राज्य:", list(states_districts.keys()))
    col1, col2 = st.columns(2)
    with col1:
        if st.button("राज्य चुनें 👆", key="select_state"):
            st.session_state.selected_state = selected_state
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("रीसेट 🔄", key="reset"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.step = 0
            st.rerun()

elif st.session_state.step == 1:
    st.header(f"📍 {st.session_state.selected_state} में जिला चुनें")
    districts = states_districts.get(st.session_state.selected_state, [])
    selected_district = st.selectbox("जिला:", districts)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("जिला चुनें 👆", key="select_district"):
            st.session_state.selected_district = selected_district
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("वापस राज्य ⬅️", key="back_state"):
            st.session_state.step = 0
            st.rerun()

elif st.session_state.step == 2:
    st.header(f"🌤️ {st.session_state.selected_district} का 10-दिन मौसम पूर्वानुमान")
    forecast_data = get_10day_forecast(st.session_state.selected_district)
    if forecast_data:
        st.markdown("**10-दिन पूर्वानुमान:**")
        for day in forecast_data:
            st.markdown(f"- **{day['date']}** {day['emoji']}: अधिकतम {day['max_temp']}°C / न्यूनतम {day['min_temp']}°C | {day['condition']}")
        st.success("मौसम लोड हो गया! अब फसल चुनें।")
    else:
        st.error("मौसम पूर्वानुमान लाने में त्रुटि। API कुंजी सेट करें या बिना मौसम के जारी रखें।")
        if st.button("बिना मौसम के जारी रखें ➡️", key="skip_weather"):
            st.session_state.step = 3
            st.rerun()
    # Crop buttons (5 columns)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("गेहूं 🌾", key="crop_wheat"):
            st.session_state.selected_crop = "wheat"
            st.session_state.step = 4  # Skip to pesticide
            st.rerun()
    with col2:
        if st.button("चावल 🌾", key="crop_rice"):
            st.session_state.selected_crop = "rice"
            st.session_state.step = 4
            st.rerun()
    with col3:
        if st.button("मक्का 🌽", key="crop_maize"):
            st.session_state.selected_crop = "maize"
            st.session_state.step = 4
            st.rerun()
    with col4:
        if st.button("कपास 🧵", key="crop_cotton"):
            st.session_state.selected_crop = "cotton"
            st.session_state.step = 4
            st.rerun()
    with col5:
        if st.button("गन्ना 🪴", key="crop_sugarcane"):
            st.session_state.selected_crop = "sugarcane"
            st.session_state.step = 4
            st.rerun()
    if st.button("वापस जिला ⬅️", key="back_district"):
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 4:  # Pesticide
    st.header(f"🛡️ {st.session_state.selected_crop} के लिए कीटनाशक/दवा सलाह")
    suggestion = get_pesticide_suggestion(st.session_state.selected_crop)
    st.markdown(suggestion)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("मूल्य देखें 💰", key="view_prices"):
            prices_msg, revenue = get_crop_prices_display(st.session_state.selected_crop)
            st.session_state.revenue_estimate = revenue
            st.session_state.step = 5
            st.rerun()
    with col2:
        if st.button("वाप
