"""
Simple Thyroid Prediction Model
This is a basic implementation for demonstration purposes.
In production, you would use a properly trained machine learning model.
"""

import random
import math

class ThyroidPredictionPipeline:
    """Simple thyroid prediction pipeline for demonstration"""
    
    def __init__(self):
        self.feature_names = [
            'age', 'sex', 'TSH', 'T3', 'TT4', 'T4U',
            'on_thyroxine', 'query_on_thyroxine', 'on_antithyroid_medication',
            'sick', 'pregnant', 'thyroid_surgery', 'I131_treatment',
            'query_hypothyroid', 'query_hyperthyroid', 'lithium',
            'goitre', 'tumor', 'hypopituitary', 'psych'
        ]
    
    def predict(self, data):
        """Make prediction based on thyroid hormone levels and symptoms"""
        # Simple rule-based prediction
        tsh = data.get('TSH', 2.0)
        t3 = data.get('T3', 120)
        tt4 = data.get('TT4', 8.0)
        t4u = data.get('T4U', 1.0)
        
        # Basic thyroid condition logic
        if tsh > 4.0 and tt4 < 4.5:
            prediction = 'primary_hypothyroid'
            confidence = min(0.95, 0.7 + (tsh - 4.0) * 0.1)
        elif tsh > 4.0 and tt4 >= 4.5:
            prediction = 'compensated_hypothyroid'
            confidence = min(0.90, 0.6 + (tsh - 4.0) * 0.08)
        elif tsh < 0.4 and tt4 > 11.2:
            prediction = 'primary_hyperthyroid'
            confidence = min(0.92, 0.75 + (11.2 - tt4) * 0.05)
        elif tsh < 0.4 and t3 > 200:
            prediction = 'primary_hyperthyroid'
            confidence = min(0.88, 0.7 + (200 - t3) * 0.002)
        else:
            prediction = 'negative'
            confidence = 0.85
        
        # Adjust confidence based on other factors
        if data.get('pregnant', False):
            confidence *= 0.9  # Pregnancy can affect thyroid levels
        
        if data.get('on_thyroxine', False):
            confidence *= 0.95  # Medication can affect readings
        
        if data.get('sick', False):
            confidence *= 0.8  # Illness can affect thyroid function
        
        return prediction, max(0.5, confidence)
    
    def predict_proba(self, data):
        """Get prediction probabilities for all classes"""
        prediction, confidence = self.predict(data)
        
        # Create probability distribution
        classes = ['negative', 'primary_hypothyroid', 'compensated_hypothyroid', 'primary_hyperthyroid']
        probabilities = [0.1, 0.1, 0.1, 0.1]  # Base probabilities
        
        # Set high probability for predicted class
        if prediction in classes:
            idx = classes.index(prediction)
            probabilities[idx] = confidence
            # Distribute remaining probability
            remaining = 1.0 - confidence
            for i in range(len(probabilities)):
                if i != idx:
                    probabilities[i] = remaining / (len(probabilities) - 1)
        
        return probabilities

# Create a simple model instance
model = ThyroidPredictionPipeline()

# Example usage:
if __name__ == "__main__":
    # Test the model
    test_data = {
        'age': 35,
        'sex': 'F',
        'TSH': 5.2,
        'T3': 110,
        'TT4': 3.8,
        'T4U': 0.9,
        'on_thyroxine': False,
        'query_on_thyroxine': False,
        'on_antithyroid_medication': False,
        'sick': False,
        'pregnant': False,
        'thyroid_surgery': False,
        'I131_treatment': False,
        'query_hypothyroid': True,
        'query_hyperthyroid': False,
        'lithium': False,
        'goitre': False,
        'tumor': False,
        'hypopituitary': False,
        'psych': False
    }
    
    prediction, confidence = model.predict(test_data)
    probabilities = model.predict_proba(test_data)
    
    print(f"Prediction: {prediction}")
    print(f"Confidence: {confidence:.2f}")
    print(f"Probabilities: {probabilities}")