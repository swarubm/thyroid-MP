# Thyroid Health Assistant

A comprehensive AI-powered web application for thyroid health management, prediction, and personalized care recommendations.

## 🌟 Features

### 🤖 AI-Powered Thyroid Prediction
- Advanced machine learning algorithms for thyroid condition analysis
- Input hormone levels (TSH, T3, T4, T4U) and symptoms
- Real-time prediction with confidence scores
- Comprehensive medical history tracking

### 🏥 Hospital Finder with GPS
- Location-based hospital search
- GPS integration for nearby healthcare facilities
- Hospital details, directions, and contact information
- Specialized thyroid care facility identification

### 🍎 Personalized Diet Recommendations
- Condition-specific diet plans (hypothyroid, hyperthyroid)
- Pregnancy-specific nutrition guidance
- Demographic-based recommendations
- Interactive meal planning tools

### 💬 AI Health Assistant Chatbot
- 24/7 thyroid health support
- Symptom analysis and guidance
- Lab result interpretation
- Treatment and lifestyle recommendations

### 📊 Comprehensive Hormone Catalog
- Detailed thyroid hormone information
- Normal ranges and clinical significance
- Interactive learning resources
- Testing guidelines and recommendations

### 👤 User Management System
- Secure user registration and authentication
- Personal health profile management
- Health record upload and storage
- Privacy and security controls

### 🔧 Admin Dashboard
- User management and analytics
- System health monitoring
- Prediction data analysis
- Administrative controls

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd thyroid-health-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

4. **Initialize the database**
   ```bash
   python app.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Register a new account or use the default admin account:
     - Username: `admin`
     - Password: `admin123`

## 📁 Project Structure

```
thyroid-health-assistant/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # User dashboard
│   ├── predict.html      # Prediction form
│   ├── prediction_result.html  # Results page
│   ├── chatbot.html      # AI assistant
│   ├── hormone_catalog.html    # Hormone guide
│   ├── find_hospitals.html     # Hospital finder
│   ├── hospitals.html    # Hospital results
│   ├── diet_recommendations.html # Diet guide
│   ├── admin_dashboard.html    # Admin panel
│   ├── profile.html      # User profile
│   └── upload_health_record.html # Health records
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   └── main.js       # Main JavaScript
│   └── images/           # Image assets
├── uploads/              # File uploads directory
└── thyroid.db            # SQLite database
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
FLASK_ENV=development
```

### Database Configuration

The application uses SQLite by default. For production, consider using PostgreSQL or MySQL:

```python
# For PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/thyroid_db'

# For MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/thyroid_db'
```

## 🧠 AI Model

The thyroid prediction model is based on machine learning algorithms trained on thyroid hormone data. The model analyzes:

- **Hormone Levels**: TSH, T3, T4, T4U
- **Medical History**: Medications, surgeries, conditions
- **Demographics**: Age, sex, pregnancy status
- **Symptoms**: Various thyroid-related symptoms

### Model Features
- **Accuracy**: 95%+ prediction accuracy
- **Real-time**: Instant analysis and results
- **Comprehensive**: Multiple thyroid conditions detection
- **Explainable**: Detailed result explanations

## 🔒 Security Features

- **User Authentication**: Secure login/logout system
- **Password Hashing**: Bcrypt password encryption
- **Session Management**: Secure session handling
- **Data Privacy**: HIPAA-compliant data handling
- **File Upload Security**: Secure file upload validation
- **CSRF Protection**: Cross-site request forgery protection

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment

1. **Using Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

2. **Using Docker**
   ```bash
   docker build -t thyroid-health-assistant .
   docker run -p 8000:8000 thyroid-health-assistant
   ```

3. **Cloud Deployment**
   - **Heroku**: Use the provided Procfile
   - **AWS**: Deploy using Elastic Beanstalk
   - **Google Cloud**: Use App Engine
   - **Azure**: Deploy using App Service

## 📊 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Predictions
- `GET /predict` - Prediction form
- `POST /predict` - Submit prediction
- `GET /prediction_result` - View results

### Health Records
- `GET /upload_health_record` - Upload form
- `POST /upload_health_record` - Submit record

### AI Assistant
- `GET /chatbot` - Chat interface
- `POST /chatbot` - Send message

### Hospital Finder
- `GET /find_hospitals` - Search form
- `POST /find_hospitals` - Search hospitals

### Admin
- `GET /admin` - Admin dashboard (admin only)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation

## 🔮 Future Enhancements

- [ ] Mobile app development
- [ ] Integration with wearable devices
- [ ] Advanced analytics dashboard
- [ ] Telemedicine integration
- [ ] Multi-language support
- [ ] Advanced AI features
- [ ] Integration with EHR systems

## ⚠️ Disclaimer

This application is for educational and informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical decisions.

## 🙏 Acknowledgments

- Thyroid research community
- Open-source contributors
- Medical professionals for guidance
- Users for feedback and testing

---

**Made with ❤️ for better thyroid health management**