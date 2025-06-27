"""
Database initialization script for Smart Agriculture System
This script creates the database tables and sets up initial data
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Prediction, Notification, WeatherData, CropPrice
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """Create all database tables"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            logger.info("Database tables created successfully")
            return True
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False

def create_sample_users():
    """Create sample users for testing (optional)"""
    try:
        with app.app_context():
            # Check if users already exist
            if User.query.first():
                logger.info("Users already exist, skipping sample user creation")
                return True
            
            # Create sample users
            sample_users = [
                {
                    'username': 'farmer1',
                    'email': 'farmer1@example.com',
                    'password': 'password123'
                },
                {
                    'username': 'demo_user',
                    'email': 'demo@smartagri.com',
                    'password': 'demo123'
                }
            ]
            
            for user_data in sample_users:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password'])
                )
                db.session.add(user)
            
            db.session.commit()
            logger.info("Sample users created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error creating sample users: {e}")
        db.session.rollback()
        return False

def create_sample_notifications():
    """Create sample notifications for users"""
    try:
        with app.app_context():
            # Get first user
            user = User.query.first()
            if not user:
                logger.warning("No users found, skipping notification creation")
                return True
            
            # Check if notifications already exist
            if Notification.query.first():
                logger.info("Notifications already exist, skipping sample creation")
                return True
            
            # Create sample notifications
            notifications = [
                {
                    'title': 'Weather Alert',
                    'message': 'Heavy rainfall expected in your area. Ensure proper drainage for your crops.',
                    'notification_type': 'weather'
                },
                {
                    'title': 'Crop Price Update',
                    'message': 'Rice prices have increased by 8% in the local market.',
                    'notification_type': 'crop_price'
                },
                {
                    'title': 'System Update',
                    'message': 'New disease detection models have been added to improve accuracy.',
                    'notification_type': 'system'
                }
            ]
            
            for notif_data in notifications:
                notification = Notification(
                    user_id=user.id,
                    title=notif_data['title'],
                    message=notif_data['message'],
                    notification_type=notif_data['notification_type'],
                    is_read=False
                )
                db.session.add(notification)
            
            db.session.commit()
            logger.info("Sample notifications created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error creating sample notifications: {e}")
        db.session.rollback()
        return False

def create_sample_weather_data():
    """Create sample weather data"""
    try:
        with app.app_context():
            # Check if weather data already exists
            if WeatherData.query.first():
                logger.info("Weather data already exists, skipping sample creation")
                return True
            
            # Create sample weather data for the past week
            base_date = datetime.now() - timedelta(days=7)
            
            for i in range(7):
                date = base_date + timedelta(days=i)
                weather = WeatherData(
                    location='Local Area',
                    temperature=20.0 + (i * 2.5),  # Varying temperature
                    humidity=60.0 + (i * 3),       # Varying humidity
                    rainfall=5.0 + (i * 2),        # Varying rainfall
                    wind_speed=8.0 + (i * 1.5),    # Varying wind speed
                    weather_condition=['Sunny', 'Cloudy', 'Rainy', 'Partly Cloudy'][i % 4],
                    recorded_at=date
                )
                db.session.add(weather)
            
            db.session.commit()
            logger.info("Sample weather data created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error creating sample weather data: {e}")
        db.session.rollback()
        return False

def create_sample_crop_prices():
    """Create sample crop price data"""
    try:
        with app.app_context():
            # Check if crop price data already exists
            if CropPrice.query.first():
                logger.info("Crop price data already exists, skipping sample creation")
                return True
            
            # Create sample crop prices
            crops = [
                {'name': 'Rice', 'price': 22.50, 'trend': 'increasing'},
                {'name': 'Wheat', 'price': 20.75, 'trend': 'stable'},
                {'name': 'Cotton', 'price': 45.00, 'trend': 'decreasing'},
                {'name': 'Maize', 'price': 18.25, 'trend': 'increasing'},
                {'name': 'Tomato', 'price': 15.50, 'trend': 'stable'},
                {'name': 'Potato', 'price': 12.00, 'trend': 'increasing'},
                {'name': 'Onion', 'price': 25.75, 'trend': 'decreasing'},
                {'name': 'Sugarcane', 'price': 35.00, 'trend': 'stable'}
            ]
            
            for crop_data in crops:
                crop_price = CropPrice(
                    crop_name=crop_data['name'],
                    price_per_kg=crop_data['price'],
                    market_location='Local Mandi',
                    price_trend=crop_data['trend']
                )
                db.session.add(crop_price)
            
            db.session.commit()
            logger.info("Sample crop price data created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error creating sample crop price data: {e}")
        db.session.rollback()
        return False

def initialize_database(create_samples=False):
    """
    Initialize the entire database
    
    Args:
        create_samples (bool): Whether to create sample data for testing
    """
    logger.info("Starting database initialization...")
    
    # Create database tables
    if not create_database():
        logger.error("Failed to create database tables")
        return False
    
    if create_samples:
        logger.info("Creating sample data...")
        
        # Create sample users
        if not create_sample_users():
            logger.error("Failed to create sample users")
            return False
        
        # Create sample notifications
        if not create_sample_notifications():
            logger.error("Failed to create sample notifications")
            return False
        
        # Create sample weather data
        if not create_sample_weather_data():
            logger.error("Failed to create sample weather data")
            return False
        
        # Create sample crop prices
        if not create_sample_crop_prices():
            logger.error("Failed to create sample crop prices")
            return False
        
        logger.info("Sample data created successfully")
    
    logger.info("Database initialization completed successfully!")
    return True

def reset_database():
    """
    Reset the database (drop all tables and recreate)
    WARNING: This will delete all existing data!
    """
    try:
        with app.app_context():
            logger.warning("Resetting database - all data will be lost!")
            
            # Drop all tables
            db.drop_all()
            logger.info("All tables dropped")
            
            # Recreate all tables
            db.create_all()
            logger.info("All tables recreated")
            
            return True
            
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return False

def check_database_status():
    """Check the current status of the database"""
    try:
        with app.app_context():
            # Check if tables exist by trying to query them
            models_to_check = [User, Prediction, Notification, WeatherData, CropPrice]
            
            logger.info("Database Status Check:")
            logger.info("=" * 50)
            
            for model in models_to_check:
                try:
                    count = model.query.count()
                    logger.info(f"{model.__name__}: {count} records")
                except Exception as e:
                    logger.error(f"{model.__name__}: Table not found or error - {e}")
            
            logger.info("=" * 50)
            return True
            
    except Exception as e:
        logger.error(f"Error checking database status: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization script for Smart Agriculture System")
    parser.add_argument("--reset", action="store_true", help="Reset the database (WARNING: deletes all data)")
    parser.add_argument("--no-samples", action="store_true", help="Don't create sample data")
    parser.add_argument("--status", action="store_true", help="Check database status")
    
    args = parser.parse_args()
    
    if args.status:
        check_database_status()
    elif args.reset:
        if input("Are you sure you want to reset the database? This will delete all data! (yes/no): ").lower() == 'yes':
            if reset_database():
                logger.info("Database reset successful")
                # Initialize with sample data unless --no-samples is specified
                initialize_database(create_samples=not args.no_samples)
            else:
                logger.error("Database reset failed")
        else:
            logger.info("Database reset cancelled")
    else:
        # Normal initialization
        create_samples = not args.no_samples
        if initialize_database(create_samples=create_samples):
            logger.info("Database initialization successful!")
        else:
            logger.error("Database initialization failed!")
