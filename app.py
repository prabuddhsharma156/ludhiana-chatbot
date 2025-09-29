import streamlit as st
import requests
from datetime import datetime

WEATHER_API_KEY = st.secrets.get("WEATHER_API_KEY", "YOUR_WEATHERAPI_KEY_HERE")

pesticide_suggestions = {
    "wheat": "फंगीसाइड XYZ (उदाहरण: कार्बेंडाजिम) - जंग और स्मट से सुरक्षा। 2-3 ग्राम/लीटर पानी में मिलाकर छिड़काव करें। लागत: ₹200-300/एकड़।",
    "rice": "कीटनाशक ABC (उदाहरण: इमिडाक्लोप्रिड) - तना बोरर और पत्ती फोल्डर नियंत्रण। 0.3 मिली/लीटर पानी। लागत: ₹150-250/एकड़।",
    "maize": "खरपतवारनाशक DEF (उदाहरण: एट्राजीन) - घास और चौड़ी पत्ती वाले खरपतवार प्रबंधन। 1 किलो/हेक्टेयर। लागत: ₹300-400/एकड़।",
    "cotton": "कीटनाशक GHI (उदाहरण: एंडोसल्फान) - बोलवर्म और एफिड्स पर निशाना। 1.5 मिली/लीटर। लागत: ₹400-500/एकड़।",
    "sugarcane": "कीटनाशक JKL (उदाहरण: क्लोरपायरीफॉस) - बोरर और दीमक से लड़ाई। 2 मिली/लीटर पानी। लागत: ₹250-350/एकड़।",
}

states_districts = {
    "पंजाब": ["लुधियाना", "अमृतसर", "जालंधर", "पटियाला", "बठिंडा"],
    "हरियाणा": ["करनाल", "अंबाला", "कुरुक्षेत्र", "सिरसा", "फरीदाबाद"],
    "राजस्थान": ["जयपुर", "जोधपुर", "उदयपुर", "कोटा", "बीकानेर"],
    "उत्तर प्रदेश": ["लखनऊ", "कानपुर", "आगरा", "वाराणसी", "मेरठ"],
}

district_english_map = {
    "लुधियाना": "Ludhiana", "अमृतसर": "Amritsar", "जालंधर": "Jalandhar", "पटियाला": "Patiala", "बठिंडा": "Bathinda",
    "करनाल": "Karnal", "अंबाला": "Ambala", "कुरुक्षेत्र": "Kurukshetra", "सिरसा": "Sirsa", "फरीदाबाद": "Faridabad",
    "जयपुर": "Jaipur", "जोधपुर": "Jodhpur", "उदयपुर": "Udaipur", "कोटा": "Kota", "बीकानेर": "Bikaner",
    "लखनऊ": "Lucknow", "कानपुर": "Kanpur", "आगरा": "Agra", "वाराणसी": "Varanasi", "मेरठ": "Meerut",
}

crop_prices = {
    "wheat": {"modal_price": 2450, "min_price": 2400, "max_price": 2500, "avg_yield_quintal_per_acre": 20},
    "rice": {"modal_price": 2150, "min_price": 2100, "max_price": 2200, "avg_yield_quintal_per_acre": 25},
    "maize": {"modal_price": 1850, "min_price": 1800, "max_price": 1900, "avg_yield_quintal_per_acre": 18},
    "cotton": {"modal_price": 6700, "min_price": 6600, "max_price": 6800, "avg_yield_quintal_per_acre": 10},
    "sugarcane": {"modal_price": 360, "min_price": 350, "max_price": 370, "avg_yield_quintal_per_acre": 400},
}

st.set_page_config(page_title="फसल सलाह चैटबॉट", page_icon="🌤️", layout="centered")
st.title("🌤️ किसानों के लिए सलाह सेवाएं")
st.markdown("---")

if "step" not in st.session_state:
    st.session_state.step = 0
if "selected_service" not in st.session_state:
    st.session_state.selected_service = ""
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
                condition = day_data["day"]["condition"]["text"]
                emoji = "☀️" if "sunny" in condition.lower() else "🌤️" if "cloudy" in condition.lower() else "🌧️" if "rain" in condition.lower() else "⛅"
                forecast_list.append({"date": date, "max_temp": max_temp, "min_temp": min_temp, "condition": condition, "emoji": emoji})
            return forecast_list
        else:
            return None
    except Exception as e:
        st.error(f"मौसम त्रुटि: {e}. API कुंजी सेट करें।")
        return None

def get_pesticide_suggestion(crop):
    crop_lower = crop.lower().strip()
    return pesticide_suggestions.get(crop_lower, "सलाह उपलब्ध नहीं। विशेषज्ञ से पूछें।")

def get_crop_prices_display(user_crop):
    table_lines = [
        f"**मंडी मूल्य (₹/क्विंटल) - {datetime.now().strftime('%Y-%m-%d')}**",
        "| फसल | मोडल | रेंज | आय/एकड़ |",
        "|------|------|------|---------|"
    ]
    revenue = 0
    crop_lower = user_crop.lower().strip()
    for crop, data in crop_prices.items():
        modal = data["modal_price"]
        min_max = f"{data['min_price']}-{data['max_price']}"
        yield_q = data["avg_yield_quintal_per_acre"]
        rev = modal * yield_q
        table_lines.append(f"| {crop.capitalize()} | {modal} | {min_max} | {rev:,} |")
        if crop_lower == crop:
            revenue = rev
    table = "\n".join(table_lines)
    msg = f"{table}\n\n**{user_crop} आय:** ₹{revenue:,}/एकड़ (उपज: {crop_prices.get(crop_lower, {}).get('avg_yield_quintal_per_acre', 0)} क्विंटल)। *Agmarknet से।*"
    return msg, revenue

def calculate_profit(revenue, cost, crop):
    if cost > 0:
        profit = revenue - cost
        emoji = "💰" if profit > 0 else "⚠️"
        return f"{emoji} **{crop} लाभ:**\n- आय: ₹{revenue:,}\n- लागत: ₹{cost:,}\n- **लाभ: ₹{profit:,}/एकड़**\n*टिप: लागत में बीज, खाद, मजदूरी शामिल करें।*"
    return f"**{crop} आय:** ₹{revenue:,}/एकड़। लागत डालें।"

if st.session_state.step == 0:
    st.header("कृपया सेवा चुनें")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("मौसम पूर्वानुमान 🌤️"):
            st.session_state.selected_service = "weather"
            st.session_state.step = 1
            st.rerun()
        if st.button("कीटनाशक सलाह 🛡️"):
            st.session_state.selected_service = "pesticide"
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("मंडी मूल्य 💰"):
            st.session_state.selected_service = "price"
            st.session_state.step = 3
            st.rerun()
        if st.button("लाभ कैलकुलेटर 💹"):
            st.session_state.selected_service = "profit"
            st.session_state.step = 3
            st.rerun()
    if st.button("रीसेट 🔄"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.session_state.step = 0
        st.rerun()

elif st.session_state.step == 1:
    st.header("🌍 राज्य चुनें (स्थान-आधारित सेवा के लिए)")
    state = st.selectbox("राज्य:", list(states_districts.keys()))
    col1, col2 = st.columns(2)
    with col1:
        if st.button("चुनें 👆"):
            st.session_state.selected_state = state
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("वापस सेवाएं ⬅️"):
            st.session_state.step = 0
            st.rerun()

elif st.session_state.step == 2:
    st.header(f"📍 {st.session_state.selected_state} में जिला चुनें")
    district = st.selectbox("जिला:", states_districts[st.session_state.selected_state])
    col1, col2 = st.columns(2)
    with col1:
        if st.button("चुनें 👆"):
            st.session_state.selected_district = district
            if st.session_state.selected_service == "weather":
                st.session_state.step = 4
            elif st.session_state.selected_service == "pesticide":
                st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("वापस राज्य ⬅️"):
            st.session_state.step = 1
            st.rerun()

elif st.session_state.step == 3:
    st.header("🌾 फसल चुनें")
    cols = st.columns(5)
    crops = ["wheat", "rice", "maize", "cotton", "sugarcane"]
    crop_names = ["गेहूं 🌾", "चावल 🌾", "मक्का 🌽", "कपास 🧵", "गन्ना 🪴"]
    for i, (crop, name) in enumerate(zip(crops, crop_names)):
        with cols[i]:
            if st.button(name, key=f"crop_{crop}"):
                st.session_state.selected_crop = crop
                if st.session_state.selected_service == "pesticide":
                    st.session_state.step = 5
                elif st.session_state.selected_service == "price":
                    st.session_state.step = 6
                elif st.session_state.selected_service == "profit":
                    st.session_state.step = 7
                st.rerun()
    if st.button("वापस ⬅️"):
        if st.session_state.selected_service in ["weather", "pesticide"]:
            st.session_state.step = 2
        else:
            st.session_state.step = 0
        st.rerun()

elif st.session_state.step == 4:
    st.header(f"🌤️ {st.session_state.selected_district} का 10-दिन मौसम पूर्वानुमान")
    forecast = get_10day_forecast(st.session_state.selected_district)
    if forecast:
        for day in forecast:
            st.markdown(f"- **{day['date']}** {day['emoji']}: {day['max_temp']}°C / {day['min_temp']}°C | {day['condition']}")
        st.success("मौसम पूर्वानुमान लोड हो गया!")
    else:
        st.error("मौसम डेटा उपलब्ध नहीं। API कुंजी सेट करें।")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("वापस जिला ⬅️"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("रीसेट 🔄"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state.step = 0
            st.rerun()

elif st.session_state.step == 5:
    st.header(f"🛡️ {st.session_state.selected_crop} के लिए कीटनाशक सलाह")
    st.markdown(get_pesticide_suggestion(st.session_state.selected_crop))
    col1, col2 = st.columns(2)
    with col1:
        if st.button("वापस फसल ⬅️"):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("रीसेट 🔄"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state.step = 0
            st.rerun()

elif st.session_state.step == 6:
    st.header(f"💰 {st.session_state.selected_crop} के लिए मंडी मूल्य")
    msg, rev = get_crop_prices_display(st.session_state.selected_crop)
    st.markdown(msg)
    st.session_state.revenue_estimate = rev
    col1, col2 = st.columns(2)
    with col1:
        if st.button("वापस फसल ⬅️"):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("रीसेट 🔄"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state.step = 0
            st.rerun()

elif st.session_state.step == 7:
    st.header(f"💹 {st.session_state.selected_crop} लाभ कैलकुलेटर")
    if st.session_state.revenue_estimate == 0:
        _, st.session_state.revenue_estimate = get_crop_prices_display(st.session_state.selected_crop)
    cost = st.number_input("कुल लागत (₹/एकड़):", min_value=0.0, value=0.0, step=1000.0)
    st.session_state.total_cost = cost
    if st.button("कैलकुलेट करें"):
        profit_msg = calculate_profit(st.session_state.revenue_estimate, cost, st.session_state.selected_crop)
        st.markdown(profit_msg)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("वापस फसल ⬅️"):
            st.session
