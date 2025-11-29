from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash, send_from_directory
from flask_cors import CORS
import requests
import os
import io
import base64
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import cv2
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import joblib
from datetime import datetime, timedelta
import json
import calendar
import math
import uuid
from werkzeug.security import check_password_hash, generate_password_hash
from bson import ObjectId
from bson.objectid import ObjectId
import pickle
import pandas as pd
import google.generativeai as genai
from pymongo import MongoClient
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# DATABASE CONFIGURATION (Previously in database.py)
# ============================================================================

# MongoDB connection string
MONGO_URI = os.getenv('MONGO_URI')

try:
    # Create MongoDB client
    client = MongoClient(MONGO_URI)
    
    # Test the connection
    client.server_info()
    
    # Get database
    db = client.agrishield
    
    # Collections
    users_collection = db.users
    products_collection = db.products
    reviews_collection = db.reviews
    orders_collection = db.orders
    
    print("Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise

def init_db():
    """Initialize database with required indexes"""
    try:
        # Create indexes
        users_collection.create_index('email', unique=True)
        products_collection.create_index('category')
        reviews_collection.create_index('product_id')
        reviews_collection.create_index('user_id')
        orders_collection.create_index('user_id')
        orders_collection.create_index('status')
        print("Database indexes created successfully!")
    except Exception as e:
        print(f"Error creating indexes: {e}")
        raise

def get_user_by_email1(email):
    """Get user by email"""
    try:
        return users_collection.find_one({'email': email})
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def get_product_by_id(product_id):
    """Get product by ID"""
    try:
        return products_collection.find_one({'_id': ObjectId(product_id)})
    except Exception as e:
        print(f"Error getting product: {e}")
        return None

def get_reviews_by_product(product_id):
    """Get all reviews for a product"""
    try:
        return list(reviews_collection.find({'product_id': ObjectId(product_id)}))
    except Exception as e:
        print(f"Error getting reviews: {e}")
        return []

def get_orders_by_user(user_id):
    """Get all orders for a user"""
    try:
        return list(orders_collection.find({'user_id': ObjectId(user_id)}))
    except Exception as e:
        print(f"Error getting orders: {e}")
        return []

def update_product_rating(product_id):
    """Update product rating based on reviews"""
    try:
        # Get all reviews for the product
        reviews = list(reviews_collection.find({'product_id': ObjectId(product_id)}))
        
        if not reviews:
            return
        
        # Calculate average rating
        total_rating = sum(review['rating'] for review in reviews)
        average_rating = total_rating / len(reviews)
        
        # Update product
        products_collection.update_one(
            {'_id': ObjectId(product_id)},
            {
                '$set': {
                    'rating': average_rating,
                    'review_count': len(reviews)
                }
            }
        )
    except Exception as e:
        print(f"Error updating product rating: {e}")
        raise

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================
# Import our models and utils
from models import (
    create_user, authenticate_user, get_user_by_id, get_user_by_email,
    create_farm, get_farms_by_user, get_farm_by_id, delete_farm,
    create_schedule, get_schedule_by_farm_id, update_task_status,
    save_weather_data, get_latest_weather,
    create_alert, get_alerts_by_user, mark_alert_as_read, delete_alert,
    grape_varieties_collection, db,
    get_grape_varieties, get_variety_info,
    create_plant_note, get_plant_notes_by_farm, get_plant_note,
    update_plant_note, delete_plant_note,
    JSONEncoder,
    # Add new consultant imports
    create_consultant, authenticate_consultant, get_consultant_by_id,
    get_consultant_by_email, get_consultants_by_location, get_all_consultants,
    create_comment, get_comments_by_farm, update_comment, delete_comment,
    assign_consultant_to_farmer, get_farmers_by_consultant, get_farm_details_by_id,
    consultants_collection
)
from utils import (
    get_weather_data, get_weather_data_by_coords, generate_farming_timeline, calculate_farm_layout,
    get_seasonal_activities, generate_pdf_plan, get_gemini_recommendation
)
# Set environment variable to disable OneDNN optimizations to avoid warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

app = Flask(__name__)
CORS(app)

# Global model variables (will be loaded on first use)
model = None
modelgrape = None
weather_model = None
scaler = None
encoder = None

# Lazy load models function
def load_models_if_needed():
    """Load models only when first needed to reduce startup time and memory"""
    global model, modelgrape, weather_model, scaler, encoder
    
    if model is None:
        print("Loading grape_model.h5...")
        model = load_model("grape_model.h5")
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        print("grape_model.h5 loaded successfully")
    
    if weather_model is None:
        print("Loading grape_leaf_disease_model.h5...")
        weather_model = load_model('grape_leaf_disease_model.h5')
        print("grape_leaf_disease_model.h5 loaded successfully")
    
    if scaler is None:
        print("Loading scaler.pkl...")
        scaler = joblib.load('scaler.pkl')
        print("scaler.pkl loaded successfully")
    
    if encoder is None:
        print("Loading label_encoder.pkl...")
        encoder = joblib.load('label_encoder.pkl')
        print("label_encoder.pkl loaded successfully")
    
    # modelgrape remains None (Apple disease model disabled)

# Class labels for grape diseases
class_names = ['Black Rot', 'Leaf Blight', 'Healthy', 'ESCA']
class_namesgrape = {
    1: "Healthy",  # Swapped from 0
    0: "Blotch Apple",  # Swapped from 1
    2: "Rotten Apple",
    3: "Scab Apple"
}

# Disease Information Dictionary
disease_info = {
    'Black Rot': {
        'symptoms': [
            'Circular brown lesions on leaves',
            'Dark sunken spots on fruit',
            'Fruit shriveling and drying on vines'
        ],
        'pesticides': ['Mancozeb', 'Myclobutanil', 'Captan','Copper Oxychloride'],
        'prevention': ['Prune infected parts', 'Ensure good air circulation']
    },
    'Leaf Blight': {
        'symptoms': ['Yellowish-brown spots on leaves', 'Leaf curling'],
        'pesticides': ['Streptomycin Sulfate', 'Copper Oxychloride','Ranman 400SC'],
        'prevention': ['Remove fallen leaves', 'Use resistant varieties']
    },
    'Healthy': {
        'symptoms': ['Lush green leaves', 'Healthy fruit production'],
        'pesticides': ['Neem Oil Spray', 'Sulfur Dust'],
        'prevention': ['Optimal watering', 'Regular plant inspection']
    },
    'ESCA': {
        'symptoms': ['Wood discoloration', 'Sudden wilting'],
        'pesticides': ['Fluazinam', 'Carbendazim','Manzate'],
        'prevention': ['Avoid wounding vines', 'Proper irrigation techniques']
    }
}


app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_KEY'] = str(uuid.uuid4())  # Random UUID instead of secret key
app.config['MONGO_URI'] = os.getenv('MONGO_URI')

# For Flask session to work, we need a secret key
app.secret_key = str(uuid.uuid4())

# Set the custom JSON encoder for the Flask app
app.json_encoder = JSONEncoder

# Template context processor to provide date variables to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Custom filter for formatting Unix timestamps to time
@app.template_filter('timestamp_to_time')
def timestamp_to_time(unix_timestamp):
    """Convert Unix timestamp to formatted time HH:MM"""
    try:
        # Convert Unix timestamp to datetime
        time_obj = datetime.utcfromtimestamp(unix_timestamp)
        return time_obj.strftime('%H:%M')
    except Exception as e:
        # If there's an error, return a placeholder
        return "--:--"



# Set upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPLOAD_FOLDERG = 'static/uploads/'
if not os.path.exists(UPLOAD_FOLDERG):
    os.makedirs(UPLOAD_FOLDERG)
app.config['UPLOAD_FOLDERG'] = UPLOAD_FOLDERG

def preprocess_image(image_path, target_size=(224, 224)):
    img = load_img(image_path, target_size=target_size)
    x = img_to_array(img)
    x = x.astype('float32') / 255.
    x = np.expand_dims(x, axis=0)
    return x

def is_grape_leaf_image(image_path):
    """
    Check if the image is a grape leaf and not a human, clothing, or fruit.
    Returns: (is_leaf, message)
    """
    img = cv2.imread(image_path)
    if img is None:
        return False, "Could not read image file"
    
    # Convert to HSV for color analysis
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define color ranges for unsupported objects
    # Human skin tones
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)
    skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
    skin_percentage = np.sum(skin_mask > 0) / (skin_mask.shape[0] * skin_mask.shape[1])
    
    # Clothing colors (e.g., blue for jeans, red for shirts)
    lower_blue = np.array([90, 50, 50], dtype=np.uint8)
    upper_blue = np.array([130, 255, 255], dtype=np.uint8)
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    blue_percentage = np.sum(blue_mask > 0) / (blue_mask.shape[0] * blue_mask.shape[1])
    
    lower_red1 = np.array([0, 70, 50], dtype=np.uint8)
    upper_red1 = np.array([10, 255, 255], dtype=np.uint8)
    lower_red2 = np.array([170, 70, 50], dtype=np.uint8)
    upper_red2 = np.array([180, 255, 255], dtype=np.uint8)
    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    red_percentage = np.sum(red_mask > 0) / (red_mask.shape[0] * red_mask.shape[1])
    
    # Fruit-like structures (based on color and shape)
    fruit_color_ranges = [
        (np.array([0, 70, 50]), np.array([10, 255, 255])),  # Red
        (np.array([170, 70, 50]), np.array([180, 255, 255])),  # Red (wrapped)
        (np.array([10, 70, 50]), np.array([30, 255, 255])),  # Orange
        (np.array([25, 50, 50]), np.array([35, 255, 255])),  # Yellow
        (np.array([130, 30, 30]), np.array([160, 255, 255]))  # Purple
    ]
    combined_fruit_mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
    for lower, upper in fruit_color_ranges:
        color_mask = cv2.inRange(hsv, lower, upper)
        combined_fruit_mask = cv2.bitwise_or(combined_fruit_mask, color_mask)
    fruit_color_percentage = np.sum(combined_fruit_mask > 0) / (combined_fruit_mask.shape[0] * combined_fruit_mask.shape[1])
    
    # Grape leaf detection (based on green color)
    lower_green = np.array([25, 30, 30], dtype=np.uint8)
    upper_green = np.array([95, 255, 255], dtype=np.uint8)
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    green_percentage = np.sum(green_mask > 0) / (green_mask.shape[0] * green_mask.shape[1])
    
    # Check for unsupported objects
    if skin_percentage > 0.15:  # Significant skin tone detected
        return False, "Unsupported image: Human detected"
    if blue_percentage > 0.25 or red_percentage > 0.25:  # Significant clothing colors detected
        return False, "Unsupported image: Clothing detected"
    if fruit_color_percentage > 0.4:  # Significant fruit-like colors detected
        return False, "Unsupported image: Fruit detected"
    
    # Check for grape leaf
    if green_percentage > 0.15:  # At least 15% green pixels
        return True, "Grape leaf detected"
    else:
        return False, "Unsupported image: Not a grape leaf"

def is_apple_image(img_path):
    """
    Check if the image is of an apple.
    """
    img = cv2.imread(img_path)
    if img is None:
        return False
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    if np.sum(mask) > 10000:  # Threshold for red pixels
        return True
    return False



#for grape type
import pickle
import joblib  # Add joblib as an alternative for loading models
import os
import traceback
from pathlib import Path

# Set up Gemini API
GEMINI_API_KEY1 = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY1)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Define model variable globally
model1 = None

# Load the trained model with enhanced error handling
def load_grape_model():
    global model1
    
    # Define possible paths to try
    model_paths = [
        r"C:\Users\tz8e\OneDrive\Desktop\disease\grape_variety_model.pkl",  # Absolute path
        "grape_variety_model.pkl",  # Relative path in current directory
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "grape_variety_model.pkl"),  # Relative to script
        os.path.join(os.path.abspath(os.getcwd()), "grape_variety_model.pkl")  # Current working directory
    ]
    
    # Try each path
    for model_path in model_paths:
        # Check if file exists
        if not os.path.exists(model_path):
            print(f"Model file not found at: {model_path}")
            continue
            
        # Try different loading methods
        try:
            print(f"Attempting to load model from: {model_path}")
            with open(model_path, 'rb') as file:
                model1 = pickle.load(file)
            print(f"Successfully loaded model using pickle from: {model_path}")
            return True
        except Exception as pickle_error:
            print(f"Error loading with pickle: {str(pickle_error)}")
            try:
                # Try joblib as an alternative
                model1 = joblib.load(model_path)
                print(f"Successfully loaded model using joblib from: {model_path}")
                return True
            except Exception as joblib_error:
                print(f"Error loading with joblib: {str(joblib_error)}")
                continue
    
    # If we get here, all attempts failed
    print("All attempts to load the model failed.")
    print("Current working directory:", os.getcwd())
    print("Files in the current directory:", os.listdir('.'))
    print("Python process owner:", os.getlogin())
    return False

# Load the model at startup
load_result = load_grape_model()
if not load_result:
    print("WARNING: Failed to load the grape variety model at startup. Predictions will not work!")

# OpenWeather API key
API_KEY1 = os.getenv('OPENWEATHER_API_KEY')


@app.route('/grapetyperec')
def grapetyperec():
    global model1
    if model1 is None:
        # Try loading again when page is accessed
        load_grape_model()
    return render_template('grapetyperec.html')

def get_grape_description(variety_name):
    """Use Gemini API to get a detailed description of a grape variety."""
    try:
        prompt = f"""Provide a detailed description of the grape variety '{variety_name}' for wine production. 
        Include information about its origin, flavor profile, growing conditions, and common wine styles.
        Keep the description to 2-3 sentences, focusing on the most important characteristics."""
        
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error getting description from Gemini API: {str(e)}")
        # Fallback to basic descriptions if API fails
        fallback_descriptions = {
            "Cabernet Sauvignon": "A robust red grape variety known for its deep color, full body, and structured tannins. Thrives in moderate to warm climates.",
            "Chardonnay": "A versatile white grape that produces wines ranging from crisp and mineral-driven to rich and buttery. Adaptable to various climates.",
            "Pinot Noir": "A delicate red variety that produces elegant wines with red fruit flavors. Prefers cooler climates with moderate sunlight.",
            "Bangalore Blue": "A South Indian variety of Concord grapes, known for its sweet, musky flavor. Well-adapted to tropical conditions."
        }
        return fallback_descriptions.get(variety_name, "A grape variety used in wine production.")

def get_growing_recommendations(variety_name):
    """Use Gemini API to get growing recommendations for a grape variety."""
    try:
        prompt = f"""Provide specific growing recommendations for the grape variety '{variety_name}' for vineyard management.
        Include key information about soil preferences, climate needs, pruning techniques, and disease management.
        Keep the recommendations to 2-3 sentences, focusing on the most practical advice."""
        
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error getting recommendations from Gemini API: {str(e)}")
        # Fallback to basic recommendations if API fails
        fallback_recommendations = {
            "Cabernet Sauvignon": "Plant in well-draining soils with full sun exposure. Requires regular pruning to control vigor and yield. Water moderately and apply balanced fertilization.",
            "Chardonnay": "Plant in limestone-rich soils when possible. Moderate water needs with good drainage. Manage canopy to control sun exposure based on desired wine style.",
            "Pinot Noir": "Requires careful site selection with good drainage and moderate temperatures. Sensitive to wind and frost; consider protection if needed. Careful canopy management is essential.",
            "Bangalore Blue": "Grows well in tropical and subtropical climates. Plant in well-draining loamy soil with regular water during growing season. Trellising helps with air circulation and managing the vigorous growth."
        }
        return fallback_recommendations.get(variety_name, "Plant in suitable soil with proper drainage and appropriate climate conditions for this variety.")

@app.route('/predictgrp', methods=['POST'])
def predictgrp():
    global model1
    data = request.json
    
    # Log the incoming data for debugging
    print(f"\n{'='*60}")
    print(f"Grape Variety Prediction Request")
    print(f"{'='*60}")
    print(f"Weather Data: {data['weather']}")
    print(f"Soil Data: {data['soil']}")
    
    # Check if model is loaded
    if model1 is None:
        print("⚠️ WARNING: Model is not loaded!")
        # Try to load the model again if it's not loaded
        load_result = load_grape_model()
        
        # If still not loaded, return error
        if not load_result or model1 is None:
            print("❌ Model loading failed during prediction attempt")
            return jsonify({
                'success': False,
                'message': "The grape variety prediction model could not be loaded. This may be due to scikit-learn version mismatch. Please upgrade scikit-learn to version 1.6.1 or higher using: pip install scikit-learn==1.6.1"
            })
    
    # Extract data from request
    weather_data = data['weather']
    soil_data = data['soil']
    
    # Create a DataFrame with the input data
    input_data = {
        "Temperature (°C)": weather_data['temp'],
        "Min Temperature (°C)": weather_data['temp_min'],
        "Max Temperature (°C)": weather_data['temp_max'],
        "Humidity (%)": weather_data['humidity'],
        "Pressure (hPa)": weather_data['pressure'],
        "Weather Condition": weather_data['condition'],
        "Wind Speed (m/s)": weather_data['wind_speed'],
        "Wind Direction (°)": weather_data['wind_deg'],
        "Soil pH": soil_data['ph'],
        "Soil Moisture (%)": soil_data['moisture'],
        "N (Nitrogen)": soil_data['nitrogen'],
        "P (Phosphorus)": soil_data['phosphorus'],
        "K (Potassium)": soil_data['potassium'],
        "Type of Soil": soil_data['type']
    }
    
    print(f"\nInput Data for Model:")
    print(f"Temperature: {input_data['Temperature (°C)']}°C")
    print(f"Humidity: {input_data['Humidity (%)']}%")
    print(f"Soil Type: {input_data['Type of Soil']}")
    print(f"Soil pH: {input_data['Soil pH']}")
    
    # Check if input is valid for grape cultivation
    is_valid = validate_parameters(input_data)
    
    if not is_valid['valid']:
        print(f"❌ Validation failed: {is_valid['message']}")
        return jsonify({
            'success': False,
            'message': is_valid['message']
        })
    
    # Create DataFrame from input_data
    df = pd.DataFrame([input_data])
    
    # Make prediction
    try:
        print("\n🔮 Making prediction...")
        prediction = model1.predict(df)
        predicted_variety = prediction[0]
        
        print(f"✅ Predicted Variety: {predicted_variety}")
        
        # Log prediction probabilities if available
        if hasattr(model1, 'predict_proba'):
            try:
                probabilities = model1.predict_proba(df)
                if hasattr(model1, 'classes_'):
                    print(f"\nPrediction Probabilities:")
                    for variety, prob in zip(model1.classes_, probabilities[0]):
                        print(f"  {variety}: {prob*100:.2f}%")
            except Exception as prob_error:
                print(f"Could not get probabilities: {str(prob_error)}")
        
        # Get description and recommendations from Gemini API
        description = get_grape_description(predicted_variety)
        recommendations = get_growing_recommendations(predicted_variety)
        
        return jsonify({
            'success': True,
            'variety': predicted_variety,
            'description': description,
            'recommendations': recommendations
        })
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Prediction error: {str(e)}\n{error_details}")
        
        # Provide more detailed error information
        if "KeyError" in str(e):
            return jsonify({
                'success': False,
                'message': f"Missing key in model input: {str(e)}"
            })
        else:
            return jsonify({
                'success': False,
                'message': f"Prediction error: {str(e)}. This may be due to scikit-learn version mismatch."
            })

@app.route('/get_weatherforg', methods=['POST'])
def get_weatherforg():
    data = request.json
    lat = data['lat']
    lon = data['lon']
    
    # Call OpenWeather API
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY1}&units=metric"
    
    try:
        response = requests.get(url)
        weather_data = response.json()
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'data': {
                    'temp': weather_data['main']['temp'],
                    'temp_min': weather_data['main']['temp_min'],
                    'temp_max': weather_data['main']['temp_max'],
                    'humidity': weather_data['main']['humidity'],
                    'pressure': weather_data['main']['pressure'],
                    'condition': weather_data['weather'][0]['main'],
                    'wind_speed': weather_data['wind']['speed'],
                    'wind_deg': weather_data['wind']['deg']
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': f"Weather API Error: {weather_data.get('message', 'Unknown error')}"
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error fetching weather data: {str(e)}"
        })

def validate_parameters(data):
    """Validate if the climate and soil parameters are suitable for grape cultivation"""
    
    # Define acceptable ranges for grape cultivation
    valid_ranges = {
        "Temperature (°C)": (10, 38),
        "Humidity (%)": (6, 45),  # Updated for air humidity (not soil)
        "Soil pH": (4.5, 8.5),
        "Soil Moisture (%)": (10, 60),
        "N (Nitrogen)": (50, 300),
        "P (Phosphorus)": (10, 150),
        "K (Potassium)": (50, 250)
    }
    
    # Check each parameter
    for param, (min_val, max_val) in valid_ranges.items():
        if data[param] < min_val or data[param] > max_val:
            return {
                'valid': False,
                'message': f"Invalid {param}: Value {data[param]} is outside the acceptable range ({min_val} - {max_val}) for grape cultivation."
            }
    
    # Check soil type
    valid_soil_types = ["Sandy", "Clayey", "Loamy", "Laterite", "Black"]
    if data["Type of Soil"] not in valid_soil_types:
        return {
            'valid': False,
            'message': f"Invalid soil type: {data['Type of Soil']}. Must be one of {', '.join(valid_soil_types)}."
        }
    
    # Check weather condition
    unsuitable_conditions = ["Thunderstorm", "Snow", "Tornado", "Hurricane", "Blizzard"]
    if data["Weather Condition"] in unsuitable_conditions:
        return {
            'valid': False,
            'message': f"Unsuitable weather condition: {data['Weather Condition']} is not appropriate for grape cultivation."
        }
    
    return {'valid': True}








# Configuration
# Groq API Configuration for Chatbot
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Gemini API for image processing
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('main without login.html', diseases=class_names)

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({"status": "healthy", "models_loaded": model is not None})

@app.route('/warmup')
def warmup():
    """Warmup endpoint to preload models after deployment"""
    try:
        load_models_if_needed()
        return jsonify({
            "status": "success", 
            "message": "Models loaded successfully",
            "models": {
                "grape_model": model is not None,
                "weather_model": weather_model is not None,
                "scaler": scaler is not None,
                "encoder": encoder is not None
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Get message from form data or JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            message = request.form.get('message', '')
            file = request.files.get('file')
        else:
            data = request.get_json()
            message = data.get('message', '')
            file = None

        if not message and not file:
            return jsonify({"error": "Empty message and no file provided"}), 400

        # If there's a file, process it with Gemini
        if file and allowed_file(file.filename):
            return process_image_with_gemini(file, message)

        # If no file, process text with Groq
        return process_text_with_groq(message)

    except Exception as e:
        return jsonify({
            "error": "Server Error",
            "details": str(e)
        }), 500

def process_text_with_groq(message):
    """
    Process text queries using Groq API with agriculture-focused responses
    """
    try:
        # System prompt to restrict chatbot to agriculture topics only
        system_prompt = """You are an expert agricultural advisor specializing in crop cultivation, plant diseases, pest management, soil health, irrigation, fertilizers, and farming techniques. 

Your expertise includes:
- Crop diseases and their treatments
- Pest identification and management
- Soil testing and nutrient management
- Irrigation systems and water management
- Organic and sustainable farming practices
- Grape cultivation and viticulture
- Apple cultivation and orchard management
- Fertilizer recommendations
- Weather-based farming advice
- Harvesting and post-harvest management

IMPORTANT RULES:
1. ONLY answer questions related to agriculture, farming, crops, plants, soil, irrigation, fertilizers, pesticides, and related agricultural topics.
2. If the user asks about anything NOT related to agriculture (like general knowledge, entertainment, sports, technology not related to farming, etc.), politely respond with: "I apologize, but I don't have expertise in that area. I specialize in agricultural topics only. Please ask me questions related to farming, crop cultivation, plant diseases, soil management, irrigation, or other agricultural matters."
3. Provide practical, actionable advice for farmers.
4. Be concise but informative.
5. Use simple language that farmers can understand.

Always stay within your agricultural expertise domain."""

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.3-70b-versatile",  # Using Llama 3.3 model for better responses
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 1,
            "stream": False
        }

        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            try:
                message_text = response_data['choices'][0]['message']['content']
                return jsonify({"response": message_text})
            except (KeyError, IndexError) as e:
                return jsonify({
                    "error": "Response Processing Error",
                    "details": f"Could not extract message from API response: {str(e)}"
                }), 500
        else:
            return jsonify({
                "error": "API Error",
                "details": f"Error {response.status_code}: {response.text}"
            }), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Timeout Error",
            "details": "The request took too long. Please try again."
        }), 504
    except Exception as e:
        return jsonify({
            "error": "Server Error",
            "details": str(e)
        }), 500

def process_image_with_gemini(file, query):
    """
    Process image queries using Gemini API v1 (not v1beta) with vision capabilities
    Restricted to agriculture-related image analysis only
    """
    try:
        # Read and process image
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes))
        
        # Convert image to base64 for API request
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Agriculture-focused prompt
        agriculture_context = """You are an expert agricultural image analyst. 

IMPORTANT RULES:
1. ONLY analyze agriculture-related images (crops, plant diseases, pests, soil, farming equipment).
2. If the image is NOT related to agriculture, respond: "I apologize, but this image doesn't appear to be related to agriculture. I can only analyze agricultural images such as crops, plant diseases, pests, soil, or farming equipment."
3. Provide detailed, practical analysis for farmers.
4. Suggest treatments for plant diseases if identified.

"""
        
        # Prepare user query with agriculture context
        user_query = agriculture_context + (query if query else "Analyze this agricultural image and provide detailed insights about crop health, diseases, or pests.")
        
        # Use Gemini API v1 with the latest stable model (gemini-2.5-flash)
        api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": user_query},
                        {
                            "inlineData": {
                                "mimeType": "image/jpeg",
                                "data": img_base64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        # Make the API request
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response_json = response.json()
        
        # Extract the generated text
        try:
            generated_text = response_json['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            generated_text = "Error extracting response from API"
            if 'error' in response_json:
                generated_text += f": {response_json['error']['message']}"

        return jsonify({
            'response': generated_text,
            'image': img_base64
        })
    
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'Request timeout. The image processing took too long. Please try again.'
        }), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/disease-detection')
def indexDis():
    return render_template('diseasePageSelection.html', diseases=class_names)

@app.route('/disease-grape')
def grapeDis():
    return render_template('grapeDisease.html', diseases=class_names)

@app.route('/disease-apple')
def appleDis():
    return render_template('apple.html', diseases=class_names)

@app.route('/predict', methods=['POST','GET'])
def predict():
    # Lazy load models on first use
    load_models_if_needed()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part', 'is_leaf': False})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file', 'is_leaf': False})
    
    if file:
        # Check if it's an image file
        allowed_extensions = {'png', 'jpg', 'jpeg'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({
                'error': 'File must be an image (PNG, JPG, JPEG)', 
                'is_leaf': False
            })
        
        # Save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Check if it's a grape leaf
        is_leaf, leaf_message = is_grape_leaf_image(filepath)
        
        if not is_leaf:
            result = {
                'prediction': 'Unsupported',
                'confidence': 0.0,
                'message': leaf_message,
                'is_leaf': False
            }
            return jsonify(result)
        
        # Preprocess and predict
        try:
            img = preprocess_image(filepath)
            pred = model.predict(img)[0]
            predicted_class_index = np.argmax(pred)
            predicted_disease = class_names[predicted_class_index]
            confidence = float(pred[predicted_class_index])
            
            # Get disease information
            disease_data = disease_info.get(predicted_disease, {})
            symptoms = disease_data.get('symptoms', [])
            pesticides = disease_data.get('pesticides', [])
            prevention = disease_data.get('prevention', [])
            
            result = {
                'prediction': predicted_disease,
                'confidence': confidence,
                'message': f'This grape leaf appears to have {predicted_disease} with {confidence:.2%} confidence.',
                'is_leaf': True,
                'disease_info': {
                    'symptoms': symptoms,
                    'pesticides': pesticides,
                    'prevention': prevention
                }
            }
            return jsonify(result)
        
        except Exception as e:
            return jsonify({
                'error': str(e), 
                'is_leaf': True
            })

@app.route('/predictgrape', methods=['POST'])
def predictgrape():
    """
    Handle image upload and prediction.
    NOTE: Apple disease prediction is currently disabled.
    """
    return jsonify({
        'error': 'Apple disease prediction is currently unavailable. This feature has been temporarily disabled.',
        'status': 'disabled'
    })
    
    # DISABLED CODE - Apple disease model removed
    # if 'file' not in request.files:
    #     return jsonify({'error': 'No file uploaded'})
    # 
    # file = request.files['file']
    # if file.filename == '':
    #     return jsonify({'error': 'No file selected'})
    # 
    # # Save the uploaded file
    # filename = secure_filename(file.filename)
    # filepath = os.path.join(app.config['UPLOAD_FOLDERG'], filename)
    # file.save(filepath)
    # print(f"File saved  {filepath}") 
    # # Check if the image is of an apple
    # if not is_apple_image(filepath):
    #     return jsonify({'error': 'Unsupported image. Please upload an image of an apple.'})
    # 
    # # Preprocess the image and make a prediction
    # img_array = preprocess_image(filepath)
    # 
    # prediction = modelgrape.predict(img_array)
    # 
    # predicted_class = np.argmax(prediction)
    # 
    # disease_label = class_namesgrape[predicted_class]
    # 
    # # Get confidence scores for all classes
    # confidence_scores = {class_namesgrape[i]: float(prediction[0][i]) for i in range(len(class_namesgrape))}
    # 
    # return jsonify({
    #     'disease': disease_label, 
    #     'image_url': filepath,
    #     'confidence': confidence_scores
    # })
    
@app.route('/weather1')
def weather1():
    return render_template('weather.html')

@app.route('/capture', methods=['POST'])
def capture():
    """
    Handle image capture from the camera.
    """
    try:
        # Get the base64 image data from the request
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided', 'is_leaf': False})
        
        # Decode the base64 image
        image_data = data['image'].split(',')[1]  # Remove the data URL prefix
        image_bytes = base64.b64decode(image_data)
        
        # Save the image temporarily
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'capture.jpg')
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # Check if it's a grape leaf
        is_leaf, leaf_message = is_grape_leaf_image(filepath)
        
        if not is_leaf:
            result = {
                'prediction': 'Unsupported',
                'confidence': 0.0,
                'message': leaf_message,
                'is_leaf': False
            }
            return jsonify(result)
        
        # Preprocess and predict
        img = preprocess_image(filepath)
        pred = model.predict(img)[0]
        predicted_class_index = np.argmax(pred)
        predicted_disease = class_names[predicted_class_index]
        confidence = float(pred[predicted_class_index])
        
        # Get disease information
        disease_data = disease_info.get(predicted_disease, {})
        symptoms = disease_data.get('symptoms', [])
        pesticides = disease_data.get('pesticides', [])
        prevention = disease_data.get('prevention', [])
        
        result = {
            'prediction': predicted_disease,
            'confidence': confidence,
            'message': f'This grape leaf appears to have {predicted_disease} with {confidence:.2%} confidence.',
            'is_leaf': True,
            'disease_info': {
                'symptoms': symptoms,
                'pesticides': pesticides,
                'prevention': prevention
            }
        }
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': str(e), 
            'is_leaf': True
        })


API_KEY = os.getenv('OPENWEATHER_API_KEY_2')

@app.route('/disease_weather')
def disease_weather():
    return render_template("weathermain.html")

@app.route('/get_weather', methods=['POST'])
def get_weather():
    data = request.json
    
    if 'lat' in data and 'lon' in data:
        # Get weather by coordinates
        lat = data['lat']
        lon = data['lon']
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    elif 'city' in data:
        # Get weather by city name
        city = data['city']
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    else:
        return jsonify({"error": "Invalid request parameters"}), 400
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        
        # Process the data and add farming recommendations
        farming_recommendations = get_farming_recommendations(weather_data)
        
        # Combine weather data with farming recommendations
        result = {
            "weather": weather_data,
            "farming_recommendations": farming_recommendations
        }
        
        return jsonify(result)
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return jsonify({"error": "Location not found"}), 404
        return jsonify({"error": f"API Error: {str(e)}"}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

@app.route('/predict_disease', methods=['POST'])
def predict_disease():
    # Lazy load models on first use
    load_models_if_needed()
    
    data = request.json
    
    try:
        # Extract weather data
        temp = data['temp']
        humidity = data['humidity']
        wind_speed = data['wind_speed']
        precipitation = data['precipitation']
        
        # Prepare input for the model
        numerical_features = np.array([[temp, humidity, wind_speed, precipitation, 0]])
        
        # Scale the numerical features
        numerical_features_scaled = scaler.transform(numerical_features)
        
        # Ensure the input shape matches model expectations
        if numerical_features_scaled.shape[1] != 5:
            raise ValueError(f"Expected 5 input features, but got {numerical_features_scaled.shape[1]} features.")
        
        # Make prediction
        prediction = weather_model.predict(numerical_features_scaled)
        
        # Get the predicted disease
        disease_index = np.argmax(prediction, axis=1)[0]
        
        # Map the disease index to the disease name
        disease_classes = ['Black Rot', 'Leaf Blight', 'ESCA', 'Healthy']
        predicted_disease = disease_classes[disease_index]
        
        # Get recommendations for the predicted disease
        disease_recommendations = get_disease_recommendations(predicted_disease)
        
        result = {
            "predicted_disease": predicted_disease,
            "confidence": float(prediction[0][disease_index]),
            "recommendations": disease_recommendations
        }
        
        return jsonify(result)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({
            "error": f"Prediction Error: {str(e)}",
            "details": error_details
        }), 500

def get_farming_recommendations(weather_data):
    """Generate farming recommendations based on weather data"""
    recommendations = {}
    
    # Extract relevant weather data
    temp = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    weather_condition = weather_data['weather'][0]['main'].lower()
    
    # Temperature based recommendations
    if temp > 30:
        recommendations["irrigation"] = "Increase irrigation by 20%. Water early morning or late evening to reduce evaporation."
        recommendations["crop_stress"] = "High temperature stress likely for crops. Consider shade cloth for sensitive plants."
    elif temp > 25:
        recommendations["irrigation"] = "Maintain regular irrigation schedule. Monitor soil moisture closely."
    elif temp < 5:
        recommendations["frost_protection"] = "Risk of frost damage. Cover sensitive crops and consider using frost protection methods."
    elif temp < 10:
        recommendations["planting"] = "Cool conditions may slow germination. Delay planting heat-loving crops."
    
    # Humidity based recommendations
    if humidity > 80:
        recommendations["disease_risk"] = "High risk of fungal diseases due to high humidity. Monitor crops closely."
        recommendations["spraying"] = "Consider preventative fungicide application if appropriate for your farming system."
    elif humidity < 30:
        recommendations["irrigation"] = "Low humidity may increase water loss. Consider increasing irrigation frequency."
    
    # Wind based recommendations
    if wind_speed > 10:
        recommendations["protection"] = "Strong winds can damage crops. Consider temporary windbreaks for vulnerable plants."
    
    # Weather condition based recommendations
    if "rain" in weather_condition:
        recommendations["field_work"] = "Postpone field operations that require dry conditions."
        recommendations["soil_erosion"] = "Monitor fields for potential erosion. Ensure proper drainage."
    elif "clear" in weather_condition or "sun" in weather_condition:
        recommendations["irrigation"] = "Check soil moisture levels as evaporation rates will be higher."
    
    return recommendations

def get_disease_recommendations(disease):
    """Generate recommendations based on the predicted grape disease"""
    recommendations = {
        "Black Rot": [
            "Remove infected leaves and fruit to reduce spread",
            "Apply fungicides containing captan or myclobutanil",
            "Ensure proper air circulation by pruning",
            "Avoid overhead irrigation"
        ],
        "Leaf Blight": [
            "Apply copper-based fungicides as preventative measure",
            "Improve air circulation in the vineyard",
            "Remove infected plant material promptly",
            "Avoid wetting leaves during irrigation"
        ],
        "ESCA": [
            "Apply sulfur or potassium bicarbonate-based fungicides",
            "Increase sunlight exposure through proper pruning",
            "Maintain good air circulation in the vineyard",
            "Monitor humidity levels and ventilate as needed"
        ],
        "Healthy": [
            "Continue regular monitoring",
            "Maintain balanced fertilization",
            "Implement preventative measures based on weather conditions",
            "Follow recommended vineyard management practices"
        ]
    }
    
    return recommendations.get(disease, ["No specific recommendations available for this condition"])




@app.route('/farm_planner')
def farm_planner():
    if 'user_id' in session:
        # If user is logged in, redirect to dashboard
        return redirect(url_for('dashboard'))
    return render_template('demo1.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        location = request.form.get('location')
        preferred_grape = request.form.get('preferred_grape')
        
        # Check if user already exists
        if get_user_by_email(email):
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('login'))
        
        # Create new user
        user_id = create_user(name, email, password, phone, location, preferred_grape)
        
        if user_id:
            # Log user in
            session['user_id'] = user_id
            flash('Account created successfully!', 'success')
            
            # Fetch weather data for user's location and save
            weather_data = get_weather_data(location)
            if weather_data:
                save_weather_data(location, weather_data)
            
            return redirect(url_for('demo1'))
        else:
            flash('Error creating account. Please try again.', 'error')
    
    # Get grape varieties for dropdown
    grape_varieties = list(grape_varieties_collection.find({}, {"name": 1}))
    return render_template('signup.html', grape_varieties=grape_varieties)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = authenticate_user(email, password)
        
        if user:
            session['user_id'] = str(user['_id'])
            flash('Logged in successfully!', 'success')
            
            # Fetch and update weather data
            weather_data = get_weather_data(user['location'])
            if weather_data:
                save_weather_data(user['location'], weather_data)
            
            return redirect(url_for('demo1'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main_without_login'))

@app.route('/demo1')
def demo1():
    
    return render_template('demo1.html')
@app.route('/main_without_login')
def main_without_login():
    
    return render_template('main without login.html')



@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access your dashboard', 'error')
        return redirect(url_for('login'))
    
    # Get user info
    user = get_user_by_id(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('login'))
    
    # Get user's farms
    farms = get_farms_by_user(session['user_id'])
    
    # Get latest weather data
    weather = get_latest_weather(user['location'])
    
    # Get alerts
    alerts = get_alerts_by_user(session['user_id'])
    
    # Get current seasonal activities
    activities = get_seasonal_activities(datetime.now())
    
    return render_template(
        'dashboard.html',
        user=user,
        farms=farms,
        weather=weather,
        alerts=alerts,
        activities=activities
    )

@app.route('/farm/new', methods=['GET', 'POST'])
def new_farm():
    if 'user_id' not in session:
        flash('Please log in to create a farm', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get form data
        farm_name = request.form.get('farm_name')
        farm_length = float(request.form.get('farm_length'))
        farm_width = float(request.form.get('farm_width'))
        grape_variety = request.form.get('grape_variety')
        plant_width_spacing = float(request.form.get('plant_width_spacing', 1.8))
        plant_length_spacing = float(request.form.get('plant_length_spacing', 2.4))
        
        # Create plant spacing object
        plant_spacing = {
            "width": plant_width_spacing,
            "length": plant_length_spacing
        }
        
        # Create new farm
        farm_id = create_farm(
            session['user_id'],
            farm_name,
            farm_length,
            farm_width, 
            grape_variety,
            plant_spacing
        )
        
        if farm_id:
            flash('Farm created successfully!', 'success')
            return redirect(url_for('farm_details', farm_id=farm_id))
        else:
            flash('Error creating farm. Please try again.', 'error')
    
    # Get grape varieties for dropdown
    grape_varieties = list(grape_varieties_collection.find({}, {"name": 1, "recommended_spacing": 1}))
    
    return render_template('new_farm.html', grape_varieties=grape_varieties)

@app.route('/farm/<farm_id>')
def farm_details(farm_id):
    if 'user_id' not in session:
        flash('Please log in to view farm details', 'error')
        return redirect(url_for('login'))
    
    # Get farm details
    farm = get_farm_by_id(farm_id)
    if not farm:
        flash('Farm not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if user owns this farm
    if str(farm['user_id']) != session['user_id']:
        flash('Access denied: You do not own this farm', 'error')
        return redirect(url_for('dashboard'))
    
    # Get farm schedule
    schedule = get_schedule_by_farm_id(farm_id)
    
    # Get layout data
    layout = calculate_farm_layout(
        farm['length'], 
        farm['width'], 
        farm['plant_spacing']['length'], 
        farm['plant_spacing']['width']
    )
    
    # Get comments from consultants
    comments = get_comments_by_farm(farm_id)
    
    # Get user details to check if consultant is assigned
    user = get_user_by_id(session['user_id'])
    consultant_name = None
    
    if user and 'consultant_id' in user and user['consultant_id']:
        consultant = get_consultant_by_id(user['consultant_id'])
        if consultant:
            consultant_name = consultant['name']
    
    return render_template(
        'farm_details.html',
        farm=farm,
        schedule=schedule,
        layout=layout,
        comments=comments,
        user=user,
        consultant_name=consultant_name
    )

@app.route('/farm/<farm_id>/schedule', methods=['GET', 'POST'])
def farm_schedule(farm_id):
    if 'user_id' not in session:
        flash('Please log in to access farm schedule', 'error')
        return redirect(url_for('login'))
    
    # Get farm details
    farm = get_farm_by_id(farm_id)
    if not farm:
        flash('Farm not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if user owns this farm
    if str(farm['user_id']) != session['user_id']:
        flash('Access denied: You do not own this farm', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Get planting date
        planting_date = request.form.get('planting_date')
        try:
            planting_date = datetime.strptime(planting_date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('farm_schedule', farm_id=farm_id))
        
        # Generate farming timeline
        tasks = generate_farming_timeline(farm['grape_variety'], planting_date)
        
        # Set end date to 3 years after planting date
        end_date = planting_date.replace(year=planting_date.year + 3)
        
        # Create or update schedule
        existing_schedule = get_schedule_by_farm_id(farm_id)
        
        if existing_schedule:
            from bson.objectid import ObjectId
            from models import schedules_collection
            
            schedules_collection.update_one(
                {"_id": ObjectId(existing_schedule['_id'])},
                {
                    "$set": {
                        "planting_date": planting_date,
                        "end_date": end_date,
                        "tasks": tasks,
                        "updated_at": datetime.now()
                    }
                }
            )
            
            schedule_id = str(existing_schedule['_id'])
            flash('Schedule updated successfully!', 'success')
        else:
            schedule_id = create_schedule(farm_id, planting_date, tasks, end_date)
            flash('Schedule created successfully!', 'success')
        
        # Create alert for upcoming tasks
        upcoming_tasks = [task for task in tasks if datetime.strptime(task['start_date'], '%Y-%m-%d') <= datetime.now() + timedelta(days=7)]
        
        for task in upcoming_tasks[:3]:  # Limit to 3 alerts
            create_alert(
                session['user_id'],
                farm_id,
                f"Upcoming task: {task['title']} - {task['description']}",
                "task",
                datetime.strptime(task['due_date'], '%Y-%m-%d')
            )
        
        return redirect(url_for('farm_details', farm_id=farm_id))
    
    # Get current schedule if exists
    schedule = get_schedule_by_farm_id(farm_id)
    
    return render_template(
        'farm_schedule.html',
        farm=farm,
        schedule=schedule
    )


@app.route('/api/task/<schedule_id>/<task_id>', methods=['PUT'])
def update_task(schedule_id, task_id):
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get data from request
    data = request.get_json()
    status = data.get('status')
    
    if not status:
        return jsonify({"error": "Status is required"}), 400
    
    # Update task status
    success = update_task_status(schedule_id, task_id, status)
    
    if success:
        # Get the task details and farm details
        from models import schedules_collection, tasks_collection, get_farm_by_id
        from bson.objectid import ObjectId
        
        schedule = schedules_collection.find_one({"_id": ObjectId(schedule_id)})
        if schedule:
            farm_id = schedule.get('farm_id')
            farm = get_farm_by_id(farm_id)
            task = None
            
            # Find the task in the schedule
            for t in schedule.get('tasks', []):
                if t.get('id') == task_id:
                    task = t
                    break
            
            if task and farm:
                # Create notification for completed task
                if status == 'completed':
                    create_alert(
                        session['user_id'],
                        farm_id,
                        f"Task completed: {task.get('title')} for {farm.get('farm_name')}",
                        "task_completed",
                        datetime.now()
                    )
                # Create reminder notification if task is due soon and status is pending
                elif status == 'pending' and 'due_date' in task:
                    due_date = datetime.strptime(task.get('due_date'), '%Y-%m-%d')
                    if due_date - datetime.now() <= timedelta(days=3):
                        create_alert(
                            session['user_id'],
                            farm_id,
                            f"Upcoming task reminder: {task.get('title')} for {farm.get('farm_name')} due on {task.get('due_date')}",
                            "task_reminder",
                            due_date
                        )
        
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Failed to update task"}), 500
    

@app.route('/api/pending-tasks')
def get_pending_tasks():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get user's farms
    farms = get_farms_by_user(session['user_id'])
    
    pending_tasks = []
    for farm in farms:
        schedule = get_schedule_by_farm_id(str(farm['_id']))
        if schedule and 'tasks' in schedule:
            for task in schedule['tasks']:
                if task.get('status') == 'pending':
                    # Add task details and farm name
                    task_data = {
                        'task_id': task.get('id'),
                        'schedule_id': str(schedule['_id']),
                        'farm_id': str(farm['_id']),
                        'farm_name': farm.get('farm_name'),
                        'title': task.get('title'),
                        'description': task.get('description'),
                        'start_date': task.get('start_date'),
                        'due_date': task.get('due_date'),
                        'category': task.get('category')
                    }
                    pending_tasks.append(task_data)
    
    return jsonify({"tasks": pending_tasks}), 200

@app.route('/api/farm/layout', methods=['POST'])
def calculate_layout():
    # Get form data
    data = request.get_json()
    farm_width = float(data.get('farmWidth', 0))
    farm_length = float(data.get('farmLength', 0))
    plant_width_spacing = float(data.get('plantWidthSpacing', 1.8))
    plant_length_spacing = float(data.get('plantLengthSpacing', 2.4))
    
    # Calculate layout
    layout = calculate_farm_layout(farm_length, farm_width, plant_length_spacing, plant_width_spacing)
    
    # Get current date and appropriate activities
    activities = get_seasonal_activities(datetime.now())
    
    return jsonify({
        "layout": layout,
        "activities": activities
    })

@app.route('/api/weather/<location>')
def weather(location):
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        # Get latest weather from database
        weather_data = get_latest_weather(location)
        
        # If weather data is older than 1 hour or doesn't exist, fetch new data
        if not weather_data or (datetime.now() - weather_data['timestamp']).total_seconds() > 3600:
            print(f"Fetching new weather data for location: {location}")
            new_weather_data = get_weather_data(location)
            if new_weather_data:
                save_weather_data(location, new_weather_data)
                return jsonify(new_weather_data)
            else:
                print(f"Failed to fetch weather data for location: {location}")
                return jsonify({"error": f"Failed to fetch weather data for {location}"}), 500
        
        if weather_data:
            return jsonify(weather_data['data'])
        else:
            return jsonify({"error": "Weather data not available"}), 500
    except Exception as e:
        print(f"Error in weather API: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/weather')
def weather_by_coords():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        
        if not lat or not lon:
            return jsonify({"error": "Latitude and longitude are required"}), 400
        
        print(f"Fetching weather for coordinates: {lat}, {lon}")
        
        # Create a location key for database storage
        location_key = f"coords_{lat}_{lon}"
        
        # Get latest weather from database
        weather_data = get_latest_weather(location_key)
        
        # If weather data is older than 1 hour or doesn't exist, fetch new data
        if not weather_data or (datetime.now() - weather_data['timestamp']).total_seconds() > 3600:
            new_weather_data = get_weather_data_by_coords(lat, lon)
            if new_weather_data:
                print(f"Successfully fetched weather data for coordinates: {lat}, {lon}")
                # Update user's location in the database if reverse geocoding data is available
                if 'name' in new_weather_data:
                    user_id = session.get('user_id')
                    location_name = new_weather_data.get('name', '')
                    print(f"Updating user location to: {location_name}")
                    db.users.update_one(
                        {"_id": ObjectId(user_id)},
                        {"$set": {"location": location_name}}
                    )
                
                save_weather_data(location_key, new_weather_data)
                return jsonify(new_weather_data)
            else:
                print(f"Failed to fetch weather data for coordinates: {lat}, {lon}")
                return jsonify({"error": "Failed to fetch weather data for these coordinates"}), 500
        
        if weather_data:
            return jsonify(weather_data['data'])
        else:
            return jsonify({"error": "Weather data not available"}), 500
    except Exception as e:
        print(f"Error in weather by coords API: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    grape_variety = data.get('grape_variety')
    location = data.get('location')
    query = data.get('query', '')
    
    # Get recommendations from Gemini API (or placeholder)
    recommendation = get_gemini_recommendation(grape_variety, location, query)
    
    return jsonify({
        "recommendation": recommendation
    })

@app.route('/api/weather/insights', methods=['GET'])
def get_weather_insights():
    """Get farming insights based on current weather conditions using Gemini API"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user = get_user_by_id(session['user_id'])
        location = user.get('location', 'unknown location')
        
        # Get latest weather data for this user's location
        weather_data = get_latest_weather(location)
        
        if not weather_data or not weather_data.get('data'):
            return jsonify({"error": "Weather data not available"}), 404
        
        # Extract key weather information
        weather = weather_data['data']
        current_temp = weather['main']['temp']
        humidity = weather['main']['humidity']
        weather_condition = weather['weather'][0]['main'] if weather.get('weather') and len(weather['weather']) > 0 else "Unknown"
        weather_description = weather['weather'][0]['description'] if weather.get('weather') and len(weather['weather']) > 0 else "Unknown"
        
        # Construct a targeted prompt for Gemini API
        farming_prompt = f"""
        Based on these current weather conditions in {location}:
        - Temperature: {current_temp}°C
        - Weather: {weather_condition} ({weather_description})
        - Humidity: {humidity}%
        
        Provide a very brief (maximum 50 words) specific farming advice for grape cultivation. 
        Focus on immediate actions farmers should take considering these exact weather conditions.
        Be specific and actionable.
        """
        
        # Get insights from Gemini API
        import requests
        import json
        
        # Gemini API configuration
        api_key = os.getenv('GEMINI_API_KEY')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": farming_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 100
            }
        }
        
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Extract the generated text from the response
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                if "content" in response_data["candidates"][0]:
                    content = response_data["candidates"][0]["content"]
                    if "parts" in content and len(content["parts"]) > 0:
                        insight = content["parts"][0]["text"].strip()
                        return jsonify({"insight": insight})
        
        # Fallback responses based on weather conditions
        fallback_insights = {
            "Clear": "Clear skies are ideal for vineyard maintenance. Check for pests, ensure adequate sunlight exposure for all vines, and monitor moisture levels.",
            "Clouds": "Cloudy conditions reduce evaporation. Good time for light pruning and training. Monitor humidity levels to prevent fungal diseases.",
            "Rain": "Rainfall increases disease risk. Avoid walking in wet vineyards to prevent spreading pathogens. Check drainage systems and monitor for standing water.",
            "Drizzle": "Light moisture can benefit vines but watch for prolonged leaf wetness. Monitor for early signs of mildew or rot if humidity remains high.",
            "Thunderstorm": "After storms, check for physical damage to vines and trellises. Ensure proper drainage and watch for signs of disease over the next few days.",
            "Snow": "Protect vines from cold damage. Ensure drainage for melting snow and inspect for broken canes or trellis damage from snow weight.",
            "Mist": "Misty conditions increase disease pressure. Avoid unnecessary vineyard work and monitor for early signs of fungal infection.",
            "Fog": "Foggy conditions increase fungal disease risk. Delay spraying operations and minimize activity in the vineyard.",
            "Haze": "Reduced sunlight may slow ripening. Monitor vine health and consider adjusted harvest timing if conditions persist."
        }
        
        # Get a fallback insight based on the current weather condition
        fallback = fallback_insights.get(weather_condition, 
            "Monitor vineyard conditions closely. Adjust irrigation based on humidity and temperature. Check for signs of stress or disease.")
        
        return jsonify({"insight": fallback})
    
    except Exception as e:
        print(f"Error getting weather insights: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    


@app.route('/api/export-pdf/<farm_id>')
def export_pdf(farm_id):
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        # Get farm and schedule data
        farm = get_farm_by_id(farm_id)
        schedule = get_schedule_by_farm_id(farm_id)
        
        if not farm or not schedule:
            return jsonify({"error": "Farm or schedule not found"}), 404
        
        # Generate PDF using the updated function
        result = generate_pdf_plan(farm, schedule)
        
        if result['success']:
            return jsonify({
                "message": "PDF generated successfully", 
                "download_url": f"/download/pdf/{result['filename']}"
            })
        else:
            return jsonify({"error": result['message']}), 500
    
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500

@app.route('/download/pdf/<filename>')
def download_pdf(filename):
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        # Validate filename to prevent directory traversal attacks
        if '..' in filename or '/' in filename:
            return jsonify({"error": "Invalid filename"}), 400
        
        # Path to the PDF file
        pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'pdfs')
        
        if not os.path.exists(os.path.join(pdf_dir, filename)):
            return jsonify({"error": "PDF file not found"}), 404
            
        return send_from_directory(pdf_dir, filename, as_attachment=True)
    
    except Exception as e:
        print(f"PDF download error: {str(e)}")
        return jsonify({"error": f"Failed to download PDF: {str(e)}"}), 500
 


@app.route('/api/alerts/<alert_id>/read', methods=['PUT'])
def read_alert(alert_id):
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    success = mark_alert_as_read(alert_id)
    
    if success:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Failed to mark alert as read"}), 500

@app.route('/api/alerts/<alert_id>/delete', methods=['DELETE'])
def delete_alert_route(alert_id):
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    success = delete_alert(alert_id)
    
    if success:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Failed to delete alert"}), 500
    

@app.route('/notifications')
def notifications():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access your notifications', 'error')
        return redirect(url_for('login'))
    
    # Get user info
    user = get_user_by_id(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('login'))
    
    # Get all alerts for the user
    alerts = get_alerts_by_user(session['user_id'])
    
    return render_template(
        'notifications.html',
        user=user,
        alerts=alerts
    )
@app.route('/farm/<farm_id>/delete', methods=['POST'])
def delete_farm_route(farm_id):
    if 'user_id' not in session:
        flash('Please log in to delete a farm', 'error')
        return redirect(url_for('login'))
    
    # Get farm details to check if user owns it
    farm = get_farm_by_id(farm_id)
    if not farm:
        flash('Farm not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if user owns this farm
    if str(farm['user_id']) != session['user_id']:
        flash('Access denied: You do not own this farm', 'error')
        return redirect(url_for('dashboard'))
    
    # Delete the farm
    success = delete_farm(farm_id)
    
    if success:
        flash('Farm deleted successfully', 'success')
    else:
        flash('Error deleting farm', 'error')
    
    return redirect(url_for('dashboard'))

# Plant Notes API endpoints
# Plant Notes API endpoints
@app.route('/api/plant-notes/<farm_id>', methods=['GET'])
def get_plant_notes(farm_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    
    # Check if user owns this farm
    farm = get_farm_by_id(farm_id)
    if not farm or str(farm['user_id']) != session['user_id']:
        return jsonify({"success": False, "error": "Access denied"}), 403
    
    notes = get_plant_notes_by_farm(farm_id)
    return jsonify({"success": True, "notes": notes})

@app.route('/api/plant-notes/<farm_id>', methods=['POST'])
def create_plant_note_route(farm_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    
    # Check if user owns this farm
    farm = get_farm_by_id(farm_id)
    if not farm or str(farm['user_id']) != session['user_id']:
        return jsonify({"success": False, "error": "Access denied"}), 403
    
    data = request.json
    
    # Validate required fields
    required_fields = ['row', 'col', 'title', 'type', 'content']
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
    
    # Create the note
    note = create_plant_note(
        farm_id=farm_id,
        row=data['row'],
        col=data['col'],
        title=data['title'],
        type=data['type'],
        content=data['content']
    )
    
    return jsonify({"success": True, "note": note})

app.route('/api/plant-notes/<farm_id>/<note_id>', methods=['PUT'])
def update_plant_note_route(farm_id, note_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    
    # Check if user owns this farm
    farm = get_farm_by_id(farm_id)
    if not farm or str(farm['user_id']) != session['user_id']:
        return jsonify({"success": False, "error": "Access denied"}), 403
    
    # Check if note exists and belongs to this farm
    note = get_plant_note(note_id)
    if not note or str(note['farm_id']) != farm_id:
        return jsonify({"success": False, "error": "Note not found"}), 404
    
    data = request.json
    
    # Validate required fields
    required_fields = ['title', 'type', 'content']
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
    
    # Update the note
    updated_note = update_plant_note(
        note_id=note_id,
        title=data['title'],
        type=data['type'],
        content=data['content']
    )
    
    if updated_note:
        return jsonify({"success": True, "note": updated_note})
    else:
        return jsonify({"success": False, "error": "Failed to update note"}), 500

@app.route('/api/plant-notes/<farm_id>/<note_id>', methods=['DELETE'])
def delete_plant_note_route(farm_id, note_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    
    # Check if user owns this farm
    farm = get_farm_by_id(farm_id)
    if not farm or str(farm['user_id']) != session['user_id']:
        return jsonify({"success": False, "error": "Access denied"}), 403
    
    # Check if note exists and belongs to this farm
    note = get_plant_note(note_id)
    if not note or str(note['farm_id']) != farm_id:
        return jsonify({"success": False, "error": "Note not found"}), 404
    
    # Delete the note
    success = delete_plant_note(note_id)
    
    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Failed to delete note"}), 500



# Consultant Routes
@app.route('/consultant/login', methods=['GET', 'POST'])
def consultant_login():
    if 'consultant_id' in session:
        # If consultant is already logged in, redirect to dashboard
        return redirect(url_for('consultant_dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        consultant = authenticate_consultant(email, password)
        
        if consultant:
            session['consultant_id'] = str(consultant['_id'])
            session.pop('user_id', None)  # Ensure user session is cleared
            flash('Logged in successfully as consultant!', 'success')
            return redirect(url_for('consultant_dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('consultant_login.html')

@app.route('/consultant/signup', methods=['GET', 'POST'])
def consultant_signup():
    if 'consultant_id' in session:
        # If consultant is already logged in, redirect to dashboard
        return redirect(url_for('consultant_dashboard'))
        
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        location = request.form.get('location')
        specialization = request.form.get('specialization')
        experience = request.form.get('experience')
        
        # Check if consultant already exists
        if get_consultant_by_email(email):
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('consultant_login'))
        
        # Create new consultant
        consultant_id = create_consultant(name, email, password, phone, location, specialization, experience)
        
        if consultant_id:
            # Log consultant in
            session['consultant_id'] = consultant_id
            session.pop('user_id', None)  # Ensure user session is cleared
            flash('Consultant account created successfully!', 'success')
            return redirect(url_for('consultant_dashboard'))
        else:
            flash('Error creating account. Please try again.', 'error')
    
    return render_template('consultant_signup.html')

@app.route('/consultant/dashboard')
def consultant_dashboard():
    if 'consultant_id' not in session:
        flash('Please log in as a consultant to access the dashboard', 'error')
        return redirect(url_for('consultant_login'))
    
    # Get consultant info
    consultant = get_consultant_by_id(session['consultant_id'])
    if not consultant:
        session.pop('consultant_id', None)
        flash('Consultant not found. Please log in again.', 'error')
        return redirect(url_for('consultant_login'))
    
    # Get assigned farmers
    farmers = get_farmers_by_consultant(session['consultant_id'])
    
    # Add farm count to each farmer
    total_farms = 0
    for farmer in farmers:
        farms = get_farms_by_user(str(farmer['_id']))
        farmer['farm_count'] = len(farms)
        total_farms += len(farms)
    
    # Get recent comments made by this consultant
    pipeline = [
        {"$match": {"consultant_id": ObjectId(session['consultant_id'])}},
        {"$lookup": {
            "from": "farms",
            "localField": "farm_id",
            "foreignField": "_id",
            "as": "farm"
        }},
        {"$unwind": "$farm"},
        {"$lookup": {
            "from": "users",
            "localField": "farm.user_id",
            "foreignField": "_id",
            "as": "farmer"
        }},
        {"$unwind": "$farmer"},
        {"$project": {
            "content": 1,
            "created_at": 1,
            "farm_id": 1,
            "farm_name": "$farm.farm_name",
            "farmer_name": "$farmer.name",
        }},
        {"$sort": {"created_at": -1}},
        {"$limit": 5}
    ]
    
    recent_comments = list(db["comments"].aggregate(pipeline))
    
    return render_template(
        'consultant_dashboard.html',
        consultant=consultant,
        farmers=farmers,
        total_farms=total_farms,
        recent_comments=recent_comments
    )

@app.route('/consultant/profile')
def consultant_profile():
    if 'consultant_id' not in session:
        flash('Please log in as a consultant to access your profile', 'error')
        return redirect(url_for('consultant_login'))
    
    # Get consultant info
    consultant = get_consultant_by_id(session['consultant_id'])
    if not consultant:
        session.pop('consultant_id', None)
        flash('Consultant not found. Please log in again.', 'error')
        return redirect(url_for('consultant_login'))
    
    # You can expand this route to include profile editing functionality
    
    return render_template(
        'consultant_profile.html',
        consultant=consultant
    )

@app.route('/consultant/profile/update', methods=['POST'])
def update_consultant_profile():
    if 'consultant_id' not in session:
        flash('Please log in as a consultant to update your profile', 'error')
        return redirect(url_for('consultant_login'))
    
    # Get form data
    name = request.form.get('name')
    phone = request.form.get('phone')
    location = request.form.get('location')
    specialization = request.form.get('specialization')
    experience = request.form.get('experience')
    
    # Update consultant
    try:
        result = consultants_collection.update_one(
            {"_id": ObjectId(session['consultant_id'])},
            {"$set": {
                "name": name,
                "phone": phone,
                "location": location,
                "specialization": specialization,
                "experience": int(experience),
                "updated_at": datetime.now()
            }}
        )
        
        if result.modified_count > 0:
            flash('Profile updated successfully', 'success')
        else:
            flash('No changes made to profile', 'info')
    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'error')
    
    return redirect(url_for('consultant_profile'))

@app.route('/consultant/profile/change-password', methods=['POST'])
def change_consultant_password():
    if 'consultant_id' not in session:
        flash('Please log in as a consultant to change your password', 'error')
        return redirect(url_for('consultant_login'))
    
    # Get form data
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Verify passwords match
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('consultant_profile'))
    
    # Get consultant
    consultant = get_consultant_by_id(session['consultant_id'])
    if not consultant:
        session.pop('consultant_id', None)
        flash('Consultant not found. Please log in again.', 'error')
        return redirect(url_for('consultant_login'))
    
    # Verify current password
    if not check_password_hash(consultant['password'], current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('consultant_profile'))
    
    # Update password
    try:
        result = consultants_collection.update_one(
            {"_id": ObjectId(session['consultant_id'])},
            {"$set": {
                "password": generate_password_hash(new_password),
                "updated_at": datetime.now()
            }}
        )
        
        if result.modified_count > 0:
            flash('Password changed successfully', 'success')
        else:
            flash('Error changing password', 'error')
    except Exception as e:
        flash(f'Error changing password: {str(e)}', 'error')
    
    return redirect(url_for('consultant_profile'))

@app.route('/consultant/farmer/<user_id>')
def consultant_view_farmer(user_id):
    if 'consultant_id' not in session:
        flash('Please log in as a consultant to access farmer details', 'error')
        return redirect(url_for('consultant_login'))
    
    # Get consultant info
    consultant = get_consultant_by_id(session['consultant_id'])
    
    # Get farmer info - ensure we're using a string ID
    try:
        if not ObjectId.is_valid(user_id):
            flash('Invalid farmer ID', 'error')
            return redirect(url_for('consultant_dashboard'))
        
        farmer = get_user_by_id(user_id)
    except Exception as e:
        print(f"Error retrieving farmer: {str(e)}")
        flash('Error retrieving farmer data', 'error')
        return redirect(url_for('consultant_dashboard'))
    
    if not farmer:
        flash('Farmer not found', 'error')
        return redirect(url_for('consultant_dashboard'))
    
    # Check if this consultant is assigned to the farmer
    consultant_id_str = str(session['consultant_id'])
    farmer_consultant_id = str(farmer.get('consultant_id', '')) if farmer.get('consultant_id') else ''
    
    if not farmer_consultant_id or farmer_consultant_id != consultant_id_str:
        flash('Access denied: You are not assigned to this farmer', 'error')
        return redirect(url_for('consultant_dashboard'))
    
    # Get farmer's farms
    farms = get_farms_by_user(user_id)
    
    return render_template(
        'consultant_view_farmer.html',
        consultant=consultant,
        farmer=farmer,
        farms=farms
    )

@app.route('/consultant/farm/<farm_id>')
def consultant_view_farm(farm_id):
    if 'consultant_id' not in session:
        flash('Please log in as a consultant to access farm details', 'error')
        return redirect(url_for('consultant_login'))
    
    # Get consultant info
    consultant = get_consultant_by_id(session['consultant_id'])
    
    # Get farm details with extended info
    farm = get_farm_details_by_id(farm_id)
    if not farm:
        # If the detailed farm view fails, try getting basic farm info
        farm = get_farm_by_id(farm_id)
        if not farm:
            flash('Farm not found', 'error')
            return redirect(url_for('consultant_dashboard'))
    
    # Get farmer (user) info - handle both possible farm object structures
    user_id = farm.get('user_id', None)
    if user_id is None and '_id' in farm:
        # Try to get the basic farm info which should have user_id
        basic_farm = get_farm_by_id(farm['_id'])
        if basic_farm and 'user_id' in basic_farm:
            user_id = basic_farm['user_id']
    
    if not user_id:
        flash('Farm owner information not found', 'error')
        return redirect(url_for('consultant_dashboard'))
    
    # Convert user_id to string if it's an ObjectId
    if isinstance(user_id, ObjectId):
        user_id = str(user_id)
    
    farmer = get_user_by_id(user_id)
    if not farmer:
        flash('Farmer not found', 'error')
        return redirect(url_for('consultant_dashboard'))
    
    # Check if this consultant is assigned to the farmer
    if 'consultant_id' not in farmer or str(farmer['consultant_id']) != session['consultant_id']:
        flash('Access denied: You are not assigned to this farm', 'error')
        return redirect(url_for('consultant_dashboard'))
    
    # Get farm schedule
    schedule = get_schedule_by_farm_id(farm_id)
    
    # Ensure dates are serialized to strings (avoid strftime errors in template)
    if farm.get('created_at') and not isinstance(farm['created_at'], str):
        try:
            farm['created_at'] = farm['created_at'].strftime('%B %d, %Y')
        except:
            farm['created_at'] = str(farm['created_at'])
    
    if schedule:
        if schedule.get('planting_date') and not isinstance(schedule['planting_date'], str):
            try:
                schedule['planting_date'] = schedule['planting_date'].strftime('%B %d, %Y')
            except:
                schedule['planting_date'] = str(schedule['planting_date'])
        
        # Process task dates
        if 'tasks' in schedule:
            for task in schedule['tasks']:
                if 'due_date' in task and not isinstance(task['due_date'], str):
                    try:
                        task['due_date'] = task['due_date'].strftime('%b %d, %Y')
                    except:
                        task['due_date'] = str(task['due_date'])
    
    # Process comment dates
    comments = get_comments_by_farm(farm_id)
    for comment in comments:
        if 'created_at' in comment and not isinstance(comment['created_at'], str):
            try:
                comment['created_at'] = comment['created_at'].strftime('%b %d, %Y')
            except:
                comment['created_at'] = str(comment['created_at'])
    
    # Get layout data
    layout = calculate_farm_layout(
        farm['length'], 
        farm['width'], 
        farm['plant_spacing']['length'], 
        farm['plant_spacing']['width']
    )
    
    return render_template(
        'consultant_view_farm.html',
        consultant=consultant,
        farm=farm,
        farmer=farmer,
        schedule=schedule,
        layout=layout,
        comments=comments
    )

@app.route('/consultant/farm/<farm_id>/comment', methods=['POST'])
def add_comment(farm_id):
    if 'consultant_id' not in session:
        flash('Please log in as a consultant to add comments', 'error')
        return redirect(url_for('consultant_login'))
    
    # Get content from form
    content = request.form.get('content')
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('consultant_view_farm', farm_id=farm_id))
    
    # Verify farm exists
    farm = get_farm_by_id(farm_id)
    if not farm:
        flash('Farm not found', 'error')
        return redirect(url_for('consultant_dashboard'))
    
    # Verify farmer has assigned this consultant
    user_id = str(farm['user_id']) if isinstance(farm['user_id'], ObjectId) else farm['user_id']
    farmer = get_user_by_id(user_id)
    
    if not farmer:
        flash('Farmer not found', 'error')
        return redirect(url_for('consultant_dashboard'))
    
    consultant_id_str = str(session['consultant_id'])
    farmer_consultant_id = str(farmer.get('consultant_id', '')) if farmer.get('consultant_id') else ''
    
    if not farmer_consultant_id or farmer_consultant_id != consultant_id_str:
        flash('Access denied: You are not assigned to this farm', 'error')
        return redirect(url_for('consultant_dashboard'))
    
    # Create comment
    try:
        comment = create_comment(farm_id, session['consultant_id'], content)
        
        if comment:
            flash('Comment added successfully', 'success')
        else:
            flash('Error adding comment', 'error')
    except Exception as e:
        print(f"Error adding comment: {str(e)}")
        flash('Error adding comment', 'error')
    
    return redirect(url_for('consultant_view_farm', farm_id=farm_id))

# Farmer Select Consultant routes
@app.route('/select-consultant')
def select_consultant():
    if 'user_id' not in session:
        flash('Please log in to select a consultant', 'error')
        return redirect(url_for('login'))
    
    # Get user info
    user = get_user_by_id(session['user_id'])
    
    # Get filter parameters
    location = request.args.get('location', '')
    specialization = request.args.get('specialization', '')
    experience = request.args.get('experience', '')
    
    # Build query
    query = {}
    if location:
        query['location'] = location
    if specialization:
        query['specialization'] = specialization
    if experience:
        try:
            query['experience'] = {'$gte': int(experience)}
        except ValueError:
            pass
    
    # Get consultants based on filters
    if query:
        consultants = list(db['consultants'].find(query))
    else:
        consultants = get_all_consultants()
    
    # Get unique locations and specializations for filtering
    locations = list(db['consultants'].distinct('location'))
    specializations = list(db['consultants'].distinct('specialization'))
    
    return render_template(
        'select_consultant.html',
        user=user,
        consultants=consultants,
        locations=locations,
        specializations=specializations,
        request=request
    )

@app.route('/assign-consultant/<consultant_id>', methods=['POST'])
def assign_consultant(consultant_id):
    if 'user_id' not in session:
        flash('Please log in to select a consultant', 'error')
        return redirect(url_for('login'))
    
    # Check if consultant exists
    consultant = get_consultant_by_id(consultant_id)
    if not consultant:
        flash('Consultant not found', 'error')
        return redirect(url_for('select_consultant'))
    
    # Assign consultant to farmer
    if assign_consultant_to_farmer(session['user_id'], consultant_id):
        flash(f'Successfully assigned {consultant["name"]} as your consultant', 'success')
    else:
        flash('Error assigning consultant', 'error')
    
    return redirect(url_for('dashboard'))

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(KeyError)
def handle_key_error(e):
    # Log the error
    app.logger.error(f"KeyError: {str(e)}")
    # Return a user-friendly error message
    flash(f"An error occurred accessing data: {str(e)}", "error")
    return redirect(url_for('index')), 302

# Function to check and generate notifications for upcoming tasks
def check_upcoming_tasks():
    """
    Check for upcoming tasks and generate notifications
    This function can be scheduled to run periodically using a task scheduler
    """
    print("Checking for upcoming tasks...")
    # Get all users
    users = list(db.users.find({}))
    
    for user in users:
        user_id = str(user['_id'])
        # Get user's farms
        farms = get_farms_by_user(user_id)
        
        for farm in farms:
            farm_id = str(farm['_id'])
            # Get farm schedule
            schedule = get_schedule_by_farm_id(farm_id)
            
            if schedule and 'tasks' in schedule:
                # Check for upcoming tasks in the next 3 days
                upcoming_date = datetime.now() + timedelta(days=3)
                
                for task in schedule['tasks']:
                    if task.get('status') == 'pending':
                        try:
                            due_date = datetime.strptime(task.get('due_date'), '%Y-%m-%d')
                            # If task is due within 3 days and no alert exists for it
                            if due_date <= upcoming_date and due_date >= datetime.now():
                                # Check if notification already exists for this task
                                existing_alert = db.alerts.find_one({
                                    "user_id": ObjectId(user_id),
                                    "farm_id": ObjectId(farm_id),
                                    "type": "task_reminder",
                                    "message": {'$regex': task.get('title')}
                                })
                                
                                if not existing_alert:
                                    # Create notification
                                    create_alert(
                                        user_id,
                                        farm_id,
                                        f"Upcoming task reminder: {task.get('title')} for {farm.get('farm_name')} due on {task.get('due_date')}",
                                        "task_reminder",
                                        due_date
                                    )
                                    print(f"Created notification for task: {task.get('title')}")
                        except (ValueError, TypeError) as e:
                            print(f"Error processing task date: {e}")
    
    print("Finished checking upcoming tasks")



# Initialize database and load sample data
init_db()

# Check if products exist, if not load sample data
if products_collection.count_documents({}) == 0:
    print("No products found. Loading sample data...")
    load_sample_data()

# Helper function to get cart from session
def get_cart():
    if 'cart' not in session:
        session['cart'] = {}
    return session['cart']

def get_cart_count():
    return sum(item['quantity'] for item in session.get('cart', {}).values())

@app.route('/shop')
def shop():
    # Get recommended products (highest rated)
    recommended_products = list(products_collection.find().sort('rating', -1).limit(8))
    
    # Get featured products (random selection)
    featured_products = list(products_collection.aggregate([
        {'$sample': {'size': 4}}
    ]))
    
    return render_template(
        'index.html',
        recommended_products=recommended_products,
        featured_products=featured_products,
        cart_count=get_cart_count(),
        now=datetime.now()
    )


@app.route('/products')
def products():
    # Get filter parameters
    category = request.args.get('category')
    min_price = float(request.args.get('min_price', 0))
    max_price = float(request.args.get('max_price', 10000))
    search = request.args.get('search', '')
    
    # Build query based on filters
    query = {
        'price': {'$gte': min_price, '$lte': max_price}
    }
    
    if category:
        query['category'] = category
    
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    
    products = list(products_collection.find(query))
    
    # Get unique categories for filter
    categories = products_collection.distinct('category')
    
    return render_template(
        'products.html',
        products=products,
        categories=categories,
        selected_category=category,
        min_price=min_price,
        max_price=max_price,
        search=search,
        cart_count=get_cart_count(),
        now=datetime.now()
    )

@app.route('/product/<product_id>')
def product_detail(product_id):
    try:
        product = get_product_by_id(product_id)
        
        if not product:
            flash('Product not found')
            return redirect(url_for('products'))
        
        # Get product reviews
        reviews = get_reviews_by_product(product_id)
        
        # Get recommended products (same category)
        recommended_products = list(products_collection.find({
            'category': product['category'],
            '_id': {'$ne': ObjectId(product_id)}
        }).limit(4))
        
        return render_template(
            'product_detail.html',
            product=product,
            reviews=reviews,
            recommended_products=recommended_products,
            cart_count=get_cart_count(),
            now=datetime.now()
        )
    except:
        flash('Invalid product ID')
        return redirect(url_for('products'))

@app.route('/cart')
def cart():
    cart = get_cart()
    cart_items = []
    subtotal = 0
    
    if cart:
        for product_id, item in cart.items():
            product = get_product_by_id(product_id)
            
            if product:
                quantity = item.get('quantity', 1)
                item_total = product['price'] * quantity
                subtotal += item_total
                
                cart_items.append({
                    '_id': product['_id'],
                    'name': product['name'],
                    'price': product['price'],
                    'image': product['image'],
                    'quantity': quantity,
                    'item_total': item_total
                })
    
    shipping = 10 if subtotal > 0 else 0
    total = subtotal + shipping
    
    return render_template(
        'cart.html',
        cart_items=cart_items,
        subtotal=subtotal,
        shipping=shipping,
        total=total,
        cart_count=get_cart_count(),
        now=datetime.now()
    )

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Process checkout (in a real app, you'd handle payment here)
        session['cart'] = {}
        flash('Order placed successfully!')
        return redirect(url_for('order_confirmation'))
    
    cart = get_cart()
    cart_items = []
    subtotal = 0
    
    if not cart:
        flash('Your cart is empty')
        return redirect(url_for('cart'))
    
    for product_id, item in cart.items():
        product = get_product_by_id(product_id)
        
        if product:
            quantity = item.get('quantity', 1)
            item_total = product['price'] * quantity
            subtotal += item_total
            
            cart_items.append({
                '_id': product['_id'],
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'quantity': quantity,
                'item_total': item_total
            })
    
    shipping = 10 if subtotal > 0 else 0
    total = subtotal + shipping
    
    return render_template(
        'checkout.html',
        cart_items=cart_items,
        subtotal=subtotal,
        shipping=shipping,
        total=total,
        cart_count=get_cart_count(),
        now=datetime.now()
    )

@app.route('/order-confirmation')
def order_confirmation():
    return render_template(
        'order_confirmation.html',
        cart_count=get_cart_count(),
        now=datetime.now()
    )

@app.route('/add-to-cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = get_cart()
    quantity = int(request.form.get('quantity', 1))
    
    if product_id in cart:
        cart[product_id]['quantity'] += quantity
    else:
        cart[product_id] = {'quantity': quantity}
    
    session['cart'] = cart
    flash('Product added to cart!')
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/update-cart/<product_id>', methods=['POST'])
def update_cart(product_id):
    cart = get_cart()
    quantity = int(request.form.get('quantity', 1))
    
    if quantity > 0:
        cart[product_id]['quantity'] = quantity
    else:
        del cart[product_id]
    
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/remove-from-cart/<product_id>')
def remove_from_cart(product_id):
    cart = get_cart()
    
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart
    
    return redirect(url_for('cart'))

@app.route('/add-review/<product_id>', methods=['POST'])
def add_review(product_id):
    if 'user_id' not in session:
        flash('Please login to add a review')
       
    
    try:
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment')
        
        if not rating or rating < 1 or rating > 5:
            flash('Please select a valid rating')
            return redirect(url_for('product_detail', product_id=product_id))
        
        if not comment.strip():
            flash('Please write a review comment')
            return redirect(url_for('product_detail', product_id=product_id))
        
        # Create review document
        review_data = {
            'product_id': ObjectId(product_id),
            'user_id': ObjectId(session['user_id']),
            'rating': rating,
            'comment': comment,
            'created_at': datetime.utcnow()
        }
        
        # Insert review
        reviews_collection.insert_one(review_data)
        
        # Update product rating
        reviews = list(reviews_collection.find({'product_id': ObjectId(product_id)}))
        if reviews:
            avg_rating = sum(review['rating'] for review in reviews) / len(reviews)
            products_collection.update_one(
                {'_id': ObjectId(product_id)},
                {
                    '$set': {
                        'rating': avg_rating,
                        'review_count': len(reviews)
                    }
                }
            )
        
        flash('Review added successfully!')
        return redirect(url_for('product_detail', product_id=product_id))
        
    except Exception as e:
        print(f"Error adding review: {e}")
        flash('An error occurred while adding your review')
        return redirect(url_for('product_detail', product_id=product_id))
    




if __name__ == '__main__':
    # Get port from environment variable for Render deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)