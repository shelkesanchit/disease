from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import json
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Custom JSON encoder for MongoDB ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

# Helper function to convert MongoDB documents to JSON-serializable format
def serialize_mongo_doc(doc):
    """Convert MongoDB document to JSON-serializable format."""
    if not doc:
        return None
    
    # Convert ObjectId fields to strings
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    
    if "farm_id" in doc and isinstance(doc["farm_id"], ObjectId):
        doc["farm_id"] = str(doc["farm_id"])
    
    if "user_id" in doc and isinstance(doc["user_id"], ObjectId):
        doc["user_id"] = str(doc["user_id"])
    
    return doc

# MongoDB Connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client["farm_planner"]

# Collections
users_collection = db["users"]
consultants_collection = db["consultants"]
farms_collection = db["farms"]
schedules_collection = db["schedules"]
grape_varieties_collection = db["grape_varieties"]
tasks_collection = db["tasks"]
weather_data_collection = db["weather_data"]
alerts_collection = db["alerts"]
plant_notes_collection = db["plant_notes"]
comments_collection = db["comments"]

# Initialize grape varieties if not exists
def init_grape_varieties():
    if grape_varieties_collection.count_documents({}) == 0:
        varieties = [
            {
                "name": "Thompson Seedless",
                "type": "Table",
                "growing_period": "110-130 days",
                "recommended_spacing": {"width": 1.8, "length": 2.4},
                "climate_preference": "Warm, dry",
                "disease_resistance": "Medium",
                "fertilizer_recommendations": {
                    "npk_ratio": "20-10-20",
                    "schedule": "Monthly during growing season"
                }
            },
            {
                "name": "Flame Seedless",
                "type": "Table",
                "growing_period": "100-120 days",
                "recommended_spacing": {"width": 1.8, "length": 2.4},
                "climate_preference": "Hot, dry",
                "disease_resistance": "Medium",
                "fertilizer_recommendations": {
                    "npk_ratio": "16-16-16",
                    "schedule": "Every 6 weeks"
                }
            },
            {
                "name": "Crimson Seedless",
                "type": "Table",
                "growing_period": "120-140 days",
                "recommended_spacing": {"width": 2.0, "length": 2.5},
                "climate_preference": "Warm, moderate humidity",
                "disease_resistance": "Medium-High",
                "fertilizer_recommendations": {
                    "npk_ratio": "15-15-15",
                    "schedule": "Monthly during growing season"
                }
            },
            {
                "name": "Concord",
                "type": "Wine/Juice",
                "growing_period": "160-180 days",
                "recommended_spacing": {"width": 2.4, "length": 3.0},
                "climate_preference": "Cool to moderate",
                "disease_resistance": "High",
                "fertilizer_recommendations": {
                    "npk_ratio": "10-10-10",
                    "schedule": "Spring and mid-summer"
                }
            },
            {
                "name": "Moon Drops",
                "type": "Table",
                "growing_period": "110-130 days",
                "recommended_spacing": {"width": 2.0, "length": 2.4},
                "climate_preference": "Moderate",
                "disease_resistance": "Medium",
                "fertilizer_recommendations": {
                    "npk_ratio": "18-6-12",
                    "schedule": "Every 8 weeks"
                }
            },
            {
                "name": "Black Corinth",
                "type": "Table/Drying",
                "growing_period": "90-110 days",
                "recommended_spacing": {"width": 1.5, "length": 2.0},
                "climate_preference": "Mediterranean",
                "disease_resistance": "Medium",
                "fertilizer_recommendations": {
                    "npk_ratio": "12-12-12",
                    "schedule": "Every 2 months"
                }
            },
            {
                "name": "Red Globe",
                "type": "Table",
                "growing_period": "140-160 days",
                "recommended_spacing": {"width": 2.0, "length": 2.5},
                "climate_preference": "Hot, dry",
                "disease_resistance": "Medium-Low",
                "fertilizer_recommendations": {
                    "npk_ratio": "13-13-21",
                    "schedule": "Every 4 weeks"
                }
            },
            {
                "name": "Autumn Royal",
                "type": "Table",
                "growing_period": "130-150 days",
                "recommended_spacing": {"width": 2.0, "length": 2.5},
                "climate_preference": "Warm to hot",
                "disease_resistance": "Medium",
                "fertilizer_recommendations": {
                    "npk_ratio": "15-5-20",
                    "schedule": "Monthly"
                }
            },
            {
                "name": "Sultana",
                "type": "Table/Drying",
                "growing_period": "110-130 days",
                "recommended_spacing": {"width": 1.8, "length": 2.2},
                "climate_preference": "Hot, dry",
                "disease_resistance": "Low",
                "fertilizer_recommendations": {
                    "npk_ratio": "12-12-17",
                    "schedule": "6-8 week intervals"
                }
            }
        ]
        
        grape_varieties_collection.insert_many(varieties)

# User model functions
def create_user(name, email, password, phone, location, preferred_grape):
    """Create a new user in the database"""
    if users_collection.find_one({"email": email}):
        return False
    
    user = {
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
        "phone": phone,
        "location": location,
        "preferred_grape": preferred_grape,
        "created_at": datetime.now(),
        "last_login": datetime.now()
    }
    
    result = users_collection.insert_one(user)
    return str(result.inserted_id)

def authenticate_user(email, password):
    """Authenticate a user"""
    user = users_collection.find_one({"email": email})
    if user and check_password_hash(user["password"], password):
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.now()}}
        )
        return user
    return None

def get_user_by_id(user_id):
    """Get user by ID"""
    return users_collection.find_one({"_id": ObjectId(user_id)})

def get_user_by_email(email):
    """Get user by email"""
    return users_collection.find_one({"email": email})

# Consultant model functions
def create_consultant(name, email, password, phone, location, specialization, experience):
    """Create a new consultant in the database"""
    if consultants_collection.find_one({"email": email}):
        return False
    
    consultant = {
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
        "phone": phone,
        "location": location,
        "specialization": specialization,
        "experience": experience,
        "created_at": datetime.now(),
        "last_login": datetime.now()
    }
    
    result = consultants_collection.insert_one(consultant)
    return str(result.inserted_id)

def authenticate_consultant(email, password):
    """Authenticate a consultant"""
    consultant = consultants_collection.find_one({"email": email})
    if consultant and check_password_hash(consultant["password"], password):
        consultants_collection.update_one(
            {"_id": consultant["_id"]},
            {"$set": {"last_login": datetime.now()}}
        )
        return consultant
    return None

def get_consultant_by_id(consultant_id):
    """Get consultant by ID"""
    return consultants_collection.find_one({"_id": ObjectId(consultant_id)})

def get_consultant_by_email(email):
    """Get consultant by email"""
    return consultants_collection.find_one({"email": email})

def get_consultants_by_location(location):
    """Get all consultants in a specific location"""
    return list(consultants_collection.find({"location": location}))

def get_all_consultants():
    """Get all consultants"""
    return list(consultants_collection.find({}))

# Farm model functions
def create_farm(user_id, farm_name, length, width, grape_variety, plant_spacing):
    """Create a new farm for a user"""
    farm = {
        "user_id": ObjectId(user_id),
        "farm_name": farm_name,
        "length": length,
        "width": width,
        "grape_variety": grape_variety,
        "plant_spacing": plant_spacing,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    result = farms_collection.insert_one(farm)
    return str(result.inserted_id)

def delete_farm(farm_id):
    """Delete a farm by ID"""
    # First, get the farm to check if it exists
    farm = farms_collection.find_one({"_id": ObjectId(farm_id)})
    if not farm:
        return False
    
    # Delete the farm
    result = farms_collection.delete_one({"_id": ObjectId(farm_id)})
    
    # Delete any associated schedules
    if result.deleted_count > 0:
        schedules_collection.delete_many({"farm_id": ObjectId(farm_id)})
        
    return result.deleted_count > 0

def get_farms_by_user(user_id):
    """Get all farms for a user"""
    return list(farms_collection.find({"user_id": ObjectId(user_id)}))

def get_farm_by_id(farm_id):
    """Get farm by ID"""
    return farms_collection.find_one({"_id": ObjectId(farm_id)})

# Schedule model functions
def create_schedule(farm_id, planting_date, tasks, end_date=None):
    """Create a farming schedule"""
    schedule = {
        "farm_id": ObjectId(farm_id),
        "planting_date": planting_date,
        "end_date": end_date,
        "tasks": tasks,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    result = schedules_collection.insert_one(schedule)
    return str(result.inserted_id)

def get_schedule_by_farm_id(farm_id):
    """Get schedule by farm ID"""
    return schedules_collection.find_one({"farm_id": ObjectId(farm_id)})

def update_task_status(schedule_id, task_id, status):
    """Update task status"""
    result = schedules_collection.update_one(
        {"_id": ObjectId(schedule_id), "tasks.id": task_id},
        {"$set": {"tasks.$.status": status, "updated_at": datetime.now()}}
    )
    
    return result.modified_count > 0

# Weather data functions
def save_weather_data(location, data):
    """Save weather data for a location"""
    weather = {
        "location": location,
        "data": data,
        "timestamp": datetime.now()
    }
    
    result = weather_data_collection.insert_one(weather)
    return str(result.inserted_id)

def get_latest_weather(location):
    """Get latest weather data for a location"""
    return weather_data_collection.find_one(
        {"location": location},
        sort=[("timestamp", -1)]
    )

# Alert functions
def create_alert(user_id, farm_id, message, type, date):
    """Create a new alert"""
    alert = {
        "user_id": ObjectId(user_id),
        "farm_id": ObjectId(farm_id) if farm_id else None,
        "message": message,
        "type": type,
        "date": date,
        "is_read": False,
        "created_at": datetime.now()
    }
    
    result = alerts_collection.insert_one(alert)
    return str(result.inserted_id)

def get_alerts_by_user(user_id):
    """Get all alerts for a user"""
    return list(alerts_collection.find(
        {"user_id": ObjectId(user_id)},
        sort=[("created_at", -1)]
    ))

def mark_alert_as_read(alert_id):
    """Mark an alert as read"""
    result = alerts_collection.update_one(
        {"_id": ObjectId(alert_id)},
        {"$set": {"is_read": True}}
    )
    
    return result.modified_count > 0

def delete_alert(alert_id):
    """Delete an alert from the database"""
    result = alerts_collection.delete_one(
        {"_id": ObjectId(alert_id)}
    )
    
    return result.deleted_count > 0

# Plant Note functions
def create_plant_note(farm_id, row, col, title, type, content):
    """Create a new plant note"""
    note = {
        "farm_id": ObjectId(farm_id),
        "row": row,
        "col": col,
        "title": title,
        "type": type,
        "content": content,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    result = plant_notes_collection.insert_one(note)
    note["_id"] = result.inserted_id
    return serialize_mongo_doc(note)

def get_plant_notes_by_farm(farm_id):
    """Get all plant notes for a farm"""
    notes = list(plant_notes_collection.find({"farm_id": ObjectId(farm_id)}))
    
    # Convert to JSON serializable format
    serialized_notes = [serialize_mongo_doc(note) for note in notes]
    
    return serialized_notes

def get_plant_note(note_id):
    """Get a plant note by ID"""
    note = plant_notes_collection.find_one({"_id": ObjectId(note_id)})
    return serialize_mongo_doc(note)

def update_plant_note(note_id, title, type, content):
    """Update a plant note"""
    result = plant_notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {
            "$set": {
                "title": title,
                "type": type,
                "content": content,
                "updated_at": datetime.now()
            }
        }
    )
    
    if result.modified_count > 0:
        return get_plant_note(note_id)
    
    return None

def delete_plant_note(note_id):
    """Delete a plant note"""
    result = plant_notes_collection.delete_one({"_id": ObjectId(note_id)})
    return result.deleted_count > 0

# Grape variety functions
def get_grape_varieties():
    """Get all grape varieties"""
    return list(grape_varieties_collection.find({}))

def get_variety_info(variety_name):
    """Get detailed info for a specific grape variety"""
    return grape_varieties_collection.find_one({"name": variety_name})

# Comment functions
def create_comment(farm_id, consultant_id, content):
    """Create a new comment on a farm by a consultant"""
    comment = {
        "farm_id": ObjectId(farm_id),
        "consultant_id": ObjectId(consultant_id),
        "content": content,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    result = comments_collection.insert_one(comment)
    comment["_id"] = str(result.inserted_id)
    return serialize_mongo_doc(comment)

def get_comments_by_farm(farm_id):
    """Get all comments for a specific farm"""
    pipeline = [
        {"$match": {"farm_id": ObjectId(farm_id)}},
        {"$lookup": {
            "from": "consultants",
            "localField": "consultant_id",
            "foreignField": "_id",
            "as": "consultant"
        }},
        {"$unwind": "$consultant"},
        {"$project": {
            "_id": 1,
            "farm_id": 1,
            "consultant_id": 1,
            "content": 1,
            "created_at": 1,
            "updated_at": 1,
            "consultant_name": "$consultant.name"
        }}
    ]
    
    comments = list(comments_collection.aggregate(pipeline))
    return [serialize_mongo_doc(comment) for comment in comments]

def update_comment(comment_id, content):
    """Update a comment"""
    result = comments_collection.update_one(
        {"_id": ObjectId(comment_id)},
        {
            "$set": {
                "content": content,
                "updated_at": datetime.now()
            }
        }
    )
    
    return result.modified_count > 0

def delete_comment(comment_id):
    """Delete a comment"""
    result = comments_collection.delete_one({"_id": ObjectId(comment_id)})
    return result.deleted_count > 0

# User model functions - add consultant relationship
def assign_consultant_to_farmer(user_id, consultant_id):
    """Assign a consultant to a farmer"""
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"consultant_id": ObjectId(consultant_id)}}
    )
    
    return result.modified_count > 0

def get_farmers_by_consultant(consultant_id):
    """Get all farmers assigned to a specific consultant"""
    return list(users_collection.find({"consultant_id": ObjectId(consultant_id)}))

# Update Farm model function to include additional info
def get_farm_details_by_id(farm_id):
    """Get farm by ID with additional details like comments and user info"""
    pipeline = [
        {"$match": {"_id": ObjectId(farm_id)}},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user"
        }},
        {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {
            "from": "comments",
            "localField": "_id",
            "foreignField": "farm_id",
            "as": "comments"
        }},
        {"$project": {
            "_id": 1,
            "farm_name": 1,
            "length": 1,
            "width": 1,
            "grape_variety": 1,
            "plant_spacing": 1,
            "created_at": 1,
            "updated_at": 1,
            "user_id": 1,  # Explicitly include the user_id field
            "user_name": {"$ifNull": ["$user.name", "Unknown"]},
            "user_location": {"$ifNull": ["$user.location", "Unknown"]},
            "comments": 1
        }}
    ]
    
    try:
        farm = next(farms_collection.aggregate(pipeline), None)
        return serialize_mongo_doc(farm) if farm else None
    except Exception as e:
        print(f"Error in get_farm_details_by_id: {str(e)}")
        return None

# Initialize database
init_grape_varieties() 