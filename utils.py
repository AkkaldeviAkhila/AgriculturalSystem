import os
import logging
import requests
from datetime import datetime, timedelta
import json

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_weather_data(location='default'):
    """Process weather data for agriculture insights"""
    try:
        # This would integrate with actual weather API
        # For demo purposes, return sample weather data
        sample_weather = {
            'location': location,
            'temperature': 25.5,
            'humidity': 65.0,
            'rainfall': 2.5,
            'wind_speed': 8.2,
            'weather_condition': 'Partly Cloudy',
            'forecast': [
                {'day': 'Today', 'temp_max': 28, 'temp_min': 22, 'rain_chance': 30},
                {'day': 'Tomorrow', 'temp_max': 30, 'temp_min': 24, 'rain_chance': 10},
                {'day': 'Day 3', 'temp_max': 27, 'temp_min': 21, 'rain_chance': 60}
            ],
            'agriculture_advice': get_weather_based_advice(25.5, 65.0, 2.5)
        }
        
        return sample_weather
        
    except Exception as e:
        logging.error(f"Weather data processing error: {e}")
        return None

def get_weather_based_advice(temperature, humidity, rainfall):
    """Generate agriculture advice based on weather conditions"""
    advice = []
    
    if temperature > 35:
        advice.append("High temperature alert: Increase irrigation frequency")
        advice.append("Consider shade nets for sensitive crops")
    elif temperature < 10:
        advice.append("Cold temperature warning: Protect crops from frost")
        advice.append("Delay transplanting until temperatures rise")
    
    if humidity > 80:
        advice.append("High humidity: Monitor for fungal diseases")
        advice.append("Ensure good air circulation around plants")
    elif humidity < 40:
        advice.append("Low humidity: Increase mulching to retain moisture")
    
    if rainfall > 50:
        advice.append("Heavy rainfall expected: Ensure proper drainage")
        advice.append("Postpone fertilizer application")
    elif rainfall < 5:
        advice.append("Low rainfall: Plan irrigation accordingly")
        advice.append("Consider drought-resistant crop varieties")
    
    if not advice:
        advice.append("Weather conditions are favorable for normal farming activities")
    
    return advice

def get_crop_price_data():
    """Get current crop price information"""
    try:
        # This would integrate with actual market price API
        # For demo purposes, return sample price data
        sample_prices = [
            {
                'crop_name': 'Rice',
                'price_per_kg': 22.50,
                'market_location': 'Local Mandi',
                'price_trend': 'increasing',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
            },
            {
                'crop_name': 'Wheat',
                'price_per_kg': 20.75,
                'market_location': 'Local Mandi',
                'price_trend': 'stable',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
            },
            {
                'crop_name': 'Cotton',
                'price_per_kg': 45.00,
                'market_location': 'Local Mandi',
                'price_trend': 'decreasing',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
            },
            {
                'crop_name': 'Tomato',
                'price_per_kg': 15.25,
                'market_location': 'Local Mandi',
                'price_trend': 'increasing',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        ]
        
        return sample_prices
        
    except Exception as e:
        logging.error(f"Price data error: {e}")
        return []

def format_currency(amount, currency='INR'):
    """Format currency amount for display"""
    if currency == 'INR':
        return f"₹{amount:.2f}"
    else:
        return f"{amount:.2f}"

def calculate_fertilizer_recommendation(soil_data):
    """Calculate fertilizer recommendations based on soil analysis"""
    try:
        nitrogen = soil_data.get('nitrogen', 0)
        phosphorus = soil_data.get('phosphorus', 0)
        potassium = soil_data.get('potassium', 0)
        
        recommendations = {
            'nitrogen_needed': max(0, 60 - nitrogen),
            'phosphorus_needed': max(0, 40 - phosphorus),
            'potassium_needed': max(0, 50 - potassium)
        }
        
        # Calculate fertilizer amounts (simplified calculation)
        recommendations['urea_kg_per_acre'] = recommendations['nitrogen_needed'] * 2.17
        recommendations['dap_kg_per_acre'] = recommendations['phosphorus_needed'] * 2.27
        recommendations['mop_kg_per_acre'] = recommendations['potassium_needed'] * 1.67
        
        return recommendations
        
    except Exception as e:
        logging.error(f"Fertilizer calculation error: {e}")
        return {}

def validate_input_data(data, required_fields):
    """Validate input data for ML predictions"""
    errors = []
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
        else:
            try:
                float(data[field])
            except (ValueError, TypeError):
                errors.append(f"Invalid value for {field}: must be a number")
    
    return errors

def log_prediction_accuracy(prediction_type, actual_result, predicted_result):
    """Log prediction accuracy for model improvement"""
    try:
        accuracy_log = {
            'timestamp': datetime.now().isoformat(),
            'prediction_type': prediction_type,
            'actual': actual_result,
            'predicted': predicted_result,
            'correct': actual_result == predicted_result
        }
        
        # In production, this would be stored in a database or log file
        logging.info(f"Prediction accuracy log: {accuracy_log}")
        
    except Exception as e:
        logging.error(f"Accuracy logging error: {e}")

def generate_farming_calendar(crop_type, planting_date):
    """Generate farming calendar for crop management"""
    try:
        crop_durations = {
            'rice': 120,
            'wheat': 125,
            'cotton': 180,
            'maize': 100,
            'tomato': 90,
            'potato': 100,
            'onion': 120
        }
        
        duration = crop_durations.get(crop_type.lower(), 100)
        planting = datetime.strptime(planting_date, '%Y-%m-%d')
        
        calendar = {
            'planting_date': planting_date,
            'germination_date': (planting + timedelta(days=7)).strftime('%Y-%m-%d'),
            'first_fertilizer': (planting + timedelta(days=21)).strftime('%Y-%m-%d'),
            'second_fertilizer': (planting + timedelta(days=45)).strftime('%Y-%m-%d'),
            'flowering_stage': (planting + timedelta(days=duration//2)).strftime('%Y-%m-%d'),
            'harvest_date': (planting + timedelta(days=duration)).strftime('%Y-%m-%d')
        }
        
        return calendar
        
    except Exception as e:
        logging.error(f"Farming calendar error: {e}")
        return {}
