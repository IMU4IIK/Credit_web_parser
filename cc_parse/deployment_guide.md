# Credit Card Parser - Deployment Guide

## Files to Upload
Transfer the following files and directories to your website via FTP:

### Python Files
- `main.py` - Main Flask application
- `api.py` - API endpoints
- `cc_parser_updated.py` - Core parsing engine
- `notification_service.py` - Email notification service

### Templates
- `templates/layout.html` - Base template
- `templates/index.html` - Homepage
- `templates/success.html` - Success page
- `templates/api_docs.html` - API documentation
- `templates/settings.html` - Settings page

### Sample Data
- `credit_cards.txt` - Sample credit card data
- `sample_input.txt` - Alternative sample data

### Directories
- `icons/` - Application icons
- `uploads/` - Directory for uploaded files (create if doesn't exist)
- `output/` - Directory for generated Excel files (create if doesn't exist)

## Required Python Packages
Install these packages on your server:
```
flask>=2.0.0
flask-sqlalchemy>=3.0.0
gunicorn>=20.1.0
pandas>=1.3.0
openpyxl>=3.0.7
requests>=2.25.1
werkzeug>=2.0.0
email-validator>=1.1.3
psycopg2-binary>=2.9.1
```

## Running the Application
To start the application on your server:

```bash
# Option 1: Using Flask directly (development only)
export FLASK_APP=main.py
flask run --host=0.0.0.0 --port=5000

# Option 2: Using Gunicorn (recommended for production)
gunicorn --bind 0.0.0.0:5000 --workers=2 main:app
```

## Setting Up Email Notifications
To enable email notifications, set the following environment variables:

### For Mailgun
```bash
export MAILGUN_API_KEY=your_mailgun_api_key
export MAILGUN_DOMAIN=your_mailgun_domain
```

### For SendGrid
```bash
export SENDGRID_API_KEY=your_sendgrid_api_key
```

## Customization
- Edit `templates/layout.html` to change the overall layout
- Edit `templates/index.html` to modify the homepage
- Configure database connections in `main.py` if needed

## Security Considerations
- This application processes sensitive credit card data
- Ensure your server uses HTTPS with a valid SSL certificate
- Consider adding authentication for production use
- Regularly update all dependencies

## Additional Notes
- Make sure the `uploads` and `output` directories are writable by the web server
- Set appropriate file permissions (typically 755 for directories, 644 for files)
- The application is configured to bind to 0.0.0.0 to be accessible externally