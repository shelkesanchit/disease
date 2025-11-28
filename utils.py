import requests
import json
from datetime import datetime, timedelta
import calendar
import math
import random
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenWeather API - Fetch weather data based on location
def get_weather_data(city):
    """Fetch weather data from OpenWeather API using city name"""
    API_KEY = os.getenv('OPENWEATHER_API_KEY')
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# OpenWeather API - Fetch weather data based on coordinates
def get_weather_data_by_coords(lat, lon):
    """Fetch weather data from OpenWeather API using coordinates"""
    API_KEY = os.getenv('OPENWEATHER_API_KEY')
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to generate a farming timeline based on grape variety and planting date
def generate_farming_timeline(grape_variety, planting_date, location=None):
    """Generate a comprehensive farming timeline based on grape variety and planting date"""
    # Convert planting_date string to datetime object if needed
    if isinstance(planting_date, str):
        planting_date = datetime.strptime(planting_date, "%Y-%m-%d")
    
    # Basic structure for a farming timeline
    timeline = []
    task_id = 0
    
    # Year 1 timeline
    # Pre-planting and planting phase (Month 0-1)
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Soil Testing",
        "description": "Conduct soil pH test, check nutrient levels",
        "category": "preparation",
        "start_date": (planting_date - timedelta(days=14)).strftime("%Y-%m-%d"),
        "due_date": (planting_date - timedelta(days=10)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Land Preparation",
        "description": "Deep plowing, leveling, and adding organic matter",
        "category": "preparation",
        "start_date": (planting_date - timedelta(days=10)).strftime("%Y-%m-%d"),
        "due_date": (planting_date - timedelta(days=3)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Install Irrigation System",
        "description": "Set up drip irrigation system for water efficiency",
        "category": "preparation",
        "start_date": (planting_date - timedelta(days=7)).strftime("%Y-%m-%d"),
        "due_date": (planting_date - timedelta(days=1)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Planting Day",
        "description": f"Plant {grape_variety} vines with proper spacing",
        "category": "planting",
        "start_date": planting_date.strftime("%Y-%m-%d"),
        "due_date": planting_date.strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    # Early Establishment Phase (Months 1-3)
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Deep Watering",
        "description": "Provide 10-15 liters per plant",
        "category": "water",
        "start_date": planting_date.strftime("%Y-%m-%d"),
        "due_date": (planting_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Apply Mulch",
        "description": "Apply organic mulch around plants to retain moisture",
        "category": "soil",
        "start_date": (planting_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        "due_date": (planting_date + timedelta(days=3)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Regular Watering",
        "description": "Water every 3-4 days (5-10 liters per vine)",
        "category": "water",
        "start_date": (planting_date + timedelta(days=3)).strftime("%Y-%m-%d"),
        "due_date": (planting_date + timedelta(days=30)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "First Fertilization",
        "description": "Apply NPK 10-10-10 (half dose)",
        "category": "fertilize",
        "start_date": (planting_date + timedelta(days=10)).strftime("%Y-%m-%d"),
        "due_date": (planting_date + timedelta(days=10)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    # Support Setup Phase (Months 3-4)
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Install Trellis System",
        "description": "Set up wooden posts with wires for vine training",
        "category": "structure",
        "start_date": (planting_date + timedelta(days=30)).strftime("%Y-%m-%d"),
        "due_date": (planting_date + timedelta(days=45)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Shoot Training",
        "description": "Train primary shoots onto trellis",
        "category": "training",
        "start_date": (planting_date + timedelta(days=45)).strftime("%Y-%m-%d"),
        "due_date": (planting_date + timedelta(days=60)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    # First Year Growth Management (Months 4-12)
    for month in range(4, 13):
        # Adjust water frequency based on season
        if 6 <= month <= 9:  # Summer/Monsoon
            water_days = "7-10"
            water_amount = "10-12"
        else:  # Other seasons
            water_days = "10-14"
            water_amount = "8-10"
            
        timeline.append({
            "id": str(task_id := task_id + 1),
            "title": f"Month {month} Watering",
            "description": f"Water every {water_days} days ({water_amount} liters per vine)",
            "category": "water",
            "start_date": (planting_date + timedelta(days=30*(month-1))).strftime("%Y-%m-%d"),
            "due_date": (planting_date + timedelta(days=30*month)).strftime("%Y-%m-%d"),
            "status": "pending"
        })
        
        # Seasonal pruning and fertilization
        if month == 6:  # Early summer pruning
            timeline.append({
                "id": str(task_id := task_id + 1),
                "title": "First Summer Pruning",
                "description": "Remove extra shoots, keeping only 2-3 strongest",
                "category": "prune",
                "start_date": (planting_date + timedelta(days=30*5 + 15)).strftime("%Y-%m-%d"),
                "due_date": (planting_date + timedelta(days=30*5 + 20)).strftime("%Y-%m-%d"),
                "status": "pending"
            })
        
        if month == 7:  # Mid-summer fertilization
            timeline.append({
                "id": str(task_id := task_id + 1),
                "title": "Summer Fertilization",
                "description": "Apply NPK 10-10-10 (full dose) + micronutrients",
                "category": "fertilize",
                "start_date": (planting_date + timedelta(days=30*6 + 10)).strftime("%Y-%m-%d"),
                "due_date": (planting_date + timedelta(days=30*6 + 15)).strftime("%Y-%m-%d"),
                "status": "pending"
            })
            
        if month == 8:  # Pest control in monsoon
            timeline.append({
                "id": str(task_id := task_id + 1),
                "title": "Pest Control",
                "description": "Spray neem oil or organic insecticides",
                "category": "pest",
                "start_date": (planting_date + timedelta(days=30*7 + 5)).strftime("%Y-%m-%d"),
                "due_date": (planting_date + timedelta(days=30*7 + 10)).strftime("%Y-%m-%d"),
                "status": "pending"
            })
            
        if month == 11:  # Winter pruning
            timeline.append({
                "id": str(task_id := task_id + 1),
                "title": "Winter Pruning",
                "description": "Prune back vines to shape for next year",
                "category": "prune",
                "start_date": (planting_date + timedelta(days=30*10 + 10)).strftime("%Y-%m-%d"),
                "due_date": (planting_date + timedelta(days=30*10 + 15)).strftime("%Y-%m-%d"),
                "status": "pending"
            })
            
            timeline.append({
                "id": str(task_id := task_id + 1),
                "title": "Winter Fertilization",
                "description": "Apply potassium-based fertilizer for winter hardiness",
                "category": "fertilize",
                "start_date": (planting_date + timedelta(days=30*10 + 20)).strftime("%Y-%m-%d"),
                "due_date": (planting_date + timedelta(days=30*10 + 25)).strftime("%Y-%m-%d"),
                "status": "pending"
            })
    
    # Year 2 Timeline (key events only)
    year2_start = planting_date.replace(year=planting_date.year + 1)
    
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Year 2 - Winter Pruning",
        "description": "Remove weak and overcrowded branches",
        "category": "prune",
        "start_date": (year2_start + timedelta(days=15)).strftime("%Y-%m-%d"),
        "due_date": (year2_start + timedelta(days=20)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Year 2 - Spring Fertilization",
        "description": "Apply NPK 15-15-15 + organic manure",
        "category": "fertilize",
        "start_date": (year2_start + timedelta(days=30)).strftime("%Y-%m-%d"),
        "due_date": (year2_start + timedelta(days=35)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Year 2 - Flowering Stage",
        "description": "Monitor flower buds appearance",
        "category": "monitor",
        "start_date": (year2_start + timedelta(days=100)).strftime("%Y-%m-%d"),
        "due_date": (year2_start + timedelta(days=120)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Year 2 - Fruit Set",
        "description": "Apply Calcium & Magnesium fertilizers",
        "category": "fertilize",
        "start_date": (year2_start + timedelta(days=150)).strftime("%Y-%m-%d"),
        "due_date": (year2_start + timedelta(days=155)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Year 2 - First Small Harvest",
        "description": f"Harvest small amount of {grape_variety} grapes",
        "category": "harvest",
        "start_date": (year2_start + timedelta(days=240)).strftime("%Y-%m-%d"),
        "due_date": (year2_start + timedelta(days=260)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    # Year 3-4 Full Production (key milestones)
    year3_start = planting_date.replace(year=planting_date.year + 2)
    
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Year 3 - Full Production Preparation",
        "description": "Ensure trellis system can support full yield",
        "category": "structure",
        "start_date": (year3_start + timedelta(days=30)).strftime("%Y-%m-%d"),
        "due_date": (year3_start + timedelta(days=45)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    timeline.append({
        "id": str(task_id := task_id + 1),
        "title": "Year 3 - First Full Harvest",
        "description": f"Harvest mature {grape_variety} grapes (15-20 kg per vine)",
        "category": "harvest",
        "start_date": (year3_start + timedelta(days=240)).strftime("%Y-%m-%d"),
        "due_date": (year3_start + timedelta(days=260)).strftime("%Y-%m-%d"),
        "status": "pending"
    })
    
    # Return the complete timeline
    return timeline

# Function to calculate optimal farm layout
def calculate_farm_layout(farm_length, farm_width, plant_length_spacing, plant_width_spacing):
    """Calculate optimal farm layout for grape cultivation"""
    # Calculate maximum plants that can be accommodated
    max_plants_width = math.floor(farm_width / plant_width_spacing)
    max_plants_length = math.floor(farm_length / plant_length_spacing)
    max_capacity = max_plants_width * max_plants_length
    
    # Calculate used area
    used_width = max_plants_width * plant_width_spacing
    used_length = max_plants_length * plant_length_spacing
    used_area = used_width * used_length
    total_area = farm_width * farm_length
    utilization = (used_area / total_area) * 100
    
    return {
        "max_plants_width": max_plants_width,
        "max_plants_length": max_plants_length,
        "max_capacity": max_capacity,
        "used_width": used_width,
        "used_length": used_length,
        "used_area": used_area,
        "total_area": total_area,
        "utilization": utilization
    }

# Function to get seasonal activities based on date
def get_seasonal_activities(date):
    month = date.month
    day = date.day
    current_month_name = calendar.month_name[month]
    
    # Define activities for each period
    activities = {
        # Land Preparation & Planting (April – June)
        4: {
            'phase': 'Land Preparation & Planting',
            'current': [
                'Deep plowing, leveling, and soil testing (April 1-15)' if day <= 15 else 'Apply organic manure and fertilizers (April 16-30)',
            ],
            'upcoming': [
                'Install drip irrigation and trellis system (May 1-15)',
                'Plant grape saplings at spacing (May 16-31)',
                'Provide shade nets to protect young plants (June)'
            ]
        },
        5: {
            'phase': 'Land Preparation & Planting',
            'current': [
                'Install drip irrigation and trellis system (May 1-15)' if day <= 15 else 'Plant grape saplings at spacing (May 16-31)',
            ],
            'upcoming': [
                'Provide shade nets to protect young plants (June)',
                'First training of vines on trellis/wires (July)',
                'Apply nitrogen-rich fertilizers (July)'
            ]
        },
        6: {
            'phase': 'Land Preparation & Planting',
            'current': [
                'Provide shade nets to protect young plants from excess rain',
            ],
            'upcoming': [
                'First training of vines on trellis/wires (July)',
                'Apply nitrogen-rich fertilizers (July)',
                'Spray bio-pesticides to control mealybugs (July)'
            ]
        },
        
        # Vine Growth & Canopy Development (July – September)
        7: {
            'phase': 'Vine Growth & Canopy Development',
            'current': [
                'First training of vines on trellis/wires',
                'Apply nitrogen-rich fertilizers (Urea, Ammonium Sulfate)',
                'Spray bio-pesticides to control mealybugs'
            ],
            'upcoming': [
                'Remove weak or unwanted shoots (August)',
                'First pruning (back pruning) to encourage strong growth (August)',
                'Second pruning to prepare for flowering (September)'
            ]
        },
        8: {
            'phase': 'Vine Growth & Canopy Development',
            'current': [
                'Remove weak or unwanted shoots (canopy management)',
                'First pruning (back pruning) to encourage strong shoot growth'
            ],
            'upcoming': [
                'Second pruning to prepare for flowering (September)',
                'Spray Gibberellic Acid to induce flowering (September)',
                'Regular irrigation for uniform flowering (October)'
            ]
        },
        9: {
            'phase': 'Vine Growth & Canopy Development',
            'current': [
                'Second pruning (forward pruning) to prepare for flowering',
                'Spray Gibberellic Acid (GA3) to induce flowering'
            ],
            'upcoming': [
                'Regular irrigation for uniform flowering (October)',
                'Apply Phosphorous and Potassium fertilizers (October)',
                'Protect from thrips, mites, and downy mildew (October)'
            ]
        },
        
        # Flowering & Fruit Setting (October – December)
        10: {
            'phase': 'Flowering & Fruit Setting',
            'current': [
                'Regular irrigation for uniform flowering',
                'Apply Phosphorous and Potassium fertilizers to strengthen flowers',
                'Protect from thrips, mites, and downy mildew'
            ],
            'upcoming': [
                'Monitor and remove excess flower clusters (November)',
                'Apply Calcium Nitrate and Boron for fruit setting (November)',
                'Ensure pollination-friendly environment (December)'
            ]
        },
        11: {
            'phase': 'Flowering & Fruit Setting',
            'current': [
                'Monitor and remove excess flower clusters (only 2-3 per shoot)',
                'Apply Calcium Nitrate and Boron for fruit setting'
            ],
            'upcoming': [
                'Ensure pollination-friendly environment (December)',
                'Apply Sulfur & Copper sprays to prevent fungal diseases (December)',
                'First fruit thinning to remove weak berries (January)'
            ]
        },
        12: {
            'phase': 'Flowering & Fruit Setting',
            'current': [
                'Fruit set stage begins; ensure pollination-friendly environment',
                'Apply Sulfur & Copper sprays to prevent fungal diseases'
            ],
            'upcoming': [
                'First fruit thinning to remove weak berries (January)',
                'Apply Potassium Nitrate for better berry size (January)',
                'Use Gibberellic Acid spray for berry elongation (January)'
            ]
        },
        
        # Berry Growth & Development (January – March)
        1: {
            'phase': 'Berry Growth & Development',
            'current': [
                'First fruit thinning to remove weak berries',
                'Apply Potassium Nitrate (KNO₃) for better berry size',
                'Use Gibberellic Acid (GA3) spray for berry elongation'
            ],
            'upcoming': [
                'Bunch thinning to maintain fruit uniformity (February)',
                'Reduce nitrogen fertilizers, increase Potassium & Calcium (February)',
                'Stop heavy irrigation to prevent cracking (March)'
            ]
        },
        2: {
            'phase': 'Berry Growth & Development',
            'current': [
                'Bunch thinning to maintain fruit uniformity',
                'Reduce nitrogen fertilizers and increase Potassium & Calcium sprays',
                'Reduce irrigation before harvesting to improve sweetness'
            ],
            'upcoming': [
                'Final monitoring of diseases and fruit quality (March)',
                'Stop heavy irrigation to prevent cracking (March)',
                'First harvest for early varieties (March)'
            ]
        },
        3: {
            'phase': 'Berry Growth & Development / Harvesting',
            'current': [
                'Final monitoring of diseases and fruit quality',
                'Stop heavy irrigation to prevent cracking',
                'First harvest for early varieties' if day >= 15 else 'Prepare for harvesting'
            ],
            'upcoming': [
                'Handpick grapes early in the morning (March 15 - April 10)',
                'Remove damaged bunches during harvest',
                'Sulfur fumigation to prevent fungal growth'
            ] if day < 15 else [
                'Sorting based on size, color, and variety (April 11-30)',
                'Pack in ventilated boxes (April 11-30)',
                'Transport to local mandis (April 20-May 10)'
            ]
        }
    }
    
    # If no activities defined for this month, return general info
    if month not in activities:
        return {
            'phase': 'Maintenance Phase',
            'current': [
                'Routine check for pest or disease',
                'Standard irrigation based on soil moisture',
                'Regular monitoring of vine growth'
            ],
            'upcoming': [
                'Prepare for next seasonal activity',
                'Plan fertilizer application based on soil test',
                'Maintain trellis and support system'
            ]
        }
    
    return activities[month]

# Function to generate a PDF farm plan
def generate_pdf_plan(farm_data, schedule_data):
    """Generate a PDF with farm plan details using ReportLab"""
    try:
        # Create the directory for storing PDFs if it doesn't exist
        pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        
        # File path for the PDF
        filename = f"{farm_data['_id']}.pdf"
        filepath = os.path.join(pdf_dir, filename)
        
        print(f"Creating PDF at: {filepath}")
        
        # Create a PDF document with larger page size for better spacing
        doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        elements = []
        
        # Add custom styles
        title_style = styles["Heading1"]
        title_style.alignment = 1  # Center alignment
        
        subtitle_style = styles["Heading2"]
        subtitle_style.spaceAfter = 10
        subtitle_style.spaceBefore = 20
        
        section_style = styles["Heading3"]
        section_style.spaceBefore = 15
        section_style.spaceAfter = 8
        
        normal_style = styles["Normal"]
        normal_style.spaceBefore = 6
        normal_style.spaceAfter = 6
        
        # Title
        elements.append(Paragraph(f"Farm Plan: {farm_data['farm_name']}", title_style))
        elements.append(Spacer(1, 0.25*inch))
        
        # Farm Details Section
        elements.append(Paragraph("Farm Details", subtitle_style))
        
        # Create a table for farm details
        farm_detail_data = [
            ["Farm Name", farm_data['farm_name']],
            ["Grape Variety", farm_data['grape_variety']],
            ["Location", farm_data.get('location', 'Not specified')],
            ["Farm Size", f"{farm_data['length']} m × {farm_data['width']} m"],
            ["Plant Spacing", f"{farm_data['plant_spacing']['length']} m × {farm_data['plant_spacing']['width']} m"],
            ["Creation Date", farm_data.get('created_at', 'Not recorded').strftime('%B %d, %Y') if isinstance(farm_data.get('created_at'), datetime) else str(farm_data.get('created_at', 'Not recorded'))],
        ]
        
        farm_table = Table(farm_detail_data, colWidths=[1.5*inch, 4*inch])
        farm_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(farm_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Schedule Section
        elements.append(Paragraph("Farming Schedule", subtitle_style))
        
        if schedule_data:
            # Basic schedule information
            schedule_basic_data = [
                ["Planting Date", schedule_data.get('planting_date', 'Not set').strftime('%B %d, %Y') if isinstance(schedule_data.get('planting_date'), datetime) else str(schedule_data.get('planting_date', 'Not set'))],
                ["End Date", schedule_data.get('end_date', 'Not set').strftime('%B %d, %Y') if isinstance(schedule_data.get('end_date'), datetime) else str(schedule_data.get('end_date', 'Not set'))],
            ]
            
            schedule_table = Table(schedule_basic_data, colWidths=[1.5*inch, 4*inch])
            schedule_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(schedule_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Display tasks in the schedule
            elements.append(Paragraph("Farming Tasks", section_style))
            
            if 'tasks' in schedule_data and schedule_data['tasks']:
                # Create table header
                task_data = [["Task", "Category", "Due Date", "Status"]]
                
                # Add task rows - make a separate table for descriptions to avoid overcrowding
                task_rows = []
                task_descriptions = []
                
                for idx, task in enumerate(schedule_data['tasks'], 1):
                    due_date = task.get('due_date', 'Not set')
                    if isinstance(due_date, str):
                        due_date_display = due_date
                    else:
                        due_date_display = due_date.strftime('%b %d, %Y') if due_date else 'Not set'
                    
                    task_rows.append([
                        task.get('title', 'Unnamed task'),
                        task.get('category', 'General'),
                        due_date_display,
                        task.get('status', 'pending').capitalize()
                    ])
                    
                    # Store description for separate table
                    task_descriptions.append([
                        f"{idx}.",
                        task.get('title', 'Unnamed task'),
                        task.get('description', 'No description')
                    ])
                
                # Add all rows to the tasks table
                task_data.extend(task_rows)
                
                # Create the task table with adjusted column widths
                task_table = Table(task_data, colWidths=[2.2*inch, 1.2*inch, 1.2*inch, 0.9*inch])
                task_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(task_table)
                
                # Add a spacer before the descriptions
                elements.append(Spacer(1, 0.2*inch))
                
                # Add description table header
                elements.append(Paragraph("Task Descriptions", section_style))
                
                # Create description table
                desc_header = [["#", "Task", "Description"]]
                desc_data = desc_header + task_descriptions
                
                desc_table = Table(desc_data, colWidths=[0.3*inch, 1.8*inch, 3.4*inch])
                desc_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(desc_table)
            else:
                elements.append(Paragraph("No tasks have been scheduled yet.", normal_style))
        else:
            elements.append(Paragraph("No schedule information available.", normal_style))
        
        # Get plant notes if available
        from models import get_plant_notes_by_farm
        notes = get_plant_notes_by_farm(str(farm_data['_id']))
        
        if notes and len(notes) > 0:
            elements.append(Paragraph("Plant Notes", subtitle_style))
            
            # Note type display mapping
            note_type_display = {
                'observation': 'Observation',
                'disease': 'Disease',
                'pest': 'Pest Problem',
                'growth': 'Growth',
                'maintenance': 'Maintenance',
                'harvest': 'Harvest'
            }
            
            # Split notes into location/metadata table and content table to avoid overcrowding
            notes_metadata = [["#", "Plant Location", "Title", "Type", "Date"]]
            notes_content = [["#", "Title", "Content"]]
            
            # Add note rows
            for idx, note in enumerate(notes, 1):
                created_at = note.get('created_at', 'Not recorded')
                if isinstance(created_at, str):
                    date_display = created_at
                else:
                    date_display = created_at.strftime('%b %d, %Y') if created_at else 'Not recorded'
                
                # Adjust row and column to be 1-indexed for user display
                row_idx = note.get('row', 0) + 1
                col_idx = note.get('col', 0) + 1
                
                # Add to metadata table
                notes_metadata.append([
                    f"{idx}.",
                    f"Row {row_idx}, Col {col_idx}",
                    note.get('title', 'Untitled'),
                    note_type_display.get(note.get('type', ''), note.get('type', 'General')),
                    date_display
                ])
                
                # Add to content table
                notes_content.append([
                    f"{idx}.",
                    note.get('title', 'Untitled'),
                    note.get('content', 'No content')
                ])
            
            # Create the notes metadata table
            notes_meta_table = Table(notes_metadata, colWidths=[0.3*inch, 1.2*inch, 1.5*inch, 1*inch, 1.5*inch])
            notes_meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(notes_meta_table)
            elements.append(Spacer(1, 0.2*inch))
            
            # Add content table header
            elements.append(Paragraph("Note Details", section_style))
            
            # Create the notes content table
            notes_content_table = Table(notes_content, colWidths=[0.3*inch, 1.2*inch, 4*inch])
            notes_content_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(notes_content_table)
        else:
            elements.append(Paragraph("Plant Notes", subtitle_style))
            elements.append(Paragraph("No plant notes recorded yet.", normal_style))
        
        # Add footer with timestamp
        def add_footer(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 8)
            footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}"
            canvas.drawRightString(6.5*inch, 0.5*inch, footer_text)
            page_num = canvas.getPageNumber()
            canvas.drawCentredString(4.25*inch, 0.5*inch, f"Page {page_num}")
            canvas.restoreState()
        
        # Build the PDF
        doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
        
        print(f"PDF generated successfully at: {filepath}")
        
        # Return success and the filename for the download URL
        return {
            "success": True,
            "message": "PDF plan generated successfully",
            "filename": filename
        }
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        # Return failure
        return {
            "success": False,
            "message": f"Failed to generate PDF: {str(e)}"
        }

# Function to generate gemini-based recommendation (placeholder)
def get_gemini_recommendation(grape_variety, location, query):
    """Get detailed recommendations for grape varieties using Google's Gemini API"""
    import requests
    import json
    
    # Gemini API configuration
    api_key = os.getenv('GEMINI_API_KEY_2')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    # Construct a comprehensive prompt that includes grape variety, location, and specific query
    prompt = f"""
    Provide detailed information about the grape variety '{grape_variety}' grown in {location}.
    
    Include:
    1. Specific climate requirements and adaptability for this variety
    2. Future climate predictions for growing this variety considering climate change
    3. Common diseases and pests that affect this variety, especially in {location}
    4. Detailed preventive measures for these diseases and pests
    5. Best practices for irrigation, fertilization, and vineyard management
    6. Specific advice related to: {query}
    
    Format the response in a well-structured way with clear sections.
    """
    
    # Request payload
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 800
        }
    }
    
    # Make API request
    try:
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
                        return content["parts"][0]["text"]
            
            return f"Could not get detailed information about {grape_variety} from Gemini API. Please try again later."
        else:
            # Fallback to basic information if API call fails
            return _get_fallback_recommendation(grape_variety, location, query)
    
    except Exception as e:
        # If any error occurs, use the fallback function
        return _get_fallback_recommendation(grape_variety, location, query)

def _get_fallback_recommendation(grape_variety, location, query):
    """Fallback function for when the Gemini API call fails"""
    # Basic recommendations based on grape variety
    recommendations = {
        "Thompson Seedless": "Thompson Seedless grapes thrive in warm, dry climates with well-drained soil. Focus on proper trellis training and regular pruning to maximize yields. As climate changes, consider increased water management and shade protection during extreme heat periods. Common pests include powdery mildew and spider mites - regular monitoring and preventive spraying with copper-based fungicides are recommended.",
        "Flame Seedless": "Flame Seedless requires consistent sunlight and warm temperatures. Pay special attention to irrigation during fruit development. With warming climates, ensure proper canopy management to protect fruits from sunburn. Disease prevention should focus on downy mildew and phylloxera control through cultural practices and resistant rootstocks.",
        "Crimson Seedless": "Crimson Seedless benefits from moderate temperatures and regular thinning to produce large, high-quality clusters. Future climate conditions may require earlier harvesting dates. Monitor closely for pierce's disease and leafroll virus, especially in warmer regions. Preventative measures include vector control and virus-tested planting material.",
        "Concord": "Concord grapes are disease-resistant but require cold winters for proper dormancy. Focus on balanced pruning and good air circulation. Climate change may affect winter chill hours - consider planting on north-facing slopes in warmer regions. Black rot and anthracnose can be issues - maintain clean vineyards and apply protective sprays before rain events.",
        "Moon Drops": "Moon Drops grapes need support for their elongated fruits. Ensure proper trellis systems and cluster thinning for best results. This variety may face challenges with irregular ripening in fluctuating future climates. Preventive measures should include proper canopy management and regulated deficit irrigation during certain growth stages.",
        "Black Corinth": "Black Corinth (Zante Currant) grapes need hot, dry conditions and produce small berries often used for drying. Climate warming may actually benefit this heat-loving variety, but increased pest pressure is likely. Implement robust IPM strategies focusing on early detection and biological controls where possible.",
        "Red Globe": "Red Globe produces large berries that require significant thinning and cluster management for best quality. This variety is particularly susceptible to extreme weather fluctuations expected with climate change. Preventive strategies should include windbreaks, shade cloth during heat waves, and excellent drainage systems to manage heavy rainfall events.",
        "Autumn Royal": "Autumn Royal benefits from extended growing seasons. Maintain adequate potassium levels for proper fruit coloration. Future climate projections indicate potential for earlier bud break, requiring frost protection systems. Focus on preventing bunch rot through proper canopy management and timely fungicide applications in humid conditions.",
        "Sultana": "Sultana (Thompson Seedless) grapes for raisin production need hot, dry conditions during ripening and harvest. Climate change may increase drought stress - implement water-efficient irrigation systems. Powdery mildew is a major concern; maintain good air circulation and apply preventive fungicides during susceptible growth stages."
    }
    
    base_response = recommendations.get(grape_variety, f"The {grape_variety} variety thrives with proper irrigation, good sunlight exposure, and regular monitoring for pests and diseases. In changing climate conditions, consider implementing water conservation techniques and heat mitigation strategies. Regular scouting for pests and preventive spraying are essential practices.")
    
    # Append some location-specific info
    if "rainfall" in query.lower() or "rain" in query.lower():
        return f"{base_response} In {location}, ensure proper drainage during rainy periods to prevent root diseases. Consider cover crops on vineyard floors to prevent erosion during heavy rainfall events."
    elif "pest" in query.lower() or "disease" in query.lower():
        return f"{base_response} Common pests in {location} include powdery mildew, downy mildew, and grape leafhoppers. Preventive measures include proper vineyard sanitation, maintaining open canopies for air circulation, and strategic application of appropriate fungicides and insecticides according to local IPM guidelines."
    elif "climate" in query.lower() or "future" in query.lower():
        return f"{base_response} Climate projections for {location} suggest increasing temperatures and more variable precipitation patterns. Consider row orientation to minimize afternoon sun exposure, install efficient irrigation systems, and select clones that tolerate heat stress. Diversifying grape varieties across your vineyard can also reduce climate-related risks."
    else:
        return base_response 