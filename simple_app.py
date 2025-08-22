#!/usr/bin/env python3
"""
Simplified Thyroid Prediction Website
This version runs with minimal dependencies for demonstration purposes.
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Simple in-memory storage (in a real app, you'd use a database)
users = {
    'admin': {
        'password': 'admin123',
        'email': 'admin@thyroid.com',
        'is_admin': True,
        'age': 30,
        'sex': 'Male',
        'location': 'New York'
    }
}

predictions = []
health_records = []

# Simple thyroid prediction model
class SimpleThyroidPredictor:
    def predict(self, data):
        """Simple rule-based thyroid prediction"""
        tsh = data.get('tsh', 0)
        t3 = data.get('t3', 0)
        tt4 = data.get('tt4', 0)
        t4u = data.get('t4u', 0)
        
        # Simple rules based on hormone levels
        if tsh > 4.5:
            if t3 < 0.8 or tt4 < 5.0:
                return 'primary_hypothyroid', 0.85
            else:
                return 'compensated_hypothyroid', 0.75
        elif tsh < 0.3:
            if t3 > 2.0 or tt4 > 12.0:
                return 'primary_hyperthyroid', 0.80
            else:
                return 'compensated_hyperthyroid', 0.70
        else:
            return 'negative', 0.90

predictor = SimpleThyroidPredictor()

# Routes
@app.route('/')
def index():
    return render_template('index_simple.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password:
            session['user'] = username
            session['is_admin'] = users[username]['is_admin']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login_simple.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_predictions = [p for p in predictions if p['user'] == session['user']]
    user_records = [r for r in health_records if r['user'] == session['user']]
    
    return render_template('dashboard_simple.html', 
                         user=users[session['user']],
                         predictions=user_predictions[-5:],
                         health_records=user_records[-5:])

@app.route('/admin')
def admin_dashboard():
    if 'user' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    return render_template('admin_dashboard_simple.html',
                         total_users=len(users),
                         total_predictions=len(predictions))

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get form data
        data = {
            'age': float(request.form.get('age', 30)),
            'sex': request.form.get('sex', 'Male'),
            'tsh': float(request.form.get('tsh', 2.0)),
            't3': float(request.form.get('t3', 1.2)),
            'tt4': float(request.form.get('tt4', 8.0)),
            't4u': float(request.form.get('t4u', 1.0)),
            'on_thyroxine': 'on_thyroxine' in request.form,
            'sick': 'sick' in request.form,
            'pregnant': 'pregnant' in request.form,
            'thyroid_surgery': 'thyroid_surgery' in request.form
        }
        
        # Make prediction
        prediction, confidence = predictor.predict(data)
        
        # Save prediction
        pred_record = {
            'id': len(predictions) + 1,
            'user': session['user'],
            'prediction': prediction,
            'confidence': confidence,
            'data': data,
            'created_at': datetime.now().isoformat()
        }
        predictions.append(pred_record)
        
        return render_template('prediction_result.html', 
                             prediction=prediction,
                             confidence=confidence,
                             data=data)
    
    return render_template('predict.html')

@app.route('/hormone_catalog')
def hormone_catalog():
    return render_template('hormone_catalog.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').lower()
    
    # Simple chatbot responses
    responses = {
        'hello': 'Hello! I\'m your thyroid health assistant. How can I help you today?',
        'help': 'I can help you with thyroid predictions, hormone information, diet recommendations, and finding hospitals. What would you like to know?',
        'tsh': 'TSH (Thyroid Stimulating Hormone) is produced by the pituitary gland. Normal range is 0.4-4.5 mIU/L.',
        't3': 'T3 (Triiodothyronine) is the active thyroid hormone. Normal range is 0.8-2.0 ng/mL.',
        't4': 'T4 (Thyroxine) is the main thyroid hormone. Normal range is 5.0-12.0 μg/dL.',
        'hypothyroid': 'Hypothyroidism occurs when your thyroid doesn\'t produce enough hormones. Symptoms include fatigue, weight gain, and cold sensitivity.',
        'hyperthyroid': 'Hyperthyroidism occurs when your thyroid produces too much hormone. Symptoms include weight loss, rapid heartbeat, and anxiety.'
    }
    
    for key, response in responses.items():
        if key in message:
            return jsonify({'response': response})
    
    return jsonify({'response': 'I\'m here to help with thyroid health questions. Try asking about TSH, T3, T4, hypothyroidism, or hyperthyroidism.'})

@app.route('/find_hospitals')
def find_hospitals():
    return render_template('find_hospitals.html')

@app.route('/api/hospitals')
def get_hospitals():
    # Sample hospital data
    hospitals = [
        {
            'name': 'City General Hospital',
            'address': '123 Main St, Downtown',
            'distance': '2.3 km',
            'phone': '+1-555-0123'
        },
        {
            'name': 'Medical Center',
            'address': '456 Oak Ave, Midtown',
            'distance': '4.1 km',
            'phone': '+1-555-0456'
        },
        {
            'name': 'Community Health Clinic',
            'address': '789 Pine Rd, Uptown',
            'distance': '6.7 km',
            'phone': '+1-555-0789'
        }
    ]
    return jsonify(hospitals)

@app.route('/diet_recommendations')
def diet_recommendations():
    condition = request.args.get('condition', 'hypothyroid')
    pregnant = request.args.get('pregnant', 'false') == 'true'
    
    return render_template('diet_recommendations.html', 
                         condition=condition,
                         pregnant=pregnant)

@app.route('/upload_health_record', methods=['GET', 'POST'])
def upload_health_record():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        record = {
            'id': len(health_records) + 1,
            'user': session['user'],
            'title': request.form.get('title', 'Health Record'),
            'description': request.form.get('description', ''),
            'record_type': request.form.get('record_type', 'lab_result'),
            'created_at': datetime.now().isoformat()
        }
        health_records.append(record)
        flash('Health record uploaded successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('upload_health_record.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=users[session['user']])

if __name__ == '__main__':
    print("Starting Thyroid Prediction Website...")
    print("Access the website at: http://localhost:5000")
    print("Admin login: username=admin, password=admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)