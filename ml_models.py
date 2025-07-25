# ml_models.py
# ml_models.py (Complete, clean, all functions, line-by-line)

import os
import logging
import numpy as np
import joblib
import cv2
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.models import load_model

# Suppress TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLModelManager:
    def __init__(self):
        try:
            model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
            logger.info("🚀 Loading ML Models for Smart Agriculture System...")

            # Load Soil Fertility Model
            self.soil_model = joblib.load(os.path.join(model_dir, 'soil_fertility_model.pkl'))
            self.soil_scaler = joblib.load(os.path.join(model_dir, 'soil_fertility_scaler.pkl'))
            self.soil_label_encoder = joblib.load(os.path.join(model_dir, 'soil_fertility_label_encoder.pkl'))
            logger.info("✅ Soil Fertility Model Loaded.")

            # Load Crop Recommendation Model
            self.crop_model = joblib.load(os.path.join(model_dir, 'crop_recommendation_model.pkl'))
            self.crop_scaler = joblib.load(os.path.join(model_dir, 'crop_recommendation_scaler.pkl'))
            self.crop_label_encoder = joblib.load(os.path.join(model_dir, 'crop_recommendation_label_encoder.pkl'))
            logger.info("✅ Crop Recommendation Model Loaded.")

            # Load Plant Disease Detection Model (if available)
            plant_model_path = os.path.join(model_dir, 'plant_disease_model.h5')
            if os.path.exists(plant_model_path):
                self.plant_disease_model = load_model(plant_model_path)
                # Correct class names (match your folders)
                self.plant_disease_classes = [
                    "Pepper__bell___Bacterial_spot",
                    "Pepper__bell___healthy",
                    "Potato___Early_blight",
                    "Potato___healthy",
                    "Potato___Late_blight",
                    "Potato___Target_Spot",
                    "Tomato___Tomato_mosaic_virus",
                    "Tomato___Tomato_YellowLeaf_Curl_Virus",
                    "Tomato_Bacterial_spot",
                    "Tomato_Early_blight",
                    "Tomato_healthy",
                    "Tomato_Late_blight",
                    "Tomato_Leaf_Mold",
                    "Tomato_Septoria_leaf_spot",
                    "Tomato_Spider_mites_Two_spotted_spider_mite"
                ]

                logger.info("✅ Plant Disease Detection Model Loaded.")
            else:
                self.plant_disease_model = None
                logger.warning("⚠️ Plant Disease Model not found; skipping.")

            self.soil_features = ['N', 'P', 'K', 'pH', 'EC', 'OC']

        except Exception as e:
            logger.error(f"❌ Error initializing MLModelManager: {e}")

    def predict_soil_fertility(self, input_array):
        try:
            scaled_input = self.soil_scaler.transform(input_array)
            prediction_encoded = self.soil_model.predict(scaled_input)[0]
            probabilities = self.soil_model.predict_proba(scaled_input)[0]
            confidence = np.max(probabilities) * 100
            prediction = self.soil_label_encoder.inverse_transform([prediction_encoded])[0]
            return str(prediction), float(confidence)
        except Exception as e:
            logger.error(f"❌ Soil prediction error: {e}")
            return "Error", 0.0

    def get_soil_recommendations(self, fertility_class):
        recommendations = {
            "Low": ["Add organic compost", "Apply NPK fertilizers", "Use green manure"],
            "Medium": ["Maintain organic content", "Use balanced NPK fertilizers"],
            "High": ["Monitor nutrient levels", "Avoid over-fertilization"]
        }
        return recommendations.get(str(fertility_class), ["Check input values and retry."])

    def predict_crop_recommendation(self, input_array):
        try:
            scaled_input = self.crop_scaler.transform(input_array)
            prediction_encoded = self.crop_model.predict(scaled_input)[0]
            probabilities = self.crop_model.predict_proba(scaled_input)[0]
            confidence = np.max(probabilities) * 100
            prediction = self.crop_label_encoder.inverse_transform([prediction_encoded])[0]
            return str(prediction), float(confidence)
        except Exception as e:
            logger.error(f"❌ Crop recommendation error: {e}")
            return "Error", 0.0
    def get_crop_info(self, crop_name):
        crop_info_dict = {  "rice": {
                "season": "Kharif (June - November)",
                "duration": "100-150 days",
                "water_requirement": "1200-1800 mm",
                "soil_type": "Clayey loam, silt loam, well-drained"
            },
            "wheat": {
                "season": "Rabi (November - April)",
                "duration": "110-140 days",
                "water_requirement": "450-650 mm",
                "soil_type": "Loamy, clay loam, well-drained"
            },
            "maize": {
                "season": "Kharif (June - October)",
                "duration": "90-120 days",
                "water_requirement": "500-800 mm",
                "soil_type": "Loamy, alluvial, well-drained"
            },
            "sugarcane": {
                "season": "Annual (Planted February - March or September - October)",
                "duration": "10-18 months",
                "water_requirement": "1500-2500 mm",
                "soil_type": "Loamy, alluvial, well-drained, fertile"
            },
            "cotton": {
                "season": "Kharif (June - November)",
                "duration": "150-180 days",
                "water_requirement": "700-1200 mm",
                "soil_type": "Black soil, sandy loam, well-drained"
            },
            "groundnut": {
                "season": "Kharif or Rabi",
                "duration": "105-120 days",
                "water_requirement": "500-600 mm",
                "soil_type": "Sandy loam, well-drained"
            },
            "millet": {
                "season": "Kharif (June - September)",
                "duration": "70-120 days",
                "water_requirement": "300-400 mm",
                "soil_type": "Sandy loam, well-drained"
            },
            "barley": {
                "season": "Rabi (November - April)",
                "duration": "90-110 days",
                "water_requirement": "300-400 mm",
                "soil_type": "Sandy loam, well-drained"
            },
            "soybean": {
                "season": "Kharif (June - October)",
                "duration": "90-120 days",
                "water_requirement": "500-700 mm",
                "soil_type": "Loamy, clay loam, well-drained"
            },
            "bajra": {
                "season": "Kharif (June - September)",
                "duration": "75-90 days",
                "water_requirement": "350-400 mm",
                "soil_type": "Sandy loam, well-drained"
            },
            "sorghum": {
                "season": "Kharif and Rabi",
                "duration": "100-120 days",
                "water_requirement": "400-600 mm",
                "soil_type": "Loamy, clay loam, well-drained"
            },
            "turmeric": {
                "season": "Planted in April - May",
                "duration": "7-9 months",
                "water_requirement": "1500-2000 mm",
                "soil_type": "Loamy, fertile, well-drained"
            },
            "mustard": {
                "season": "Rabi (October - March)",
                "duration": "110-140 days",
                "water_requirement": "400-500 mm",
                "soil_type": "Loamy, clay loam, well-drained"
            },
            "sunflower": {
                "season": "Kharif and Rabi",
                "duration": "80-120 days",
                "water_requirement": "500-600 mm",
                "soil_type": "Loamy, well-drained"
            },
            "gram": {
                "season": "Rabi (October - April)",
                "duration": "90-100 days",
                "water_requirement": "400-500 mm",
                "soil_type": "Sandy loam, clay loam, well-drained"
            },
            "lentil": {
                "season": "Rabi (November - April)",
                "duration": "100-110 days",
                "water_requirement": "350-500 mm",
                "soil_type": "Loamy, well-drained"
            },
            "pea": {
                "season": "Rabi (October - March)",
                "duration": "90-120 days",
                "water_requirement": "400-500 mm",
                "soil_type": "Loamy, well-drained"
            },
            "cabbage": {
                "season": "Rabi and Kharif",
                "duration": "70-120 days",
                "water_requirement": "350-500 mm",
                "soil_type": "Loamy, well-drained"
            },
            "onion": {
                "season": "Kharif and Rabi",
                "duration": "100-150 days",
                "water_requirement": "600-800 mm",
                "soil_type": "Loamy, well-drained"
            },
            "potato": {
                "season": "Rabi (October - March)",
                "duration": "90-120 days",
                "water_requirement": "500-700 mm",
                "soil_type": "Sandy loam, well-drained"
            } }  # Keep your full dictionary unchanged here
        return crop_info_dict.get(
            crop_name.lower(),
            {
                "season": "Not available",
                "duration": "Not available",
                "water_requirement": "Not available",
                "soil_type": "Not available"
            }
        )

    def preprocess_image_for_disease_detection(self, img_array):
        # Convert to BGR if needed
        if img_array.shape[-1] == 4:  # RGBA
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        elif img_array.shape[-1] == 3:  # RGB
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        # Resize to (224, 224) as expected by your model
        img_resized = cv2.resize(img_array, (224, 224))

        # Normalize
        img_resized = img_resized.astype('float32') / 255.0

        # Add batch dimension
        img_resized = np.expand_dims(img_resized, axis=0)

        return img_resized

    def predict_plant_disease(self, img_array):
        try:
            img_preprocessed = self.preprocess_image_for_disease_detection(img_array)
            prediction = self.plant_disease_model.predict(img_preprocessed)
            predicted_class = np.argmax(prediction, axis=1)[0]
            confidence = float(np.max(prediction)) * 100

            disease_label = self.plant_disease_classes[predicted_class]
            return disease_label, confidence

        except Exception as e:
            logging.error(f"❌ Plant disease prediction error: {e}")
            return "Error", 0

    def get_disease_treatment(self, disease):
        treatments = {
            "Pepper__bell___healthy": "No treatment needed.",
            "Pepper__bell___Bacterial_spot": "Remove infected leaves, apply copper-based bactericide.",
            "Potato___healthy": "No treatment needed.",
            "Potato___Early_blight": "Apply recommended fungicide, remove infected foliage.",
            "Potato___Late_blight": "Use fungicides and resistant varieties.",
            "Potato___Target_Spot": "Remove affected leaves, apply fungicide.",
            "Tomato___Tomato_mosaic_virus": "Remove infected plants, control aphids.",
            "Tomato___Tomato_YellowLeaf_Curl_Virus": "Control whiteflies, remove infected plants.",
            "Tomato_Bacterial_spot": "Apply copper-based bactericides, remove infected parts.",
            "Tomato_Early_blight": "Apply fungicides, remove infected leaves.",
            "Tomato_healthy": "No treatment needed.",
            "Tomato_Late_blight": "Apply fungicides, use resistant varieties.",
            "Tomato_Leaf_Mold": "Improve air circulation, apply fungicide.",
            "Tomato_Septoria_leaf_spot": "Apply fungicide, remove infected leaves.",
            "Tomato_Spider_mites_Two_spotted_spider_mite": "Use miticides, maintain proper humidity."
        }
        return treatments.get(disease, "Consult an agronomist for appropriate treatment.")


if __name__ == '__main__':
    ml_mgr = MLModelManager()
    logger.info("✅ MLModelManager ready for testing.")
