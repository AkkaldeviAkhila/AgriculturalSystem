from extensions import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class User(db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    predictions = relationship('Prediction', backref='user', lazy=True)
    notifications = relationship('Notification', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Prediction(db.Model):
    """Model to store ML predictions and results"""
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    prediction_type = Column(String(50), nullable=False)  # soil_fertility, crop_recommendation, disease_detection
    input_data = Column(Text, nullable=False)  # JSON string of input parameters
    result = Column(Text, nullable=False)  # Prediction result
    confidence_score = Column(Float)  # Confidence percentage
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Prediction {self.prediction_type} by User {self.user_id}>'


class Notification(db.Model):
    """Model for weather and crop price notifications"""
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # weather, crop_price, system
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.title} for User {self.user_id}>'


class WeatherData(db.Model):
    """Model to store weather information"""
    __tablename__ = 'weather_data'

    id = Column(Integer, primary_key=True)
    location = Column(String(100), nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    rainfall = Column(Float)
    wind_speed = Column(Float)
    weather_condition = Column(String(100))
    recorded_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WeatherData {self.location} at {self.recorded_at}>'


class CropPrice(db.Model):
    """Model to store crop price information"""
    __tablename__ = 'crop_prices'

    id = Column(Integer, primary_key=True)
    crop_name = Column(String(100), nullable=False)
    price_per_kg = Column(Float, nullable=False)
    market_location = Column(String(100), nullable=False)
    price_date = Column(DateTime, default=datetime.utcnow)
    price_trend = Column(String(20))  # increasing, decreasing, stable

    def __repr__(self):
        return f'<CropPrice {self.crop_name}: {self.price_per_kg}/kg>'
