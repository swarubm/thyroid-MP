from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import pandas as pd
import numpy as np
import requests
import json
import os
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///thyroid.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    age = db.Column(db.Integer)
    sex = db.Column(db.String(10))
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    predictions = db.relationship('Prediction', backref='user', lazy=True)
    health_records = db.relationship('HealthRecord', backref='user', lazy=True)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age = db.Column(db.Float)
    sex = db.Column(db.String(10))
    tsh = db.Column(db.Float)
    t3 = db.Column(db.Float)
    tt4 = db.Column(db.Float)
    t4u = db.Column(db.Float)
    on_thyroxine = db.Column(db.Boolean)
    query_on_thyroxine = db.Column(db.Boolean)
    on_antithyroid_medication = db.Column(db.Boolean)
    sick = db.Column(db.Boolean)
    pregnant = db.Column(db.Boolean)
    thyroid_surgery = db.Column(db.Boolean)
    i131_treatment = db.Column(db.Boolean)
    query_hypothyroid = db.Column(db.Boolean)
    query_hyperthyroid = db.Column(db.Boolean)
    lithium = db.Column(db.Boolean)
    goitre = db.Column(db.Boolean)
    tumor = db.Column(db.Boolean)
    hypopituitary = db.Column(db.Boolean)
    psych = db.Column(db.Boolean)
    prediction = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    record_type = db.Column(db.String(50))  # 'lab_result', 'medication', 'symptom'
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    specializations = db.Column(db.Text)  # JSON string of specializations

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load the trained model
try:
    model = joblib.load('thyroid_detection_pipeline.joblib')
except:
    # Use simple model if the file doesn't exist
    from thyroid_detection_pipeline import ThyroidPredictionPipeline
    model = ThyroidPredictionPipeline()

# Hormone Catalog
HORMONE_CATALOG = {
    'TSH': {
        'name': 'Thyroid Stimulating Hormone',
        'normal_range': '0.4 - 4.0 mIU/L',
        'description': 'Produced by pituitary gland, stimulates thyroid hormone production',
        'high_meaning': 'May indicate hypothyroidism',
        'low_meaning': 'May indicate hyperthyroidism'
    },
    'T3': {
        'name': 'Triiodothyronine',
        'normal_range': '80 - 200 ng/dL',
        'description': 'Active thyroid hormone, affects metabolism',
        'high_meaning': 'May indicate hyperthyroidism',
        'low_meaning': 'May indicate hypothyroidism'
    },
    'T4': {
        'name': 'Thyroxine',
        'normal_range': '4.5 - 11.2 μg/dL',
        'description': 'Main thyroid hormone, precursor to T3',
        'high_meaning': 'May indicate hyperthyroidism',
        'low_meaning': 'May indicate hypothyroidism'
    },
    'FT4': {
        'name': 'Free Thyroxine',
        'normal_range': '0.8 - 1.8 ng/dL',
        'description': 'Unbound T4, more accurate indicator',
        'high_meaning': 'May indicate hyperthyroidism',
        'low_meaning': 'May indicate hypothyroidism'
    }
}

# Diet Recommendations
DIET_RECOMMENDATIONS = {
    'hypothyroid': {
        'general': [
            'Increase iodine-rich foods (seafood, dairy, eggs)',
            'Include selenium-rich foods (Brazil nuts, tuna, sardines)',
            'Eat zinc-rich foods (oysters, beef, pumpkin seeds)',
            'Consume vitamin D (fatty fish, fortified dairy)',
            'Include fiber-rich foods for digestive health'
        ],
        'avoid': [
            'Goitrogenic foods in excess (cabbage, broccoli, soy)',
            'Processed foods high in sodium',
            'Excessive caffeine and alcohol'
        ]
    },
    'hyperthyroid': {
        'general': [
            'Eat calcium-rich foods (dairy, leafy greens)',
            'Include vitamin D sources',
            'Consume anti-inflammatory foods (omega-3 rich fish)',
            'Eat small, frequent meals',
            'Stay hydrated'
        ],
        'avoid': [
            'Iodine-rich foods in excess',
            'Caffeine and stimulants',
            'Alcohol',
            'Large meals'
        ]
    },
    'pregnant': {
        'general': [
            'Increase folic acid (leafy greens, fortified grains)',
            'Eat iron-rich foods (lean meat, beans, spinach)',
            'Include calcium sources (dairy, fortified foods)',
            'Consume omega-3 fatty acids (low-mercury fish)',
            'Eat protein-rich foods'
        ],
        'avoid': [
            'Raw fish and undercooked meat',
            'Unpasteurized dairy',
            'Excessive caffeine',
            'Alcohol',
            'High-mercury fish'
        ]
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).limit(5).all()
    health_records = HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         predictions=user_predictions, 
                         health_records=health_records)

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('dashboard'))
    
    total_users = User.query.count()
    total_predictions = Prediction.query.count()
    recent_predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_predictions=total_predictions,
                         recent_predictions=recent_predictions,
                         recent_users=recent_users)

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        # Get form data
        data = {
            'age': float(request.form['age']),
            'sex': request.form['sex'],
            'TSH': float(request.form['tsh']),
            'T3': float(request.form['t3']),
            'TT4': float(request.form['tt4']),
            'T4U': float(request.form['t4u']),
            'on_thyroxine': request.form.get('on_thyroxine') == 'on',
            'query_on_thyroxine': request.form.get('query_on_thyroxine') == 'on',
            'on_antithyroid_medication': request.form.get('on_antithyroid_medication') == 'on',
            'sick': request.form.get('sick') == 'on',
            'pregnant': request.form.get('pregnant') == 'on',
            'thyroid_surgery': request.form.get('thyroid_surgery') == 'on',
            'I131_treatment': request.form.get('i131_treatment') == 'on',
            'query_hypothyroid': request.form.get('query_hypothyroid') == 'on',
            'query_hyperthyroid': request.form.get('query_hyperthyroid') == 'on',
            'lithium': request.form.get('lithium') == 'on',
            'goitre': request.form.get('goitre') == 'on',
            'tumor': request.form.get('tumor') == 'on',
            'hypopituitary': request.form.get('hypopituitary') == 'on',
            'psych': request.form.get('psych') == 'on'
        }
        
        # Prepare data for prediction
        df = pd.DataFrame([data])
        
        # Make prediction
        try:
            if hasattr(model, 'predict') and callable(getattr(model, 'predict')):
                if hasattr(model, 'predict_proba'):
                    # Standard sklearn model
                    prediction = model.predict(df)[0]
                    confidence = max(model.predict_proba(df)[0])
                else:
                    # Our simple model
                    prediction, confidence = model.predict(data)
            else:
                # Fallback
                prediction = 'negative'
                confidence = 0.8
            
            # Save prediction to database
            pred_record = Prediction(
                user_id=current_user.id,
                age=data['age'],
                sex=data['sex'],
                tsh=data['TSH'],
                t3=data['T3'],
                tt4=data['TT4'],
                t4u=data['T4U'],
                on_thyroxine=data['on_thyroxine'],
                query_on_thyroxine=data['query_on_thyroxine'],
                on_antithyroid_medication=data['on_antithyroid_medication'],
                sick=data['sick'],
                pregnant=data['pregnant'],
                thyroid_surgery=data['thyroid_surgery'],
                i131_treatment=data['I131_treatment'],
                query_hypothyroid=data['query_hypothyroid'],
                query_hyperthyroid=data['query_hyperthyroid'],
                lithium=data['lithium'],
                goitre=data['goitre'],
                tumor=data['tumor'],
                hypopituitary=data['hypopituitary'],
                psych=data['psych'],
                prediction=prediction,
                confidence=confidence
            )
            db.session.add(pred_record)
            db.session.commit()
            
            return render_template('prediction_result.html', 
                                 prediction=prediction, 
                                 confidence=confidence,
                                 data=data)
        
        except Exception as e:
            flash(f'Prediction error: {str(e)}')
            return redirect(url_for('predict'))
    
    return render_template('predict.html', hormone_catalog=HORMONE_CATALOG)

@app.route('/hormone_catalog')
def hormone_catalog():
    return render_template('hormone_catalog.html', hormones=HORMONE_CATALOG)

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_message = request.json.get('message', '')
        
        # Simple chatbot responses
        responses = {
            'hello': 'Hello! I\'m your thyroid health assistant. How can I help you today?',
            'symptoms': 'Common thyroid symptoms include fatigue, weight changes, mood swings, and temperature sensitivity. Would you like to know more about specific symptoms?',
            'test': 'Thyroid tests typically include TSH, T3, T4, and sometimes antibodies. You can use our prediction tool to analyze your results.',
            'diet': 'Diet recommendations depend on your thyroid condition. I can provide personalized recommendations based on your diagnosis.',
            'hospital': 'I can help you find nearby hospitals. Please share your location or enable GPS.',
            'help': 'I can help with thyroid information, symptom analysis, diet recommendations, and finding healthcare providers. What would you like to know?'
        }
        
        # Simple keyword matching
        response = "I'm here to help with thyroid health questions. You can ask about symptoms, tests, diet, or finding hospitals."
        for keyword, reply in responses.items():
            if keyword in user_message.lower():
                response = reply
                break
        
        return jsonify({'response': response})
    
    return render_template('chatbot.html')

@app.route('/find_hospitals', methods=['GET', 'POST'])
@login_required
def find_hospitals():
    if request.method == 'POST':
        location = request.form.get('location', '')
        
        # Use geopy to get coordinates
        geolocator = Nominatim(user_agent="thyroid_app")
        try:
            location_data = geolocator.geocode(location)
            if location_data:
                lat, lon = location_data.latitude, location_data.longitude
                
                # Search for hospitals using OpenStreetMap API
                hospitals = []
                search_url = f"https://nominatim.openstreetmap.org/search"
                params = {
                    'q': 'hospital',
                    'format': 'json',
                    'lat': lat,
                    'lon': lon,
                    'radius': 5000,  # 5km radius
                    'limit': 10
                }
                
                response = requests.get(search_url, params=params)
                if response.status_code == 200:
                    results = response.json()
                    for result in results:
                        hospitals.append({
                            'name': result.get('display_name', '').split(',')[0],
                            'address': result.get('display_name', ''),
                            'distance': geodesic((lat, lon), (float(result['lat']), float(result['lon']))).kilometers
                        })
                
                return render_template('hospitals.html', hospitals=hospitals, location=location)
            else:
                flash('Location not found. Please try a different location.')
        except Exception as e:
            flash(f'Error finding hospitals: {str(e)}')
    
    return render_template('find_hospitals.html')

@app.route('/diet_recommendations')
@login_required
def diet_recommendations():
    # Get user's latest prediction
    latest_prediction = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).first()
    
    recommendations = {}
    if latest_prediction:
        if latest_prediction.prediction == 'primary_hypothyroid' or latest_prediction.prediction == 'compensated_hypothyroid':
            recommendations['condition'] = 'hypothyroid'
        elif 'hyper' in latest_prediction.prediction:
            recommendations['condition'] = 'hyperthyroid'
        else:
            recommendations['condition'] = 'normal'
    
    # Check if user is pregnant
    if latest_prediction and latest_prediction.pregnant:
        recommendations['pregnant'] = True
    
    return render_template('diet_recommendations.html', 
                         recommendations=recommendations,
                         diet_data=DIET_RECOMMENDATIONS)

@app.route('/upload_health_record', methods=['GET', 'POST'])
@login_required
def upload_health_record():
    if request.method == 'POST':
        record_type = request.form['record_type']
        title = request.form['title']
        description = request.form['description']
        
        # Handle file upload
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                # Save file (in production, use cloud storage)
                filename = f"uploads/{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
                os.makedirs('uploads', exist_ok=True)
                file.save(filename)
                file_path = filename
        
        record = HealthRecord(
            user_id=current_user.id,
            record_type=record_type,
            title=title,
            description=description,
            file_path=file_path
        )
        db.session.add(record)
        db.session.commit()
        
        flash('Health record uploaded successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('upload_health_record.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.age = int(request.form['age'])
        current_user.sex = request.form['sex']
        current_user.location = request.form['location']
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))
    
    return render_template('profile.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@thyroid.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True)