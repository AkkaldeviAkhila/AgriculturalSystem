import os
import logging
import joblib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout

logging.basicConfig(level=logging.INFO)

model_dir = 'models'
os.makedirs(model_dir, exist_ok=True)

# Utility to save confusion matrix
def save_confusion_matrix(y_true, y_pred, labels, title, filename):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 7))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.title(title)
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.savefig(filename)
    plt.close()

# Train or evaluate Soil Fertility
try:
    soil_model_path = os.path.join(model_dir, 'soil_fertility_model.pkl')
    if os.path.exists(soil_model_path):
        logging.info("✅ Soil Fertility Model found. Loading for evaluation...")
        clf = joblib.load(soil_model_path)
        scaler = joblib.load(os.path.join(model_dir, 'soil_fertility_scaler.pkl'))
        le = joblib.load(os.path.join(model_dir, 'soil_fertility_label_encoder.pkl'))
    else:
        logging.info("⚡ Soil Fertility Model not found. Training...")
        df = pd.read_csv('datasets/soil_fertility.csv')
        X = df[['N', 'P', 'K', 'pH', 'EC', 'OC']]
        y = df['Output']

        le = LabelEncoder()
        y = le.fit_transform(y)

        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        joblib.dump(clf, soil_model_path)
        joblib.dump(scaler, os.path.join(model_dir, 'soil_fertility_scaler.pkl'))
        joblib.dump(le, os.path.join(model_dir, 'soil_fertility_label_encoder.pkl'))
        logging.info("✅ Soil Fertility Model trained and saved.")

    df = pd.read_csv('datasets/soil_fertility.csv')
    X = df[['N', 'P', 'K', 'pH', 'EC', 'OC']]
    y = le.transform(df['Output'])
    X = scaler.transform(X)
    y_pred = clf.predict(X)
    acc = accuracy_score(y, y_pred)
    logging.info(f"✅ Soil Fertility Accuracy: {acc * 100:.2f}%")
    logging.info(f"📊 Classification Report:\n{classification_report(y, y_pred, target_names=le.classes_)}")
    save_confusion_matrix(y, y_pred, le.classes_, "Soil Fertility Confusion Matrix", "soil_fertility_cm.jpg")

except Exception as e:
    logging.error(f"❌ Soil Fertility Error: {e}")

# Train or evaluate Crop Recommendation
try:
    crop_model_path = os.path.join(model_dir, 'crop_recommendation_model.pkl')
    if os.path.exists(crop_model_path):
        logging.info("✅ Crop Recommendation Model found. Loading for evaluation...")
        clf = joblib.load(crop_model_path)
        scaler = joblib.load(os.path.join(model_dir, 'crop_recommendation_scaler.pkl'))
        le = joblib.load(os.path.join(model_dir, 'crop_recommendation_label_encoder.pkl'))
    else:
        logging.info("⚡ Crop Recommendation Model not found. Training...")
        df = pd.read_csv('datasets/Crop_recommendation.csv')
        X = df.drop('label', axis=1)
        y = df['label']

        le = LabelEncoder()
        y = le.fit_transform(y)

        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        joblib.dump(clf, crop_model_path)
        joblib.dump(scaler, os.path.join(model_dir, 'crop_recommendation_scaler.pkl'))
        joblib.dump(le, os.path.join(model_dir, 'crop_recommendation_label_encoder.pkl'))
        logging.info("✅ Crop Recommendation Model trained and saved.")

    df = pd.read_csv('datasets/Crop_recommendation.csv')
    X = df.drop('label', axis=1)
    y = le.transform(df['label'])
    X = scaler.transform(X)
    y_pred = clf.predict(X)
    acc = accuracy_score(y, y_pred)
    logging.info(f"✅ Crop Recommendation Accuracy: {acc * 100:.2f}%")
    logging.info(f"📊 Classification Report:\n{classification_report(y, y_pred, target_names=le.classes_)}")
    save_confusion_matrix(y, y_pred, le.classes_, "Crop Recommendation Confusion Matrix", "crop_recommendation_cm.jpg")

except Exception as e:
    logging.error(f"❌ Crop Recommendation Error: {e}")

# Train or evaluate Plant Disease CNN
try:
    plant_model_path = os.path.join(model_dir, 'plant_disease_cnn.h5')
    if os.path.exists(plant_model_path):
        logging.info("✅ Plant Disease Model found. Loading for evaluation...")
        model = load_model(plant_model_path)
        datagen = ImageDataGenerator(rescale=1./255)
        test_gen = datagen.flow_from_directory('datasets/PlantVillage', target_size=(128, 128),
                                               batch_size=32, class_mode='categorical', shuffle=False)
        y_true = test_gen.classes
        y_pred_probs = model.predict(test_gen, verbose=1)
        y_pred = np.argmax(y_pred_probs, axis=1)
        labels = list(test_gen.class_indices.keys())
        acc = accuracy_score(y_true, y_pred)
        logging.info(f"✅ Plant Disease CNN Accuracy: {acc * 100:.2f}%")
        logging.info(f"📊 Classification Report:\n{classification_report(y_true, y_pred, target_names=labels)}")
        save_confusion_matrix(y_true, y_pred, labels, "Plant Disease Confusion Matrix", "plant_disease_cm.jpg")
    else:
        logging.info("⚡ Plant Disease Model not found. Training...")
        datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)
        train_gen = datagen.flow_from_directory('datasets/PlantVillage', target_size=(128, 128),
                                                batch_size=32, class_mode='categorical', subset='training')
        val_gen = datagen.flow_from_directory('datasets/PlantVillage', target_size=(128, 128),
                                              batch_size=32, class_mode='categorical', subset='validation')
        num_classes = len(train_gen.class_indices)
        model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 3)),
            MaxPooling2D(2, 2),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D(2, 2),
            Flatten(),
            Dense(128, activation='relu'),
            Dropout(0.5),
            Dense(num_classes, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        model.fit(train_gen, epochs=10, validation_data=val_gen)
        model.save(plant_model_path)
        logging.info("✅ Plant Disease CNN model trained and saved.")

except Exception as e:
    logging.error(f"❌ Plant Disease Error: {e}")
