import streamlit as st
import requests
from datetime import datetime

# --- Page Configuration (set this once at the top) ---
st.set_page_config(page_title="किसान सलाह", page_icon="🌱", layout="wide")

# --- IMPORTANT: API Key Management ---
# The code securely accesses your API key from Streamlit's secrets manager.
# You MUST create a file at .streamlit/secrets.toml and add your key there.
WEATHER_API_KEY = st.secrets.get("a471efb91f4c4e29ac9135831252209")

# --- Custom Styling (CSS) ---
def add_custom_css():
    st.markdown(f"""
    <style>
    /* General App Styling */
    .stApp {{
        background-image: url("https://images.pexels.com/photos/235922/pexels-photo-235922.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2");
        background-size: cover;
        background-attachment: fixed;
    }}

    /* Translucent Containers with Shadow */
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {{
        background: rgba(248, 249, 251, 0.85);
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-right: 1px solid rgba(0,0,0,0.1);
    }}
    .main .block-container {{
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(5px);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }}

    /* --- Landing Page Specific Styles --- */
    .landing-page-container {{
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("https://images.pexels.com/photos/3889855/pexels-photo-3889855.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"); /* NEW FARMER IMAGE */
        background-size: cover;
        background-position: center;
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        text-align: center;
        color: white;
    }}
    .landing-page-container h1 {{
        font-size: 4.5rem;
        font-weight: 900;
        text-shadow: 3px 3px 10px rgba(0,0,0,0.8);
    }}
    .landing-page-container .stButton button {{
        background-color: #28a745; /* A vibrant green */
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        padding: 1rem 2.5rem;
        border-radius: 50px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    .landing-page-container .stButton button:hover {{
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(0,0,0,0.5);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- Data Dictionaries ---
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
crops_list = ["wheat", "rice", "maize", "cotton", "sugarcane"]

# --- Helper Functions ---
@st.cache_data(ttl=1800)
def get_10day_forecast(hindi_district):
    if not WEATHER_API_KEY:
        st.error("Weather API key not configured. Please add it to your secrets file.")
        return None
    english_district = district_english_map.get(hindi_district, hindi_district)
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={english_district},India&days=10"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        forecast_list = []
        for day_data in data["forecast"]["forecastday"]:
            condition = day_data["day"]["condition"]["text"]
            emoji = "☀️" if "sunny" in condition.lower() else "🌤️" if "cloudy" in condition.lower() else "🌧️" if "rain" in condition.lower() else "⛅"
            forecast_list.append({
                "date": day_data["date"], "max_temp": day_data["day"]["maxtemp_c"],
                "min_temp": day_data["day"]["mintemp_c"], "condition": condition, "emoji": emoji
            })
        return forecast_list
    except requests.exceptions.RequestException as e:
        st.error(f"मौसम डेटा प्राप्त करने में विफल: {e}")
        return None

def get_crop_revenue(user_crop):
    crop_data = crop_prices.get(user_crop.lower().strip())
    return crop_data["modal_price"] * crop_data["avg_yield_quintal_per_acre"] if crop_data else 0

# --- UI Rendering Functions ---
def render_sidebar():
    with st.sidebar:
        st.title("🌱 किसान सलाह")
        st.markdown("---")
        service_map = {"🏠 होम": "home", "🌤️ मौसम पूर्वानुमान": "weather", "🛡️ कीटनाशक सलाह": "pesticide", "💰 मंडी मूल्य": "price", "💹 लाभ कैलकुलेटर": "profit"}
        service = st.radio("सेवा चुनें:", list(service_map.keys()))
        st.session_state.selected_service = service_map[service]
        st.markdown("---")
        if st.session_state.selected_service in ["weather", "pesticide"]:
            st.session_state.selected_state = st.selectbox("राज्य:", list(states_districts.keys()))
            if st.session_state.selected_state:
                st.session_state.selected_district = st.selectbox("जिला:", states_districts[st.session_state.selected_state])
        if st.session_state.selected_service in ["pesticide", "price", "profit"]:
             st.session_state.selected_crop = st.selectbox("फसल:", [c.capitalize() for c in crops_list])
        st.markdown("---")
        if st.button("↩️ होम पेज पर लौटें"):
            st.session_state.page = "landing"
            st.rerun()

def render_weather_page():
    st.header(f"🌤️ {st.session_state.get('selected_district', '...')} के लिए मौसम का पूर्वानुमान")
    if st.session_state.get('selected_district'):
        with st.spinner("मौसम डेटा लोड हो रहा है..."):
            forecast = get_10day_forecast(st.session_state.selected_district)
        if forecast:
            for day in forecast:
                st.markdown(f"- **{day['date']}**: {day['emoji']} {day['max_temp']}°C / {day['min_temp']}°C | {day['condition']}")
            st.success("10-दिन का पूर्वानुमान सफलतापूर्वक लोड हो गया।")

# Other render functions remain largely the same, but simplified for clarity
def render_home_page(): st.header("👋 आपका स्वागत है!"); st.info("कृपया बाईं ओर दिए गए मेनू से एक सेवा चुनें।")
def render_pesticide_page():
    st.header(f"🛡️ {st.session_state.get('selected_crop', '...')} के लिए कीटनाशक सलाह")
    if st.session_state.get('selected_crop'): st.markdown(pesticide_suggestions.get(st.session_state.selected_crop.lower(), "कोई सलाह उपलब्ध नहीं।"))
def render_price_page():
    st.header(f"💰 {st.session_state.get('selected_crop', '...')} के लिए मंडी मूल्य")
    if st.session_state.get('selected_crop'):
        crop_lower = st.session_state.selected_crop.lower()
        price_data = crop_prices.get(crop_lower)
        if price_data:
            revenue = price_data['modal_price'] * price_data['avg_yield_quintal_per_acre']
            col1, col2, col3 = st.columns(3)
            col1.metric("न्यूनतम मूल्य", f"₹{price_data['min_price']}", "प्रति क्विंटल")
            col2.metric("मोडल मूल्य", f"₹{price_data['modal_price']}", "प्रति क्विंटल")
            col3.metric("अधिकतम मूल्य", f"₹{price_data['max_price']}", "प्रति क्विंटल")
            st.metric("अनुमानित आय", f"₹{revenue:,}", "प्रति एकड़")
def render_profit_page():
    st.header(f"💹 {st.session_state.get('selected_crop', '...')} के लिए लाभ कैलक्यूलेटर")
    if st.session_state.get('selected_crop'):
        revenue = get_crop_revenue(st.session_state.selected_crop.lower())
        cost = st.number_input("खेती की कुल लागत दर्ज करें (₹ प्रति एकड़)", min_value=0, step=500)
        profit = revenue - cost
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("अनुमानित आय", f"₹{revenue:,}", "प्रति एकड़"); col2.metric("आपकी लागत", f"₹{cost:,}", "प्रति एकड़")
        col3.metric("शुद्ध लाभ/नुकसान", f"₹{profit:,}", "लाभ" if profit >= 0 else "नुकसान")

# --- Main App Logic with Page Routing ---
add_custom_css()
if "page" not in st.session_state: st.session_state.page = "landing"

if st.session_state.page == "landing":
    st.markdown('<div class="landing-page-container"><h1>किसान सलाह</h1><p>आपकी खेती, आपकी तरक्की</p></div>', unsafe_allow_html=True)
    if st.button("ऐप में प्रवेश करें", key="enter_app"):
        st.session_state.page = "main_app"; st.rerun()
else:
    st.title("कृषि सहायक सेवाएं"); st.markdown("---")
    render_sidebar()
    service_pages = {"home": render_home_page, "weather": render_weather_page, "pesticide": render_pesticide_page, "price": render_price_page, "profit": render_profit_page}
    service_pages.get(st.session_state.get("selected_service", "home"), render_home_page)()

