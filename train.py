# train_models.py

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import logging

def train_and_save_soil_fertility():
    df = pd.read_csv('datasets/soil_fertility.csv')
    X = df[['N', 'P', 'K', 'pH', 'EC', 'OC']]
    y = df['Output']

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=label_encoder.classes_.astype(str))

    print(f"\n✅ Soil Fertility Model Accuracy: {acc*100:.2f}%")
    print("📊 Classification Report:\n", report)
    print("📊 Confusion Matrix:\n", cm)

    # Save confusion matrix
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
    plt.title('Soil Fertility Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    plt.savefig('reports/soil_fertility_confusion_matrix.jpg')
    plt.close()
    print("🖼️ Confusion matrix saved as 'reports/soil_fertility_confusion_matrix.jpg'")

    model_dir = 'models'
    joblib.dump(clf, os.path.join(model_dir, 'soil_fertility_model.pkl'))
    joblib.dump(scaler, os.path.join(model_dir, 'soil_fertility_scaler.pkl'))
    joblib.dump(label_encoder, os.path.join(model_dir, 'soil_fertility_label_encoder.pkl'))

def train_and_save_crop_recommendation():
    df = pd.read_csv('datasets/Crop_recommendation.csv')
    X = df.drop('label', axis=1)
    y = df['label']

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=label_encoder.classes_)

    print(f"\n✅ Crop Recommendation Model Accuracy: {acc*100:.2f}%")
    print("📊 Classification Report:\n", report)
    print("📊 Confusion Matrix:\n", cm)

    # Save confusion matrix
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
    plt.title('Crop Recommendation Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    plt.savefig('reports/crop_recommendation_confusion_matrix.jpg')
    plt.close()
    print("🖼️ Confusion matrix saved as 'reports/crop_recommendation_confusion_matrix.jpg'")

    model_dir = 'models'
    joblib.dump(clf, os.path.join(model_dir, 'crop_recommendation_model.pkl'))
    joblib.dump(scaler, os.path.join(model_dir, 'crop_recommendation_scaler.pkl'))
    joblib.dump(label_encoder, os.path.join(model_dir, 'crop_recommendation_label_encoder.pkl'))

if __name__ == '__main__':
    os.makedirs('models', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    logging.basicConfig(level=logging.INFO)

    print("\n🚀 Starting model training for Smart Agriculture System...")
    train_and_save_soil_fertility()
    train_and_save_crop_recommendation()
    print("\n✅ All models trained, saved, and confusion matrices exported successfully.")
