# AI Weather Prediction System - Deployment Guide

This guide covers deployment options for the AI Weather Prediction System on various platforms.

## 🚀 Quick Start (Local Development)

1. **Clone and Setup**
   ```bash
   cd weather_prediction
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

2. **Access the Application**
   - Open http://127.0.0.1:8000 in your browser
   - Start making weather predictions!

## 🌐 Production Deployment Options

### Option 1: Railway (Recommended - Free Tier Available)

Railway offers easy deployment with automatic builds from Git.

1. **Prepare Your Code**
   ```bash
   # Ensure all files are committed
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Railway**
   - Visit [railway.app](https://railway.app)
   - Sign up/login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will automatically detect Django and deploy

3. **Environment Variables**
   Set these in Railway dashboard:
   ```
   SECRET_KEY=your-secret-key-here
   WEATHER_API_KEY=ff8c21d34e1be467ed610359b93f7bca
   DJANGO_SETTINGS_MODULE=weather_prediction.settings_production
   ```

4. **Custom Domain (Optional)**
   - Go to Settings → Domains
   - Add your custom domain

### Option 2: Render (Free Tier Available)

1. **Create render.yaml**
   ```yaml
   services:
     - type: web
       name: weather-prediction
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: gunicorn weather_prediction.wsgi:application
       envVars:
         - key: SECRET_KEY
           generateValue: true
         - key: WEATHER_API_KEY
           value: ff8c21d34e1be467ed610359b93f7bca
   ```

2. **Deploy**
   - Visit [render.com](https://render.com)
   - Connect your GitHub repository
   - Render will automatically deploy

### Option 3: Heroku

1. **Install Heroku CLI**
   ```bash
   # Install Heroku CLI from heroku.com/cli
   heroku login
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-weather-app-name
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key-here
   heroku config:set WEATHER_API_KEY=ff8c21d34e1be467ed610359b93f7bca
   heroku config:set DJANGO_SETTINGS_MODULE=weather_prediction.settings_production
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 4: PythonAnywhere

1. **Upload Code**
   - Upload your project files to PythonAnywhere
   - Or clone from GitHub in a Bash console

2. **Create Virtual Environment**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 weather-prediction
   pip install -r requirements.txt
   ```

3. **Configure Web App**
   - Go to Web tab → Add a new web app
   - Choose Django
   - Set source code path: `/home/yourusername/weather_prediction`
   - Set working directory: `/home/yourusername/weather_prediction`

4. **Configure WSGI**
   Edit the WSGI configuration file:
   ```python
   import os
   import sys
   
   path = '/home/yourusername/weather_prediction'
   if path not in sys.path:
       sys.path.append(path)
   
   os.environ['DJANGO_SETTINGS_MODULE'] = 'weather_prediction.settings_production'
   
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

## 🔧 Environment Variables

Create a `.env` file for local development:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Weather API
WEATHER_API_KEY=ff8c21d34e1be467ed610359b93f7bca
WEATHER_BASE_URL=https://api.openweathermap.org/data/2.5/

# Database (for production)
DATABASE_URL=postgres://user:password@host:port/database

# Email (for error notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ADMIN_EMAIL=admin@yourdomain.com

# Caching (optional)
REDIS_URL=redis://localhost:6379/1

# Error Tracking (optional)
SENTRY_DSN=your-sentry-dsn-here
```

## 📊 Database Setup

### SQLite (Default - Development)
No additional setup required. Database file is created automatically.

### PostgreSQL (Production)
```bash
# Install PostgreSQL
pip install psycopg2-binary

# Set DATABASE_URL environment variable
DATABASE_URL=postgres://user:password@host:port/database
```

### MySQL (Alternative)
```bash
# Install MySQL client
pip install mysqlclient

# Set DATABASE_URL environment variable
DATABASE_URL=mysql://user:password@host:port/database
```

## 🔒 Security Checklist

- [ ] Set `DEBUG = False` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable HTTPS (`SECURE_SSL_REDIRECT = True`)
- [ ] Set secure cookie flags
- [ ] Configure proper CORS settings
- [ ] Set up error monitoring (Sentry)
- [ ] Regular security updates

## 📈 Performance Optimization

### 1. Caching
```python
# Install Redis
pip install redis django-redis

# Configure in settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 2. Static Files
```python
# Use WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 3. Database Optimization
```python
# Use connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 60

# Enable query optimization
DATABASES['default']['OPTIONS'] = {
    'MAX_CONNS': 20,
    'MIN_CONNS': 5,
}
```

## 🔍 Monitoring and Logging

### 1. Application Monitoring
```python
# Install Sentry
pip install sentry-sdk

# Configure in settings_production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[DjangoIntegration()],
)
```

### 2. Server Monitoring
- Use services like New Relic, DataDog, or Pingdom
- Monitor response times, error rates, and uptime
- Set up alerts for critical issues

## 🚨 Troubleshooting

### Common Issues

1. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic --noinput
   ```

2. **Database Connection Errors**
   - Check DATABASE_URL format
   - Verify database credentials
   - Ensure database server is running

3. **API Key Issues**
   - Verify WEATHER_API_KEY is set correctly
   - Check API key validity on OpenWeatherMap
   - Monitor API usage limits

4. **Memory Issues**
   - Optimize ML model loading
   - Use caching for model instances
   - Consider using smaller model files

### Debug Mode
```python
# Enable debug mode temporarily
DEBUG = True
ALLOWED_HOSTS = ['*']

# Check logs
tail -f logs/django.log
```

## 📱 Mobile Optimization

The application is fully responsive and works on mobile devices. For better mobile experience:

1. **PWA Support** (Optional)
   - Add service worker
   - Create manifest.json
   - Enable offline functionality

2. **Performance**
   - Optimize images
   - Minimize JavaScript
   - Use CDN for static files

## 🔄 Continuous Deployment

### GitHub Actions (Example)
```yaml
name: Deploy to Railway

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to Railway
      uses: railway-app/railway-action@v1
      with:
        railway-token: ${{ secrets.RAILWAY_TOKEN }}
```

## 📞 Support

For deployment issues:
1. Check the logs first
2. Verify environment variables
3. Test locally with production settings
4. Contact platform support if needed

## 🎯 Next Steps

After successful deployment:
1. Set up monitoring and alerts
2. Configure backup strategy
3. Plan for scaling
4. Implement CI/CD pipeline
5. Add more ML models
6. Enhance UI/UX features

---

**Congratulations!** Your AI Weather Prediction System is now live and ready to serve users worldwide! 🌟