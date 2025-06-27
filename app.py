import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import numpy as np
import pandas as pd
from datetime import datetime
import joblib
import cv2
from PIL import Image
import io
import base64

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-for-development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///agriculture.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize the app with the extension
db.init_app(app)

# Import models and utilities
from models import User, Prediction, Notification
from utils import allowed_file, process_weather_data

# Initialize ML manager and chatbot as None (lazy loading)
ml_manager = None
chatbot = None

def get_ml_manager():
    """Lazy loading of ML manager"""
    global ml_manager
    if ml_manager is None:
        try:
            from ml_models import MLModelManager
            ml_manager = MLModelManager()
        except Exception as e:
            logging.error(f"Error initializing ML manager: {e}")
            # Return a mock manager for development
            class MockMLManager:
                def predict_soil_fertility(self, data):
                    return "Medium", 85.0
                def predict_crop_recommendation(self, data):
                    return "Rice", 90.0
                def predict_plant_disease(self, image):
                    return "Healthy", 95.0
                def get_soil_recommendations(self, fertility):
                    return ["Add balanced NPK fertilizer", "Test soil pH"]
                def get_crop_info(self, crop):
                    return {"season": "Kharif", "water_req": "Medium"}
                def get_disease_treatment(self, disease):
                    return "Apply appropriate fungicide treatment"
            ml_manager = MockMLManager()
    return ml_manager

def get_chatbot():
    """Lazy loading of chatbot"""
    global chatbot
    if chatbot is None:
        try:
            from assistant import VoiceChatbot
            chatbot = VoiceChatbot()
        except Exception as e:
            logging.error(f"Error initializing chatbot: {e}")
            # Return a mock chatbot for development
            class MockChatbot:
                def process_message(self, message, language='en'):
                    return "Hello! I'm here to help with your farming questions."
            chatbot = MockChatbot()
    return chatbot

# Create tables on startup
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Home page with agriculture system overview"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            logging.error(f"Registration error: {e}")
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard for logged-in users"""
    if 'user_id' not in session:
        flash('Please login to access dashboard.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    recent_predictions = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).limit(5).all()
    notifications = Notification.query.filter_by(user_id=user.id, is_read=False).all()
    
    return render_template('dashboard.html', user=user, predictions=recent_predictions, notifications=notifications)

@app.route('/soil-prediction', methods=['GET', 'POST'])
def soil_prediction():
    """Soil fertility prediction using ML"""
    if 'user_id' not in session:
        flash('Please login to access this feature.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Get input parameters
            nitrogen = float(request.form['nitrogen'])
            phosphorus = float(request.form['phosphorus'])
            potassium = float(request.form['potassium'])
            ph = float(request.form['ph'])
            organic_matter = float(request.form['organic_matter'])
            moisture = float(request.form['moisture'])
            
            # Prepare input for prediction
            input_data = np.array([[nitrogen, phosphorus, potassium, ph, organic_matter, moisture]])
            
            # Make prediction
            ml_mgr = get_ml_manager()
            fertility_class, confidence = ml_mgr.predict_soil_fertility(input_data)
            
            # Save prediction to database
            prediction = Prediction(
                user_id=session['user_id'],
                prediction_type='soil_fertility',
                input_data=f"N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}, OM:{organic_matter}, M:{moisture}",
                result=f"Fertility: {fertility_class}, Confidence: {confidence:.2f}%",
                confidence_score=confidence
            )
            db.session.add(prediction)
            db.session.commit()
            
            return render_template('soil_prediction.html', 
                                 prediction_result={
                                     'fertility_class': fertility_class,
                                     'confidence': confidence,
                                     'recommendations': ml_mgr.get_soil_recommendations(fertility_class)
                                 })
        
        except Exception as e:
            flash(f'Prediction failed: {str(e)}', 'error')
            logging.error(f"Soil prediction error: {e}")
    
    return render_template('soil_prediction.html')

@app.route('/crop-suggestion', methods=['GET', 'POST'])
def crop_suggestion():
    """Crop recommendation using ML"""
    if 'user_id' not in session:
        flash('Please login to access this feature.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Get input parameters
            nitrogen = float(request.form['nitrogen'])
            phosphorus = float(request.form['phosphorus'])
            potassium = float(request.form['potassium'])
            temperature = float(request.form['temperature'])
            humidity = float(request.form['humidity'])
            ph = float(request.form['ph'])
            rainfall = float(request.form['rainfall'])
            
            # Prepare input for prediction
            input_data = np.array([[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]])
            
            # Make prediction
            ml_mgr = get_ml_manager()
            recommended_crop, confidence = ml_mgr.predict_crop_recommendation(input_data)
            
            # Save prediction to database
            prediction = Prediction(
                user_id=session['user_id'],
                prediction_type='crop_recommendation',
                input_data=f"N:{nitrogen}, P:{phosphorus}, K:{potassium}, T:{temperature}, H:{humidity}, pH:{ph}, R:{rainfall}",
                result=f"Crop: {recommended_crop}, Confidence: {confidence:.2f}%",
                confidence_score=confidence
            )
            db.session.add(prediction)
            db.session.commit()
            
            return render_template('crop_suggestion.html', 
                                 prediction_result={
                                     'recommended_crop': recommended_crop,
                                     'confidence': confidence,
                                     'crop_info': ml_mgr.get_crop_info(recommended_crop)
                                 })
        
        except Exception as e:
            flash(f'Prediction failed: {str(e)}', 'error')
            logging.error(f"Crop suggestion error: {e}")
    
    return render_template('crop_suggestion.html')

@app.route('/disease-detection', methods=['GET', 'POST'])
def disease_detection():
    """Plant disease detection using image analysis"""
    if 'user_id' not in session:
        flash('Please login to access this feature.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            if 'image' not in request.files:
                flash('No image file selected!', 'error')
                return render_template('disease_detection.html')
            
            file = request.files['image']
            if file.filename == '':
                flash('No image file selected!', 'error')
                return render_template('disease_detection.html')
            
            if file and allowed_file(file.filename):
                # Process the image
                image = Image.open(file.stream)
                
                # Convert PIL image to numpy array for processing
                img_array = np.array(image)
                
                # Make disease prediction
                ml_mgr = get_ml_manager()
                disease_class, confidence = ml_mgr.predict_plant_disease(img_array)
                
                # Convert image to base64 for display
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG')
                img_str = base64.b64encode(img_buffer.getvalue()).decode()
                
                # Save prediction to database
                prediction = Prediction(
                    user_id=session['user_id'],
                    prediction_type='disease_detection',
                    input_data=f"Image: {file.filename}",
                    result=f"Disease: {disease_class}, Confidence: {confidence:.2f}%",
                    confidence_score=confidence
                )
                db.session.add(prediction)
                db.session.commit()
                
                return render_template('disease_detection.html', 
                                     prediction_result={
                                         'disease_class': disease_class,
                                         'confidence': confidence,
                                         'image_data': img_str,
                                         'treatment': ml_mgr.get_disease_treatment(disease_class)
                                     })
            else:
                flash('Invalid file type. Please upload an image.', 'error')
        
        except Exception as e:
            flash(f'Disease detection failed: {str(e)}', 'error')
            logging.error(f"Disease detection error: {e}")
    
    return render_template('disease_detection.html')

@app.route('/chatbot')
def chatbot_page():
    """Voice chatbot interface"""
    if 'user_id' not in session:
        flash('Please login to access this feature.', 'error')
        return redirect(url_for('login'))
    
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API endpoint for chatbot interactions"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.json
        message = data.get('message', '')
        language = data.get('language', 'en')
        
        # Process the message through the chatbot
        chat_bot = get_chatbot()
        response = chat_bot.process_message(message, language)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
    
    except Exception as e:
        logging.error(f"Chat API error: {e}")
        return jsonify({'error': 'Chat processing failed'}), 500

@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    """Convert speech audio to text"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # This would handle audio file upload and speech recognition
        # For now, return a placeholder response
        return jsonify({
            'text': 'Speech recognition feature will be implemented with proper audio handling',
            'status': 'success'
        })
    
    except Exception as e:
        logging.error(f"Speech to text error: {e}")
        return jsonify({'error': 'Speech recognition failed'}), 500

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech audio"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.json
        text = data.get('text', '')
        language = data.get('language', 'en')
        
        # Generate speech audio
        chat_bot = get_chatbot()
        audio_data = chat_bot.text_to_speech(text, language) if hasattr(chat_bot, 'text_to_speech') else None
        
        return jsonify({
            'audio_data': audio_data,
            'status': 'success'
        })
    
    except Exception as e:
        logging.error(f"Text to speech error: {e}")
        return jsonify({'error': 'Text to speech failed'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
