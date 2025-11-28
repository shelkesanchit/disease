document.addEventListener('DOMContentLoaded', function() {
    // Set current year in footer
    document.getElementById('current-year').textContent = new Date().getFullYear();
    
    // DOM elements
    const geolocateBtn = document.getElementById('geolocate-btn');
    const coordinatesDiv = document.getElementById('coordinates');
    const latLonSpan = document.getElementById('lat-lon');
    const useCoordinatesBtn = document.getElementById('use-coordinates');
    const cityInput = document.getElementById('city-input');
    const searchCityBtn = document.getElementById('search-city-btn');
    const weatherSection = document.getElementById('weather-section');
    const predictionSection = document.getElementById('prediction-section');
    const predictDiseaseBtn = document.getElementById('predict-disease-btn');
    const newPredictionBtn = document.getElementById('new-prediction-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    const errorModal = document.getElementById('error-modal');
    const errorMessage = document.getElementById('error-message');
    const errorOkBtn = document.getElementById('error-ok-btn');
    const closeModal = document.querySelector('.close-modal');
    
    // Weather data storage
    let currentWeatherData = null;
    
    // Event listeners
    geolocateBtn.addEventListener('click', getUserLocation);
    useCoordinatesBtn.addEventListener('click', () => {
        const [lat, lon] = latLonSpan.dataset.coords.split(',');
        getWeatherByCoords(lat, lon);
    });
    
    searchCityBtn.addEventListener('click', () => {
        const city = cityInput.value.trim();
        if (city) {
            getWeatherByCity(city);
        } else {
            showError('Please enter a city name.');
        }
    });
    
    cityInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchCityBtn.click();
        }
    });
    
    predictDiseaseBtn.addEventListener('click', predictDisease);
    newPredictionBtn.addEventListener('click', resetToPrediction);
    
    errorOkBtn.addEventListener('click', () => {
        errorModal.classList.add('hidden');
    });
    
    closeModal.addEventListener('click', () => {
        errorModal.classList.add('hidden');
    });
    
    // Get user's location
    function getUserLocation() {
        showLoading('Getting your location...');
        
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude.toFixed(4);
                    const lon = position.coords.longitude.toFixed(4);
                    
                    latLonSpan.textContent = `Lat: ${lat}, Lon: ${lon}`;
                    latLonSpan.dataset.coords = `${lat},${lon}`;
                    coordinatesDiv.classList.remove('hidden');
                    hideLoading();
                },
                (error) => {
                    hideLoading();
                    let errorMsg = 'Unable to retrieve your location.';
                    
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMsg = 'Location access denied. Please enable location permissions.';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMsg = 'Location information is unavailable.';
                            break;
                        case error.TIMEOUT:
                            errorMsg = 'Location request timed out.';
                            break;
                        case error.UNKNOWN_ERROR:
                            errorMsg = 'An unknown error occurred.';
                            break;
                    }
                    
                    showError(errorMsg);
                }
            );
        } else {
            hideLoading();
            showError('Geolocation is not supported by this browser.');
        }
    }
    
    // Get weather by coordinates
    function getWeatherByCoords(lat, lon) {
        showLoading('Fetching weather data...');
        
        fetch('/get_weather', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ lat, lon }),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to fetch weather data');
                });
            }
            return response.json();
        })
        .then(data => {
            hideLoading();
            displayWeatherData(data);
        })
        .catch(error => {
            hideLoading();
            showError(error.message);
        });
    }
    
    // Get weather by city name
    function getWeatherByCity(city) {
        showLoading('Fetching weather data...');
        
        fetch('/get_weather', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ city }),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to fetch weather data');
                });
            }
            return response.json();
        })
        .then(data => {
            hideLoading();
            displayWeatherData(data);
        })
        .catch(error => {
            hideLoading();
            showError(error.message);
        });
    }
    
    // Format date and time
    function formatDateTime() {
        const now = new Date();
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return now.toLocaleDateString(undefined, options);
    }
    
    // Display weather data
    function displayWeatherData(data) {
        currentWeatherData = data;
        
        const weather = data.weather;
        const recommendations = data.farming_recommendations;
        
        // Update location and date
        document.getElementById('location-name').textContent = `${weather.name}, ${weather.sys.country}`;
        document.getElementById('date-time').textContent = formatDateTime();
        
        // Update weather icon
        const iconCode = weather.weather[0].icon;
        const iconUrl = `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
        document.getElementById('weather-icon-img').src = iconUrl;
        
        // Update weather data
        document.getElementById('temperature').textContent = `${weather.main.temp.toFixed(1)}°C`;
        document.getElementById('humidity').textContent = `${weather.main.humidity}%`;
        document.getElementById('wind-speed').textContent = `${weather.wind.speed} m/s`;
        
        // Estimate precipitation (not directly available in current weather data)
        let precipitationText = '0 mm';
        if (weather.rain) {
            precipitationText = `${weather.rain['1h'] || 0} mm`;
        } else if (weather.snow) {
            precipitationText = `${weather.snow['1h'] || 0} mm`;
        }
        document.getElementById('precipitation').textContent = precipitationText;
        
        // Update farming recommendations
        const recList = document.getElementById('farming-recommendations-list');
        recList.innerHTML = '';
        
        if (Object.keys(recommendations).length === 0) {
            const li = document.createElement('li');
            li.textContent = 'No specific recommendations for current conditions.';
            recList.appendChild(li);
        } else {
            for (const [key, value] of Object.entries(recommendations)) {
                const li = document.createElement('li');
                li.textContent = value;
                recList.appendChild(li);
            }
        }
        
        // Show weather section
        weatherSection.classList.remove('hidden');
        predictionSection.classList.add('hidden');
        
        // Scroll to weather section
        weatherSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Predict disease based on weather data
    function predictDisease() {
        if (!currentWeatherData) {
            showError('Weather data not available. Please fetch weather data first.');
            return;
        }
        
        showLoading('Analyzing disease risk...');
        
        const weather = currentWeatherData.weather;
        
        // Extract required data for prediction
        const predictionData = {
            temp: weather.main.temp,
            humidity: weather.main.humidity,
            wind_speed: weather.wind.speed,
            precipitation: weather.rain ? (weather.rain['1h'] || 0) : 0
        };
        
        fetch('/predict_disease', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(predictionData),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to predict disease');
                });
            }
            return response.json();
        })
        .then(data => {
            hideLoading();
            displayPredictionResults(data);
        })
        .catch(error => {
            hideLoading();
            showError(error.message);
        });
    }
    
    // Display prediction results
    function displayPredictionResults(data) {
        const disease = data.predicted_disease;
        const confidence = data.confidence * 100;
        const recommendations = data.recommendations;
        
        // Update disease name and status indicator
        document.getElementById('predicted-disease').textContent = disease;
        
        const statusIndicator = document.getElementById('prediction-result-status');
        statusIndicator.className = 'status-indicator';
        
        // Set icon based on disease
        if (disease === 'Healthy') {
            statusIndicator.classList.add('status-healthy');
            statusIndicator.innerHTML = '<i class="fas fa-check-circle"></i>';
        } else {
            if (confidence > 80) {
                statusIndicator.classList.add('status-danger');
                statusIndicator.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
            } else {
                statusIndicator.classList.add('status-warning');
                statusIndicator.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
            }
        }
        
        // Update risk meter
        const riskLevel = document.getElementById('risk-level');
        riskLevel.style.width = `${confidence}%`;
        riskLevel.className = 'level';
        
        if (disease === 'Healthy') {
            riskLevel.classList.add('risk-low');
        } else if (confidence > 80) {
            riskLevel.classList.add('risk-high');
        } else {
            riskLevel.classList.add('risk-medium');
        }
        
        document.getElementById('confidence-percentage').textContent = `${confidence.toFixed(1)}%`;
        
        // Update recommendations
        const recList = document.getElementById('disease-recommendations-list');
        recList.innerHTML = '';
        
        if (recommendations.length === 0) {
            const li = document.createElement('li');
            li.textContent = 'No specific recommendations available.';
            recList.appendChild(li);
        } else {
            recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = rec;
                recList.appendChild(li);
            });
        }
        
        // Show prediction section
        weatherSection.classList.add('hidden');
        predictionSection.classList.remove('hidden');
        
        // Scroll to prediction section
        predictionSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Reset to get a new prediction
    function resetToPrediction() {
        weatherSection.classList.remove('hidden');
        predictionSection.classList.add('hidden');
        weatherSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Show loading overlay
    function showLoading(message) {
        loadingText.textContent = message || 'Loading...';
        loadingOverlay.classList.remove('hidden');
    }
    
    // Hide loading overlay
    function hideLoading() {
        loadingOverlay.classList.add('hidden');
    }
    
    // Show error modal
    function showError(message) {
        errorMessage.textContent = message;
        errorModal.classList.remove('hidden');
    }
});