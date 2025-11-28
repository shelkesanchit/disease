# Deployment Guide for Render

## Quick Deployment Steps

### 1. Prepare Your Code

Make sure you have:
- ✅ `.env` file with all your API keys (don't commit this)
- ✅ `.env.example` as a template
- ✅ `requirements.txt` with all dependencies
- ✅ `Procfile` for Render
- ✅ `build.sh` build script
- ✅ `.gitignore` to exclude sensitive files

### 2. Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Render deployment"

# Create main branch
git branch -M main

# Add your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git push -u origin main
```

### 3. Deploy on Render

1. **Sign up/Login to Render**: https://render.com/

2. **Create New Web Service**:
   - Click "New +" button
   - Select "Web Service"
   - Connect your GitHub account
   - Select your repository

3. **Configure Service**:
   ```
   Name: disease-detection-app (or your preferred name)
   Environment: Python 3
   Region: Choose nearest to your users
   Branch: main
   Build Command: chmod +x build.sh && ./build.sh
   Start Command: gunicorn app:app
   ```

4. **Select Plan**:
   - Choose "Free" for testing
   - Or "Starter" for production ($7/month)

5. **Add Environment Variables**:
   Click "Advanced" → "Add Environment Variable"
   
   Add these variables:
   ```
   MONGO_URI = your_mongodb_atlas_connection_string
   OPENWEATHER_API_KEY = your_openweather_key
   OPENWEATHER_API_KEY_2 = your_second_openweather_key
   GEMINI_API_KEY = your_gemini_key
   GEMINI_API_KEY_2 = your_second_gemini_key
   GROQ_API_KEY = your_groq_key
   FLASK_SECRET_KEY = your_random_secret_key
   FLASK_ENV = production
   ```

6. **Create Web Service**:
   - Click "Create Web Service"
   - Wait 5-10 minutes for initial deployment

### 4. Monitor Deployment

- Check "Logs" tab for build progress
- First deployment takes longer (installing dependencies)
- Look for "Server is running" message

### 5. Access Your App

Once deployed:
- URL: `https://your-app-name.onrender.com`
- It may take 30 seconds to wake up on free tier

## Important Notes for Render Free Tier

⚠️ **Free tier limitations**:
- Service spins down after 15 minutes of inactivity
- First request after inactivity takes 30-50 seconds
- 750 hours/month free
- Good for testing and demos

✅ **Recommendations**:
- Use Starter plan for production
- Keep MongoDB Atlas on M0 (free) tier
- Monitor usage in Render dashboard

## Troubleshooting

### Build Fails
**Error**: "Command failed with exit code 1"
- Check `build.sh` has correct permissions
- Verify all dependencies in `requirements.txt`
- Check Render build logs for specific error

### Application Won't Start
**Error**: "Application failed to respond"
- Verify `Procfile` is correct: `web: gunicorn app:app`
- Check environment variables are set
- Review application logs in Render

### Database Connection Error
**Error**: "MongoClient connection error"
- Verify `MONGO_URI` is correct in Render environment
- Check MongoDB Atlas allows connections from anywhere (0.0.0.0/0)
- Ensure database user has read/write permissions

### Static Files Not Loading
**Solution**:
- Ensure directories are created in `build.sh`
- Check file paths in code use `os.path.join()`
- Verify static files are in correct directories

### Model Files Not Found
**Error**: "FileNotFoundError: grape_model.h5"
- Ensure model files are committed to git (not in .gitignore)
- Check file names match exactly (case-sensitive)
- Verify files are in root directory

## Updating Your Deployment

When you make changes:

```bash
# Make your changes
git add .
git commit -m "Your change description"
git push origin main
```

Render will automatically:
- Detect the push
- Rebuild your application
- Deploy the new version

## Custom Domain (Optional)

To use your own domain:
1. Go to your service settings in Render
2. Click "Custom Domain"
3. Add your domain
4. Update DNS records as instructed

## Monitoring

- **Logs**: View real-time logs in Render dashboard
- **Metrics**: Check service health and response times
- **Alerts**: Set up email notifications for downtime

## Scaling

To handle more traffic:
1. Upgrade to Starter plan ($7/month)
2. Or upgrade to Standard plan ($25/month) for more resources
3. Monitor metrics to determine if scaling is needed

## Support

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com/
- Your app logs: Check Render dashboard

---

**Need Help?** Check the main README.md for additional information.
