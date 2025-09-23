import streamlit as st
import requests
from datetime import datetime

# Load API key from Streamlit Secrets (MUST SET REAL KEY for weather to work)
WEATHER_API_KEY = st.secrets.get("WEATHER_API_KEY", "YOUR_WEATHERAPI_KEY_HERE")

# Crop to pesticide mapping (Hindi descriptions)
pesticide_suggestions = {
    "wheat": "फंगीसाइड XYZ (उदाहरण: कार्बेंडाजिम) - जंग और स्मट से सुरक्षा।",
    "rice": "कीटनाशक ABC (उदाहरण: इमिडाक्लोप्रिड) - तना बोरर और पत्ती फोल्डर नियंत्रण।",
    "maize": "खरपतवारनाशक DEF (उदाहरण: एट्राजीन) - घास और चौड़ी पत्ती वाले खरपतवार प्रबंधन।",
    "cotton": "कीटनाशक GHI (उदाहरण: एंडोसल्फान) - बोलवर्म और एफिड्स पर निशाना।",
    "sugarcane": "कीटनाशक JKL (उदाहरण: क्लोरपायरीफॉस) - बोरर और दीमक से लड़ाई।",
}

# All 28 Indian States with 4-5 major districts (Hindi for UI)
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

# Hindi District to English City Mapping (for Weather API - fixes wrong weather)
district_english_map = {
    # Punjab
    "लुधियाना": "Ludhiana",
    "अमृतसर": "Amritsar",
    "जालंधर": "Jalandhar",
    "पटियाला": "Patiala",
    "बठिंडा": "Bathinda",
    # Haryana
    "करनाल": "Karnal",
    "अंबाला": "Ambala",
    "कुरुक्षेत्र": "Kurukshetra",
    "सिरसा": "Sirsa",
    "फरीदाबाद": "Faridabad",
    # Uttar Pradesh
    "लखनऊ": "Lucknow",
    "कानपुर": "Kanpur",
    "आगरा": "Agra",
    "वाराणसी": "Varanasi",
    "मेरठ": "Meerut",
    # Maharashtra
    "मुंबई": "Mumbai",
    "पुणे": "Pune",
    "नागपुर": "Nagpur",
    "नासिक": "Nashik",
    "अमरावती": "Amravati",
    # Rajasthan
    "जयपुर": "Jaipur",
    "जोधपुर": "Jodhpur",
    "उदयपुर": "Udaipur",
    "कोटा": "Kota",
    "बीकानेर": "Bikaner",
    # Madhya Pradesh
    "भोपाल": "Bhopal",
    "इंदौर": "Indore",
    "ग्वालियर": "Gwalior",
    "जबलपुर": "Jabalpur",
    "उज्जैन": "Ujjain",
    # Gujarat
    "अहमदाबाद": "Ahmedabad",
    "सूरत": "Surat",
    "वडोदरा": "Vadodara",
    "राजकोट": "Rajkot",
    "भावनगर": "Bhavnagar",
    # Bihar
    "पटना": "Patna",
    "गया": "Gaya",
    "भागलपुर": "Bhagalpur",
    "मुजफ्फरपुर": "Muzaffarpur",
    "पूर्णिया": "Purnia",
    # Andhra Pradesh
    "विशाखापत्तनम": "Visakhapatnam",
    "विजयवाड़ा": "Vijayawada",
    "गुंटूर": "Guntur",
    "कुरनूल": "Kurnool",
    "अनंतपुर": "Anantapur",
    # Karnataka
    "बेंगलुरु": "Bengaluru",
    "मैसूर": "Mysore",
    "हुबली": "Hubli",
    "बेलगाम": "Belgaum",
    "मंगलुरु": "Mangalore",
    # Tamil Nadu
    "चेन्नई": "Chennai",
    "कोयंबटूर": "Coimbatore",
    "मदुरै": "Madurai",
    "तिरुचिरापल्ली": "Tiruchirappalli",
    "सलेम": "Salem",
    # Telangana
    "हैदराबाद": "Hyderabad",
    "वरंगल": "Warangal",
    "निजामाबाद": "Nizamabad",
    "खम्मम": "Khammam",
    "महबूबनगर": "Mahbubnagar",
    # Add more as needed for other states (e.g., "कोलकाता": "Kolkata")
    "कोलकाता": "Kolkata",
    "देहरादून": "Dehradun",
    "शिमला": "Shimla",
    "रांची": "Ranchi",
    "भुवनेश्वर": "Bhubaneswar",
    # ... (extend for all if needed; fallback to Hindi if not mapped)
}

# Real crop prices (Oct 2024 national averages - static)
crop_prices = {
    "wheat": {"modal_price": 2450, "min_price": 2400, "max_price": 2500, "avg_yield_quintal_per_acre": 20},
    "rice": {"modal_price": 2150, "min_price": 2100, "max_price": 2200, "avg_yield_quintal_per_acre": 25},
    "maize": {"modal_price": 1850, "min_price": 1800, "max_price": 1900, "avg_yield_quintal_per_acre": 18},
    "cotton": {"modal_price": 6700, "min_price": 6600, "max_price": 6800, "avg_yield_quintal_per_acre": 10},
    "sugarcane": {"modal_price": 360, "min_price": 350, "max_price": 370, "avg_yield_quintal_per_acre": 400},
}

st.set_page_config(page_title="फसल सलाह चैटबॉट", page_icon="🌤️", layout="centered")
st.title("🌤️ भारतीय किसानों के लिए मौसम, सलाह और लाभ कैलकुलेटर")
st.markdown("---")

# Session state
if "step" not in st.session_state:
    st.session_state.step = 0
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

# Weather fetch function (with English mapping)
@st.cache_data(ttl=1800)
def get_10day_forecast(hindi_district):
    english_district = district_english_map.get(hindi_district, hindi_district)  # Map to English
    days = 10
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={english_district},India&days={days}"
    if WEATHER_API_KEY == "YOUR_WEATHERAPI_KEY_HERE":
        return None  # Force error if key not set
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
            st.error(f"API त्रुटि: {response.status_code}. कुंजी चेक करें।")
            return None
    except Exception as e:
        st.error(f"मौसम डेटा त्रुटि: {e}. API कुंजी सेट करें।")
        return None

# Pesticide suggestion
def get_pesticide_suggestion(crop):
    crop_lower = crop.lower().strip()
    return pesticide_suggestions.get(crop_lower, "विशिष्ट सुझाव उपलब्ध नहीं। विशेषज्ञ से पूछें।")

# Prices display
def get_crop_prices_display(user_crop):
    crop_lower = user_crop.lower().strip()
    data = crop_prices.get(crop_lower, {})
    modal = data.get("modal_price", 0)
    yield_q = data.get("avg_yield_quintal_per_acre", 0)
    revenue = modal * yield_q
    table = f"**मंडी मूल्य (₹/क्विंटल, Oct 2024):** | फसल | मोडल | रेंज | आय/एकड़ |\n|------|------|------|----------|\n
