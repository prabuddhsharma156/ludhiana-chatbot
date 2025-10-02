<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>किसान सहायक অ্যাপ</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Poppins', sans-serif;
        }
        .page {
            display: none;
        }
        .page.active {
            display: block;
        }
        /* Custom scrollbar for weather forecast */
        .weather-container::-webkit-scrollbar {
            width: 8px;
        }
        .weather-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        .weather-container::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 10px;
        }
        .weather-container::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    </style>
</head>
<body class="bg-gray-100">

    <!-- Landing Page -->
    <div id="landing-page" class="page active h-screen w-screen bg-cover bg-center" style="background-image: url('https://images.pexels.com/photos/159516/farmer-on-his-tractor-in-his-field-in-spring-plowing-his-field-agriculture-159516.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1');">
        <!-- Overlay -->
        <div class="h-full w-full bg-black bg-opacity-50 flex flex-col justify-center items-center">
            <h1 class="text-white text-4xl md:text-6xl font-bold mb-4 text-center animate-pulse">किसान सहायक</h1>
            <p class="text-white text-lg md:text-2xl mb-8 text-center">আপনার বিশ্বস্ত কৃষি সঙ্গী</p>
            <button onclick="showPage('menu-page')" class="bg-green-600 text-white text-xl font-bold py-4 px-8 rounded-lg shadow-lg hover:bg-green-700 transition-transform transform hover:scale-105">
                অ্যাপে প্রবেশ করুন
            </button>
        </div>
    </div>

    <!-- Menu Page -->
    <div id="menu-page" class="page p-4 md:p-8 min-h-screen flex flex-col justify-center items-center bg-green-50">
        <h2 class="text-3xl md:text-4xl font-bold text-gray-800 mb-8 text-center">मुख्य मेनू</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl">
            <button onclick="showPage('weather-page')" class="bg-blue-500 text-white p-6 rounded-lg shadow-md hover:bg-blue-600 transition-transform transform hover:scale-105">
                <h3 class="text-2xl font-semibold">मौसम की जानकारी</h3>
                <p class="mt-2">अगले 10 दिनों का पूर्वानुमान देखें</p>
            </button>
            <button onclick="showPage('pesticide-page')" class="bg-yellow-500 text-white p-6 rounded-lg shadow-md hover:bg-yellow-600 transition-transform transform hover:scale-105">
                <h3 class="text-2xl font-semibold">कीटनाशक जानकारी</h3>
                <p class="mt-2">फसलों के लिए सही कीटनाशक चुनें</p>
            </button>
            <button onclick="showPage('profit-page')" class="bg-green-500 text-white p-6 rounded-lg shadow-md hover:bg-green-600 transition-transform transform hover:scale-105">
                <h3 class="text-2xl font-semibold">लाभ गणना</h3>
                <p class="mt-2">अपनी फसल का मुनाफा जानें</p>
            </button>
             <button onclick="showPage('landing-page')" class="bg-gray-500 text-white p-6 rounded-lg shadow-md hover:bg-gray-600 transition-transform transform hover:scale-105">
                <h3 class="text-2xl font-semibold">बाहर निकलें</h3>
                <p class="mt-2">ऐप से बाहर जाने के लिए</p>
            </button>
        </div>
    </div>

    <!-- Weather Page -->
    <div id="weather-page" class="page p-4 md:p-8 min-h-screen bg-blue-50">
        <div class="max-w-4xl mx-auto">
            <button onclick="showPage('menu-page')" class="bg-gray-500 text-white py-2 px-4 rounded-lg hover:bg-gray-600 mb-6">&larr; मुख्य मेनू पर वापस जाएं</button>
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h2 class="text-3xl font-bold text-gray-800 mb-6 text-center">मौसम की जानकारी</h2>
                
                <div class="mb-4">
                    <label for="state-select" class="block text-lg font-medium text-gray-700 mb-2">1. राज्य चुनें:</label>
                    <select id="state-select" class="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500">
                        <option value="">-- राज्य का चयन करें --</option>
                    </select>
                </div>

                <div id="district-selection" class="mb-6 hidden">
                    <label for="district-select" class="block text-lg font-medium text-gray-700 mb-2">2. जिला चुनें:</label>
                    <select id="district-select" class="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500">
                        <option value="">-- जिले का चयन करें --</option>
                    </select>
                </div>

                <div id="weather-result" class="mt-6"></div>
            </div>
        </div>
    </div>

    <!-- Pesticide Page -->
    <div id="pesticide-page" class="page p-4 md:p-8 min-h-screen bg-yellow-50">
        <div class="max-w-4xl mx-auto">
            <button onclick="showPage('menu-page')" class="bg-gray-500 text-white py-2 px-4 rounded-lg hover:bg-gray-600 mb-6">&larr; मुख्य मेनू पर वापस जाएं</button>
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h2 class="text-3xl font-bold text-gray-800 mb-6 text-center">कीटनाशक जानकारी</h2>
                <p class="text-center text-gray-600 mb-6">जानकारी देखने के लिए अपनी फसल चुनें:</p>
                <div id="crop-buttons" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                    <!-- Crop buttons will be inserted here by JavaScript -->
                </div>
                <div id="pesticide-info" class="mt-6 p-4 border border-gray-200 rounded-lg bg-gray-50 hidden"></div>
            </div>
        </div>
    </div>

    <!-- Profit Page -->
    <div id="profit-page" class="page p-4 md:p-8 min-h-screen bg-green-50">
         <div class="max-w-4xl mx-auto">
            <button onclick="showPage('menu-page')" class="bg-gray-500 text-white py-2 px-4 rounded-lg hover:bg-gray-600 mb-6">&larr; मुख्य मेनू पर वापस जाएं</button>
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h2 class="text-3xl font-bold text-gray-800 mb-6 text-center">लाभ गणना</h2>
                
                <div class="mb-4">
                    <label for="crop-profit-select" class="block text-lg font-medium text-gray-700 mb-2">फसल चुनें:</label>
                    <select id="crop-profit-select" class="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-green-500 focus:border-green-500">
                         <!-- Options will be populated by JS -->
                    </select>
                </div>
                
                <div class="mb-4">
                    <label for="cost-input" class="block text-lg font-medium text-gray-700 mb-2">कुल लागत दर्ज करें (प्रति एकड़):</label>
                    <input type="number" id="cost-input" placeholder="उदाहरण: 15000" class="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-green-500 focus:border-green-500">
                </div>

                <button onclick="calculateProfit()" class="w-full bg-green-600 text-white text-lg font-bold py-3 px-6 rounded-lg shadow-md hover:bg-green-700 transition-transform transform hover:scale-105">
                    लाभ की गणना करें
                </button>

                <div id="profit-result" class="mt-6 hidden text-center p-4 border border-green-200 rounded-lg bg-green-100"></div>
            </div>
        </div>
    </div>

    <script>
        // --- CONFIGURATION ---
        // IMPORTANT: Replace "YOUR_API_KEY" with your actual OpenWeatherMap API key.
        const WEATHER_API_KEY = "YOUR_API_KEY"; 

        const locations = {
            "उत्तर प्रदेश": ["लखनऊ", "कानपुर", "वाराणसी", "आगरा", "मेरठ"],
            "पंजाब": ["लुधियाना", "अमृतसर", "जालंधर", "पटियाला", "बठिंडा"],
            "हरियाणा": ["गुड़गांव", "फरीदाबाद", "पानीपत", "सोनीपत", "हिसार"],
            "राजस्थान": ["जयपुर", "जोधपुर", "उदयपुर", "कोटा", "बीकानेर"],
            "मध्य प्रदेश": ["भोपाल", "इंदौर", "ग्वालियर", "जबलपुर", "उज्जैन"],
        };

        const crops = {
            "चावल": {
                info: "धान के लिए, ट्राइसायक्लाजोल (Tricyclazole) का उपयोग ब्लास्ट रोग के नियंत्रण के लिए किया जाता है। ब्राउन प्लांट हॉपर के लिए इमिडाक्लोप्रिड (Imidacloprid) प्रभावी है। उपयोग से पहले विशेषज्ञ से सलाह अवश्य लें।",
                mandi_price: 2000 // प्रति क्विंटल
            },
            "गेहूँ": {
                info: "गेहूँ में दीमक के लिए क्लोरपायरीफॉस (Chlorpyrifos) का प्रयोग करें। खरपतवार नियंत्रण के लिए सल्फोसल्फ्यूरॉन (Sulfosulfuron) या 2,4-D का छिड़काव करें। हमेशा लेबल पर दिए गए निर्देशों का पालन करें।",
                mandi_price: 2200 // प्रति क्विंटल
            },
            "मक्का": {
                info: "मक्का में फॉल आर्मीवर्म के लिए इमामेक्टिन बेंजोएट (Emamectin Benzoate) का छिड़काव करें। तना छेदक के लिए कार्बोफ्यूरान (Carbofuran) का उपयोग किया जा सकता है। खुराक के लिए कृषि विशेषज्ञ से परामर्श करें।",
                mandi_price: 1800 // प्रति क्विंटल
            },
            "कपास": {
                info: "कपास में गुलाबी सुंडी (Pink Bollworm) के लिए फेनप्रोपेथ्रिन (Fenpropathrin) का उपयोग करें। सफेद मक्खी के लिए डायफेन्थियुरॉन (Diafenthiuron) का छिड़काव फायदेमंद है। सही समय और मात्रा का ध्यान रखें।",
                mandi_price: 6500 // प्रति क्विंटल
            },
            "गन्ना": {
                info: "गन्ने में अगेती तना छेदक के लिए फिप्रोनिल (Fipronil) का प्रयोग करें। पाइरिला कीट के नियंत्रण के लिए क्लोरपायरीफॉस (Chlorpyrifos) का छिड़काव करें। सुरक्षा उपकरणों का उपयोग अवश्य करें।",
                mandi_price: 350 // प्रति क्विंटल
            },
        };

        // --- PAGE NAVIGATION ---
        function showPage(pageId) {
            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            document.getElementById(pageId).classList.add('active');
        }

        // --- WEATHER LOGIC ---
        const stateSelect = document.getElementById('state-select');
        const districtSelect = document.getElementById('district-select');
        const districtSelectionDiv = document.getElementById('district-selection');
        const weatherResultDiv = document.getElementById('weather-result');

        // Populate states
        Object.keys(locations).forEach(state => {
            const option = document.createElement('option');
            option.value = state;
            option.textContent = state;
            stateSelect.appendChild(option);
        });

        // Handle state change
        stateSelect.addEventListener('change', () => {
            const selectedState = stateSelect.value;
            districtSelect.innerHTML = '<option value="">-- जिले का चयन करें --</option>'; // Reset districts
            weatherResultDiv.innerHTML = '';

            if (selectedState) {
                districtSelectionDiv.classList.remove('hidden');
                locations[selectedState].forEach(district => {
                    const option = document.createElement('option');
                    option.value = district;
                    option.textContent = district;
                    districtSelect.appendChild(option);
                });
            } else {
                districtSelectionDiv.classList.add('hidden');
            }
        });

        // Handle district change (fetch weather)
        districtSelect.addEventListener('change', () => {
            const selectedDistrict = districtSelect.value;
            if (selectedDistrict) {
                fetchWeather(selectedDistrict);
            }
        });

        async function fetchWeather(district) {
            if (WEATHER_API_KEY === "YOUR_API_KEY") {
                weatherResultDiv.innerHTML = `<div class="text-red-600 bg-red-100 p-4 rounded-lg">त्रुटि: कृपया डेवलपर से संपर्क करें और वैध मौसम API कुंजी प्रदान करें।</div>`;
                return;
            }
            
            weatherResultDiv.innerHTML = `<div class="text-center p-4">मौसम का डेटा लोड हो रहा है...</div>`;
            const url = `https://api.openweathermap.org/data/2.5/forecast/daily?q=${district}&cnt=10&appid=${WEATHER_API_KEY}&units=metric&lang=hi`;

            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`API से त्रुटि: ${response.statusText}`);
                }
                const data = await response.json();
                displayWeather(data);
            } catch (error) {
                console.error("Weather fetch error:", error);
                weatherResultDiv.innerHTML = `<div class="text-red-600 bg-red-100 p-4 rounded-lg">मौसम का डेटा प्राप्त करने में विफल। कृपया अपनी इंटरनेट कनेक्टिविटी जांचें या बाद में प्रयास करें।</div>`;
            }
        }

        function displayWeather(data) {
            if (!data || !data.list) {
                weatherResultDiv.innerHTML = `<div class="text-red-600 bg-red-100 p-4 rounded-lg">मौसम का डेटा उपलब्ध नहीं है।</div>`;
                return;
            }

            let html = `<h3 class="text-2xl font-bold text-gray-700 mb-4 text-center">${data.city.name} - अगले 10 दिन</h3>
                        <div class="weather-container overflow-x-auto pb-4">
                            <div class="flex space-x-4">`;

            data.list.forEach(day => {
                const date = new Date(day.dt * 1000);
                const dayName = date.toLocaleDateString('hi-IN', { weekday: 'short' });
                const fullDate = date.toLocaleDateString('hi-IN', { day: 'numeric', month: 'short' });
                const iconUrl = `https://openweathermap.org/img/wn/${day.weather[0].icon}@2x.png`;

                html += `
                    <div class="flex-shrink-0 w-36 text-center bg-blue-100 p-4 rounded-lg shadow">
                        <p class="font-semibold text-blue-800">${dayName}, ${fullDate}</p>
                        <img src="${iconUrl}" alt="${day.weather[0].description}" class="mx-auto w-16 h-16">
                        <p class="text-lg font-bold text-gray-800">${Math.round(day.temp.day)}°C</p>
                        <p class="text-sm text-gray-600 capitalize">${day.weather[0].description}</p>
                        <p class="text-xs text-gray-500 mt-2">💧 ${day.humidity}%</p>
                    </div>
                `;
            });

            html += `</div></div>`;
            weatherResultDiv.innerHTML = html;
        }


        // --- PESTICIDE LOGIC ---
        const cropButtonsDiv = document.getElementById('crop-buttons');
        const pesticideInfoDiv = document.getElementById('pesticide-info');

        Object.keys(crops).forEach(cropName => {
            const button = document.createElement('button');
            button.className = 'bg-yellow-400 text-gray-800 p-4 rounded-lg shadow-md hover:bg-yellow-500 font-semibold transition-transform transform hover:scale-105';
            button.textContent = cropName;
            button.onclick = () => showPesticideInfo(cropName);
            cropButtonsDiv.appendChild(button);
        });

        function showPesticideInfo(cropName) {
            pesticideInfoDiv.classList.remove('hidden');
            pesticideInfoDiv.innerHTML = `
                <h4 class="text-xl font-bold text-gray-800 mb-2">${cropName}</h4>
                <p class="text-gray-700">${crops[cropName].info}</p>
            `;
        }

        // --- PROFIT LOGIC ---
        const cropProfitSelect = document.getElementById('crop-profit-select');
        const costInput = document.getElementById('cost-input');
        const profitResultDiv = document.getElementById('profit-result');

        // Populate crop dropdown for profit calculation
        Object.keys(crops).forEach(cropName => {
            const option = document.createElement('option');
            option.value = cropName;
            option.textContent = cropName;
            cropProfitSelect.appendChild(option);
        });

        function calculateProfit() {
            const selectedCrop = cropProfitSelect.value;
            const cost = parseFloat(costInput.value);

            if (!selectedCrop || isNaN(cost) || cost <= 0) {
                profitResultDiv.innerHTML = `<p class="font-semibold text-red-700">कृपया मान्य फसल और लागत दर्ज करें।</p>`;
                profitResultDiv.classList.remove('hidden');
                profitResultDiv.classList.remove('border-green-200', 'bg-green-100');
                profitResultDiv.classList.add('border-red-200', 'bg-red-100');
                return;
            }

            const mandiPrice = crops[selectedCrop].mandi_price;
            // Assuming an average yield per acre for calculation (this is a placeholder)
            // Rice/Wheat: ~20 quintal, Maize: ~25 quintal, Cotton: ~10 quintal, Sugarcane: ~300 quintal
            const averageYield = { "चावल": 20, "गेहूँ": 20, "मक्का": 25, "कपास": 10, "गन्ना": 300 }[selectedCrop];
            
            const totalIncome = mandiPrice * averageYield;
            const profit = totalIncome - cost;

            profitResultDiv.innerHTML = `
                <h4 class="text-xl font-bold text-green-800 mb-2">${selectedCrop} के लिए लाभ विश्लेषण</h4>
                <p class="text-gray-700">अनुमानित मंडी भाव: <span class="font-semibold">₹${mandiPrice}/क्विंटल</span></p>
                <p class="text-gray-700">अनुमानित उपज: <span class="font-semibold">${averageYield} क्विंटल/एकड़</span></p>
                <p class="text-gray-700">कुल आय: <span class="font-semibold">₹${totalIncome.toLocaleString('hi-IN')}</span></p>
                <p class="text-gray-700">आपकी लागत: <span class="font-semibold">- ₹${cost.toLocaleString('hi-IN')}</span></p>
                <hr class="my-2">
                <p class="text-lg text-green-900">अनुमानित शुद्ध लाभ (प्रति एकड़): <span class="font-bold text-2xl">₹${profit.toLocaleString('hi-IN')}</span></p>
            `;
            profitResultDiv.classList.remove('hidden');
            profitResultDiv.classList.remove('border-red-200', 'bg-red-100');
            profitResultDiv.classList.add('border-green-200', 'bg-green-100');
        }

    </script>
</body>
</html>
