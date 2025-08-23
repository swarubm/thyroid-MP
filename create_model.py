#!/usr/bin/env python3
"""
Script to create a simple thyroid prediction model for demonstration purposes.
This creates a basic model that can be used with the Flask application.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

def create_sample_data():
    """Create sample thyroid data for demonstration"""
    np.random.seed(42)
    n_samples = 1000
    
    # Generate sample data
    data = {
        'age': np.random.normal(45, 15, n_samples).astype(int),
        'sex': np.random.choice(['M', 'F'], n_samples),
        'TSH': np.random.lognormal(0.5, 0.8, n_samples),
        'T3': np.random.normal(140, 30, n_samples),
        'TT4': np.random.normal(8, 2, n_samples),
        'T4U': np.random.normal(1.0, 0.2, n_samples),
        'on_thyroxine': np.random.choice([True, False], n_samples, p=[0.3, 0.7]),
        'query_on_thyroxine': np.random.choice([True, False], n_samples, p=[0.1, 0.9]),
        'on_antithyroid_medication': np.random.choice([True, False], n_samples, p=[0.1, 0.9]),
        'sick': np.random.choice([True, False], n_samples, p=[0.2, 0.8]),
        'pregnant': np.random.choice([True, False], n_samples, p=[0.1, 0.9]),
        'thyroid_surgery': np.random.choice([True, False], n_samples, p=[0.1, 0.9]),
        'I131_treatment': np.random.choice([True, False], n_samples, p=[0.05, 0.95]),
        'query_hypothyroid': np.random.choice([True, False], n_samples, p=[0.2, 0.8]),
        'query_hyperthyroid': np.random.choice([True, False], n_samples, p=[0.1, 0.9]),
        'lithium': np.random.choice([True, False], n_samples, p=[0.05, 0.95]),
        'goitre': np.random.choice([True, False], n_samples, p=[0.1, 0.9]),
        'tumor': np.random.choice([True, False], n_samples, p=[0.05, 0.95]),
        'hypopituitary': np.random.choice([True, False], n_samples, p=[0.02, 0.98]),
        'psych': np.random.choice([True, False], n_samples, p=[0.1, 0.9])
    }
    
    df = pd.DataFrame(data)
    
    # Ensure age is within reasonable bounds
    df['age'] = df['age'].clip(18, 90)
    
    # Create target variable based on TSH levels and other factors
    def create_target(row):
        if row['TSH'] > 4.0 and row['TT4'] < 4.5:
            return 'primary_hypothyroid'
        elif row['TSH'] > 4.0 and row['TT4'] >= 4.5:
            return 'compensated_hypothyroid'
        elif row['TSH'] < 0.4 and row['TT4'] > 11.2:
            return 'primary_hyperthyroid'
        else:
            return 'negative'
    
    df['disease'] = df.apply(create_target, axis=1)
    
    return df

def prepare_features(df):
    """Prepare features for the model"""
    # Convert sex to numeric
    df['sex_numeric'] = df['sex'].map({'M': 1, 'F': 0})
    
    # Select features
    feature_columns = [
        'age', 'sex_numeric', 'TSH', 'T3', 'TT4', 'T4U',
        'on_thyroxine', 'query_on_thyroxine', 'on_antithyroid_medication',
        'sick', 'pregnant', 'thyroid_surgery', 'I131_treatment',
        'query_hypothyroid', 'query_hyperthyroid', 'lithium',
        'goitre', 'tumor', 'hypopituitary', 'psych'
    ]
    
    # Convert boolean columns to int
    boolean_columns = [
        'on_thyroxine', 'query_on_thyroxine', 'on_antithyroid_medication',
        'sick', 'pregnant', 'thyroid_surgery', 'I131_treatment',
        'query_hypothyroid', 'query_hyperthyroid', 'lithium',
        'goitre', 'tumor', 'hypopituitary', 'psych'
    ]
    
    for col in boolean_columns:
        df[col] = df[col].astype(int)
    
    return df[feature_columns], df['disease']

def create_model():
    """Create and train the thyroid prediction model"""
    print("Creating sample thyroid data...")
    df = create_sample_data()
    
    print("Preparing features...")
    X, y = prepare_features(df)
    
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate model
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Training accuracy: {train_score:.3f}")
    print(f"Testing accuracy: {test_score:.3f}")
    
    # Create a simple pipeline for the Flask app
    class ThyroidPredictionPipeline:
        def __init__(self, model):
            self.model = model
            self.feature_names = [
                'age', 'sex', 'TSH', 'T3', 'TT4', 'T4U',
                'on_thyroxine', 'query_on_thyroxine', 'on_antithyroid_medication',
                'sick', 'pregnant', 'thyroid_surgery', 'I131_treatment',
                'query_hypothyroid', 'query_hyperthyroid', 'lithium',
                'goitre', 'tumor', 'hypopituitary', 'psych'
            ]
        
        def predict(self, data):
            """Make prediction on input data"""
            # Convert input data to feature vector
            features = []
            for feature in self.feature_names:
                if feature == 'sex':
                    features.append(1 if data[feature] == 'M' else 0)
                elif feature in ['on_thyroxine', 'query_on_thyroxine', 'on_antithyroid_medication',
                               'sick', 'pregnant', 'thyroid_surgery', 'I131_treatment',
                               'query_hypothyroid', 'query_hyperthyroid', 'lithium',
                               'goitre', 'tumor', 'hypopituitary', 'psych']:
                    features.append(1 if data[feature] else 0)
                else:
                    features.append(data[feature])
            
            # Make prediction
            prediction = self.model.predict([features])[0]
            probabilities = self.model.predict_proba([features])[0]
            confidence = max(probabilities)
            
            return prediction, confidence
        
        def predict_proba(self, data):
            """Get prediction probabilities"""
            features = []
            for feature in self.feature_names:
                if feature == 'sex':
                    features.append(1 if data[feature] == 'M' else 0)
                elif feature in ['on_thyroxine', 'query_on_thyroxine', 'on_antithyroid_medication',
                               'sick', 'pregnant', 'thyroid_surgery', 'I131_treatment',
                               'query_hypothyroid', 'query_hyperthyroid', 'lithium',
                               'goitre', 'tumor', 'hypopituitary', 'psych']:
                    features.append(1 if data[feature] else 0)
                else:
                    features.append(data[feature])
            
            return self.model.predict_proba([features])[0]
    
    pipeline = ThyroidPredictionPipeline(model)
    
    # Save the model
    print("Saving model...")
    joblib.dump(pipeline, 'thyroid_detection_pipeline.joblib')
    
    print("Model saved as 'thyroid_detection_pipeline.joblib'")
    print("Model creation completed successfully!")
    
    return pipeline

if __name__ == "__main__":
    create_model()