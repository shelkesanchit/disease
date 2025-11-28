# Disease Detection & Farm Planning Application

A comprehensive Flask-based web application for grape disease detection, farm planning, and agricultural consultancy.

## Features

- 🍇 Grape disease detection using ML models
- 🌾 Farm planning and management
- 🌦️ Weather-based farming recommendations
- 👨‍🌾 Consultant-farmer connection system
- 🛒 E-commerce for agricultural products
- 🤖 AI-powered chatbot for farming queries

## Tech Stack

- **Backend**: Flask, Python 3.12
- **Database**: MongoDB Atlas
- **ML/AI**: TensorFlow, Keras, Google Gemini API
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Render

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd disease
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your actual API keys and credentials:
     ```
     MONGO_URI=your_mongodb_connection_string
     OPENWEATHER_API_KEY=your_openweather_key
     GEMINI_API_KEY=your_gemini_key
     GROQ_API_KEY=your_groq_key
     FLASK_SECRET_KEY=your_secret_key
     ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open browser: `http://localhost:5000`

## Deployment to Render

### Prerequisites
- GitHub account
- Render account (free tier available)
- All API keys ready

### Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: Your app name
     - **Environment**: Python 3
     - **Build Command**: `chmod +x build.sh && ./build.sh`
     - **Start Command**: `gunicorn app:app`
     - **Instance Type**: Free

3. **Add Environment Variables in Render**
   - In Render dashboard, go to "Environment"
   - Add all variables from your `.env` file:
     - `MONGO_URI`
     - `OPENWEATHER_API_KEY`
     - `OPENWEATHER_API_KEY_2`
     - `GEMINI_API_KEY`
     - `GEMINI_API_KEY_2`
     - `GROQ_API_KEY`
     - `FLASK_SECRET_KEY`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (first deployment takes 5-10 minutes)
   - Your app will be live at: `https://your-app-name.onrender.com`

## Project Structure

```
disease/
├── app.py                 # Main Flask application
├── models.py             # Database models and operations
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
├── Procfile             # Render deployment config
├── runtime.txt          # Python version
├── build.sh             # Build script for Render
├── .env                 # Environment variables (not in git)
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore file
├── templates/           # HTML templates
├── static/              # Static files (CSS, JS, images)
├── uploads/             # Uploaded images
└── instance/            # Instance-specific data
```

## Required Model Files

Ensure these ML model files are present:
- `grape_model.h5` - Grape disease detection
- `grape_leaf_disease_model.h5` - Grape leaf disease
- `scaler.pkl` - Data scaler
- `label_encoder.pkl` - Label encoder

**Note**: `apple_disease.h5` has been disabled and can be deleted.

## API Keys Required

- **MongoDB Atlas**: Database connection
- **OpenWeather API**: Weather data
- **Google Gemini API**: AI recommendations
- **Groq API**: Chatbot functionality

## Troubleshooting

### Build fails on Render
- Check if all environment variables are set
- Verify `requirements.txt` has all dependencies
- Check build logs in Render dashboard

### App crashes after deployment
- Check application logs in Render
- Verify MongoDB connection string is correct
- Ensure all API keys are valid

### Static files not loading
- Check if directories are created in `build.sh`
- Verify file paths use `os.path.join()`

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.
