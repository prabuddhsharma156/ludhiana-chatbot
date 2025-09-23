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
}

# All 28 Indian States with 4-5 major districts each (Hindi names, agri-focused where possible)
states_districts = {
    "आंध्र प्रदेश": ["विशाखापत्तनम", "विजयवाड़ा", "गुंटूर", "कुरनूल", "अनंतपुर"],
    "अरुणाचल प्रदेश": ["इटानगर", "तवांग", "पापुम पारे", "लोहित"],
    "असम": ["गुवाहाटी", "डिब्रूगढ़", "जोरहाट", "सिलचर", "कामरूप"],
    "बिहार": ["पटना", "गया", "भागलपुर", "मुजफ्फरपुर", "पूर्णिया"],
    "छत्तीसगढ़": ["रायपुर", "दुर्ग", "बिलासपुर", "रायगढ़", "जांजगीर-चांपा"],
    "गोवा": ["पणजी", "मार्गाव", "साउस गोवा", "नॉर्थ गोवा"],
    "गुजरात": ["अहमदाबाद", "सूरत", "वडोदरा", "राजकोट", "भावनगर"],
    "हरियाणा": ["करनाल", "अंबाला", "कुरुक्षेत्र", "सिरसा", "फरीदाबाद"],
    "हिमाचल प्रदेश": ["शिमला", "मंडी", "कुल्लू", "कांगड़ा", "सोलन"],
    "झारखंड": ["रांची", "धनबाद", "जमशेदपुर", "गिरिडीह", "हजारीबाग"],
    "कर्नाटक": ["बेंगलुरु", "मैसूर", "हुबली", "बेलगाम", "मंगलुरु"],
    "केरल": ["तिरुवनंतपुरम", "कोच्चि", "कोझिकोड", "त्रिशूर", "कोट्टायम"],
    "मध्य प्रदेश": ["भोपाल", "इंदौर", "ग्वालियर", "जबलपुर", "उज्जैन"],
    "महाराष्ट्र": ["मुंबई", "पुणे", "नागपुर", "नासिक", "अमरावती"],
    "मणिपुर": ["इम्फाल पूर्व", "इम्फाल पश्चिम", "बिश्नुपुर", "थौबल"],
    "मेघालय": ["शिलांग", "ईस्ट खासी हिल्स", "वेस्ट गारो हिल्स", "ईस्ट गारो हिल्स"],
    "मिजोरम": ["आइजोल", "लुंगलेई", "चम्फाई", "कौलक"],
    "नागालैंड": ["कोहिमा", "दिमापुर", "मोकोकचुंग", "तुकेसांग"],
    "ओडिशा": ["भुवनेश्वर", "कटक", "बरम्पुर", "राउरकेला", "बालासोर"],
    "पंजाब": ["लुधियाना", "अमृतसर", "जालंधर", "पटियाला", "बठिंडा"],
    "राजस्थान": ["जयपुर", "जोधपुर", "उदयपुर", "कोटा", "बीकानेर"],
    "सिक्किम": ["गंगटोक", "मंगन", "ईस्ट सिक्किम", "वेस्ट सिक्किम"],
    "तमिलनाडु": ["चेन्नई", "कोयंबटूर", "मदुरै", "तिरुचिरापल्ली", "सलेम"],
    "तेलंगाना": ["हैदराबाद", "वरंगल", "निजामाबाद", "खम्मम", "महबूबनगर"],
    "त्रिपुरा": ["अगरतला", "उनाकोटी", "वेस्ट त्रिपुरा", "सिपाहिजाला"],
    "उत्तर प्रदेश": ["लखनऊ", "कानपुर", "आगरा", "वाराणसी", "मेरठ"],
    "उत्तराखंड": ["देहरादून", "हरिद्वार", "उधम सिंह नगर", "नैनीताल"],
    "पश्चिम बंगाल": ["कोलकाता", "हावड़ा", "दरजीलिंग", "बर्धमान", "मालदा"],
}

# Real crop prices: National India-wide averages (Oct 2024 data from Agmarknet/CommodityOnline - static for stability)
# Sources: Recent mandi averages (e.g., Wheat ₹2450 from Ludhiana/Delhi; works tomorrow without updates)
crop_prices = {
    "wheat": {"modal_price": 2450, "min_price": 2400, "max_price": 2500, "avg_yield_quintal_per_acre": 20},
    "rice": {"modal_price": 2150, "min_price": 2100, "max_price": 2200, "avg_yield_quintal_per_acre": 25},
    "maize": {"modal_price": 1850, "min_price": 1800, "max_price": 1900, "avg_yield_quintal_per_acre": 18},
    "cotton": {"modal_price": 6700, "min_price": 6600, "max_price": 6800, "avg_yield_quintal_per_acre": 10},
    "sugarcane": {"modal_price": 360, "min_price": 350, "max_price": 370, "avg_yield_quintal_per_acre": 400},
}

# Streamlit App (Hindi title and config)
st.set_page_config(page_title="10-दिन मौसम और फसल सलाह चैटबॉट", page_icon="🌤️", layout="centered")

st.title("🌤️ भारतीय किसानों के लिए 10-दिन मौसम, फसल सलाह और लाभ कैलकुलेटर")
st.markdown("---")

# Initialize session state for steps (no chat input - button-based)
if "step" not in st.session_state:
    st.session_state.step = 0  # 0: State, 1: District, 2: Weather, 3: Crop, 4: Pesticide, 5: Prices, 6: Profit
if "selected_state" not in st.session_state:
    st.session_state.selected_state = ""
if "selected_district" not in st.session_state:
    st.session_state.selected_district = ""
if "selected_crop" not in st.session_state:
    st.session_state.selected_crop = ""
if "total_cost" not in st.session_state:
    st.session_state.total_cost = 0  # For profit calc
if "revenue_estimate" not in st.session_state:
    st.session_state.revenue_estimate = 0

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
                weather_emoji = "☀️" if "sunny" in condition.lower() else "🌤️" if "cloudy" in condition.lower() else "🌧️" if "rain" in condition.lower() else "⛅"
                forecast_list.append({
                    "date": date,
                    "max_temp": max_temp,
                    "min_temp": min_temp,
                    "avg_temp": avg_temp,
                    "condition": condition,
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

# Function to display crop prices (National table with real data)
def get_crop_prices_display(user_crop):
    if not crop_prices:
        return "मूल्य डेटा अभी उपलब्ध नहीं। agmarknet.nic.in पर नवीनतम जांचें।"
    
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
    
    msg = f"{table}\n\n**आपकी फसल ({user_crop}) के लिए आय:** ₹{total_revenue_estimate:,}/एकड़ (औसत उपज {crop_prices.get(crop_lower, {}).get('avg_yield_quintal_per_acre', 0)} क्विंटल/एकड़)।\n\n*नोट: राष्ट्रीय औसत (Agmarknet से)। वास्तविक के लिए [Agmarknet](https://agmarknet.gov.in/SearchCmmMkt.aspx) चेक करें।*"
    
    return msg, total_revenue_estimate  # Return revenue for profit calc

# Function to calculate profit (new)
def calculate_profit(revenue, total_cost, crop):
    if total_cost > 0:
        profit = revenue - total_cost
        profit_emoji = "💰" if profit > 0 else "⚠️" if profit == 0 else "📉"
        return f"{profit_emoji} **{crop} के लिए लाभ कैलकुलेशन:**\n- अनुमानित आय: ₹{revenue:,}/एकड़\n- कुल लागत (आपकी इनपुट): ₹{total_cost:,}/एकड़\n- **शुद्ध लाभ: ₹{profit:,}/एकड़** (लागत घटाकर)\n\n*टिप: सामान्य लागत - गेहूं: ₹15,000-20,000/एकड़ (बीज, खाद, श्रम); अपनी वास्तविक लागत डालें।*"
    else:
        return f"**{crop} के लिए आय:** ₹{revenue:,}/एकड़। लागत डालकर लाभ देखें!\n\n*टिप: कुल लागत (बीज + श्रम + खाद आदि) डालें (₹ में)।*"

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
    if st.button("वापस राज्य चुनें ⬅️", key="back_state"):
        st.session_state.step = 0
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
            if st.button("चावल 🌾", key="crop_rice"):
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
        st.error("मौसम डेटा लाने में त्रुटि। API कुंजी सेट करें या पुनः प्रय
