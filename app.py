import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import numpy as np
import io
import base64
from PIL import Image
from datetime import datetime

# Logging
logging.basicConfig(level=logging.DEBUG)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-for-development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Upload & DB config
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///agriculture.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 300, "pool_pre_ping": True}
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Database
from extensions import db
db.init_app(app)

# Models & utilities
from models import User, Prediction, Notification
from utils import allowed_file

# ML Manager preload
try:
    from ml_models import MLModelManager
    ml_manager = MLModelManager()
except Exception as e:
    logging.error(f"Error loading MLModelManager: {e}")
    class MockMLManager:
        def predict_soil_fertility(self, data): return "Medium", 85.0
        def predict_crop_recommendation(self, data): return "Rice", 90.0
        def predict_plant_disease(self, image): return "Healthy", 95.0
        def get_soil_recommendations(self, fertility): return ["Use balanced fertilizers"]
        def get_crop_info(self, crop): return {"season": "Kharif", "duration": "120-150 days", "water_requirement": "High", "soil_type": "Loam"}
        def get_disease_treatment(self, disease): return "Apply recommended fungicide"
    ml_manager = MockMLManager()

# Chatbot preload
try:
    from assistant import VoiceChatbot
    chatbot = VoiceChatbot()
except Exception as e:
    logging.error(f"Error loading VoiceChatbot: {e}")
    class MockChatbot:
        def process_message(self, msg, lang='en'): return "How can I help your farming today?"
        def text_to_speech(self, text, lang='en'):
            filename = "static/audio/mock_response.mp3"
            return {'status': 'success', 'message': 'Mock TTS generated.', 'audio_file': filename}
    chatbot = MockChatbot()

# Create tables on startup
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username, email, password = request.form['username'], request.form['email'], request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username exists!', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email registered!', 'error')
            return render_template('register.html')
        try:
            user = User(username=username, email=email, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Registration error: {e}")
            flash('Registration failed.', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'], session['username'] = user.id, user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Login required.', 'error')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    predictions = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).limit(5).all()
    notifications = Notification.query.filter_by(user_id=user.id, is_read=False).all()
    return render_template('dashboard.html', user=user, predictions=predictions, notifications=notifications)

@app.route('/soil_prediction', methods=['GET', 'POST'])
def soil_prediction():
    prediction_result = None
    if request.method == 'POST':
        try:
            features = ml_manager.soil_features
            input_data = np.array([[float(request.form.get(f.lower(), 0)) for f in features]])
            prediction, confidence = ml_manager.predict_soil_fertility(input_data)
            recommendations = ml_manager.get_soil_recommendations(prediction)
            prediction_result = {'fertility_class': prediction.capitalize(), 'confidence': confidence, 'recommendations': recommendations}
        except Exception as e:
            logging.error(f"Soil prediction error: {e}")
            prediction_result = {'fertility_class': "Error", 'confidence': 0, 'recommendations': ["Check input and retry."]}
    return render_template('soil_prediction.html', prediction_result=prediction_result)

@app.route('/crop-suggestion', methods=['GET', 'POST'])
def crop_suggestion():
    if 'user_id' not in session:
        flash('Login required.', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            inputs = [float(request.form[f]) for f in ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']]
            crop, confidence = ml_manager.predict_crop_recommendation(np.array([inputs]))
            info = ml_manager.get_crop_info(crop)
            db.session.add(Prediction(user_id=session['user_id'], prediction_type='crop_recommendation', input_data=str(inputs), result=f"{crop}, {confidence:.2f}%", confidence_score=confidence))
            db.session.commit()
            return render_template('crop_suggestion.html', prediction_result={'recommended_crop': crop, 'confidence': confidence, 'crop_info': info})
        except Exception as e:
            logging.error(f"Crop suggestion error: {e}")
            flash('Prediction failed.', 'error')
    return render_template('crop_suggestion.html')

@app.route('/disease-detection', methods=['GET', 'POST'])
def disease_detection():
    if 'user_id' not in session:
        flash('Login required.', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            file = request.files.get('image')
            if file and allowed_file(file.filename):
                img = Image.open(file.stream).convert('RGB')
                img_array = np.array(img)

                disease, confidence = ml_manager.predict_plant_disease(img_array)

                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_str = base64.b64encode(img_buffer.getvalue()).decode()

                treatment = ml_manager.get_disease_treatment(disease)

                db.session.add(Prediction(
                    user_id=session['user_id'],
                    prediction_type='disease_detection',
                    input_data=file.filename,
                    result=f"{disease}, {confidence:.2f}%",
                    confidence_score=confidence
                ))
                db.session.commit()

                return render_template('disease_detection.html', prediction_result={
                    'disease_class': disease,
                    'confidence': confidence,
                    'image_data': img_str,
                    'treatment': treatment
                })
            else:
                flash('Upload a valid image.', 'error')
        except Exception as e:
            logging.error(f"Disease detection error: {e}")
            flash('Detection failed.', 'error')
    return render_template('disease_detection.html')

@app.route('/chatbot')
def chatbot_page():
    if 'user_id' not in session:
        flash('Login required.', 'error')
        return redirect(url_for('login'))
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        data = request.json
        message, language = data.get('message', ''), data.get('language', 'en')
        response = chatbot.process_message(message, language)
        return jsonify({'response': response, 'status': 'success'})
    except Exception as e:
        logging.error(f"Chat API error: {e}")
        return jsonify({'error': 'Chat failed'}), 500

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        data = request.json
        text, language = data.get('text', ''), data.get('language', 'en')
        result = chatbot.text_to_speech(text, language)
        if result.get('status') == 'success' and result.get('audio_file'):
            audio_url = url_for('static', filename=result['audio_file'].split('static/')[-1])
            return jsonify({'audio_url': audio_url, 'status': 'success', 'message': result.get('message', '')})
        else:
            return jsonify({'error': result.get('message', 'TTS generation failed.'), 'status': 'error'})
    except Exception as e:
        logging.error(f"TTS error: {e}")
        return jsonify({'error': 'TTS failed'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)