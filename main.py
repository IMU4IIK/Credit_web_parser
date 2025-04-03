from flask import Flask, render_template, request, send_file, flash, redirect, url_for, session
import os
import logging
import tempfile
from werkzeug.utils import secure_filename
import cc_parser_updated as cc_parser
from api import api_bp
import notification_service as notifications

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Register API blueprint
app.register_blueprint(api_bp)

# Create upload folder if it doesn't exist
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create backgrounds folder if it doesn't exist
BACKGROUNDS_FOLDER = os.path.join(UPLOAD_FOLDER, 'backgrounds')
if not os.path.exists(BACKGROUNDS_FOLDER):
    os.makedirs(BACKGROUNDS_FOLDER)
app.config['BACKGROUNDS_FOLDER'] = BACKGROUNDS_FOLDER

# Create output folder if it doesn't exist
OUTPUT_FOLDER = 'output'
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Allowed image extensions for background uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the home page with the file upload form."""
    # Get available card types for dropdown
    card_types = cc_parser.get_card_types()
    
    # Get available countries for dropdown from sample file
    sample_file = 'credit_cards.txt'
    countries = []
    if os.path.exists(sample_file):
        countries = cc_parser.get_available_countries(sample_file)
    
    return render_template('index.html', card_types=card_types, countries=countries)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing."""
    # Check if a file was submitted
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    # Check if a file was selected
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    # Check file extension
    if not file.filename.lower().endswith('.txt'):
        flash('Please upload a .txt file', 'error')
        return redirect(url_for('index'))
    
    # Get filter options
    country_filter = request.form.get('country_filter')
    card_type_filter = request.form.get('card_type_filter')
    notification_email = request.form.get('notification_email')
    
    # Save the uploaded file
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    
    # Generate output filename with filter info
    filter_info = ''
    if country_filter:
        filter_info += f"_{country_filter}"
    if card_type_filter:
        filter_info += f"_{card_type_filter}"
    
    output_filename = os.path.splitext(filename)[0] + filter_info + '.xlsx'
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    # Parse and process the file
    try:
        logging.info(f"Processing file: {input_path}")
        logging.info(f"Filters - Country: {country_filter}, Card Type: {card_type_filter}")
        
        # Parse the data with filters
        data = cc_parser.parse_credit_card_data(
            input_path, 
            country_filter=country_filter if country_filter and country_filter != 'all' else None, 
            card_type_filter=card_type_filter if card_type_filter and card_type_filter != 'all' else None
        )
        
        # Export to Excel
        if data:
            if cc_parser.export_to_excel(data, output_path):
                # Check if user requested email notification
                if notification_email:
                    # Send email with results
                    logging.info(f"Sending notification email to {notification_email}")
                    email_sent = notifications.send_processing_notification(
                        notification_email, 
                        data, 
                        output_path,
                        country_filter,
                        card_type_filter
                    )
                    if email_sent:
                        flash(f'Email notification sent to {notification_email}', 'success')
                    else:
                        flash('Failed to send email notification. Email service not configured properly.', 'warning')
                
                flash(f'Successfully processed {len(data)} records', 'success')
                return render_template('success.html', 
                                       record_count=len(data), 
                                       output_file=output_filename,
                                       country_filter=country_filter,
                                       card_type_filter=card_type_filter,
                                       notification_email=notification_email)
            else:
                flash('Error exporting data to Excel', 'error')
        else:
            flash('No valid data found in the file (or no data matched your filters)', 'error')
    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        flash(f'Error processing file: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    """Download the processed Excel file."""
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(output_path):
        return send_file(output_path, as_attachment=True)
    else:
        flash('File not found', 'error')
        return redirect(url_for('index'))

@app.route('/api-docs')
def api_docs():
    """Display the API documentation page."""
    return render_template('api_docs.html')

@app.route('/process-demo', methods=['POST'])
def process_demo():
    """Process the demo file (credit_cards.txt)."""
    input_path = 'credit_cards.txt'
    
    # Get filter options
    country_filter = request.form.get('country_filter')
    card_type_filter = request.form.get('card_type_filter')
    notification_email = request.form.get('notification_email')
    
    # Generate output filename with filter info
    filter_info = ''
    if country_filter:
        filter_info += f"_{country_filter}"
    if card_type_filter:
        filter_info += f"_{card_type_filter}"
    
    output_filename = 'credit_cards' + filter_info + '.xlsx'
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    # Check if the demo file exists
    if not os.path.exists(input_path):
        flash('Demo file not found', 'error')
        return redirect(url_for('index'))
    
    # Parse and process the file
    try:
        logging.info(f"Processing demo file: {input_path}")
        logging.info(f"Filters - Country: {country_filter}, Card Type: {card_type_filter}")
        
        # Parse the data with filters
        data = cc_parser.parse_credit_card_data(
            input_path, 
            country_filter=country_filter if country_filter and country_filter != 'all' else None, 
            card_type_filter=card_type_filter if card_type_filter and card_type_filter != 'all' else None
        )
        
        # Export to Excel
        if data:
            if cc_parser.export_to_excel(data, output_path):
                # Check if user requested email notification
                if notification_email:
                    # Send email with results
                    logging.info(f"Sending notification email to {notification_email}")
                    email_sent = notifications.send_processing_notification(
                        notification_email, 
                        data, 
                        output_path,
                        country_filter,
                        card_type_filter
                    )
                    if email_sent:
                        flash(f'Email notification sent to {notification_email}', 'success')
                    else:
                        flash('Failed to send email notification. Email service not configured properly.', 'warning')
                
                flash(f'Successfully processed {len(data)} records', 'success')
                return render_template('success.html', 
                                       record_count=len(data), 
                                       output_file=output_filename,
                                       country_filter=country_filter,
                                       card_type_filter=card_type_filter,
                                       notification_email=notification_email)
            else:
                flash('Error exporting data to Excel', 'error')
        else:
            flash('No valid data found in the file (or no data matched your filters)', 'error')
    except Exception as e:
        logging.error(f"Error processing demo file: {str(e)}")
        flash(f'Error processing file: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET'])
def settings():
    """Display the user settings page."""
    # List all available background images
    backgrounds = []
    for filename in os.listdir(app.config['BACKGROUNDS_FOLDER']):
        if os.path.isfile(os.path.join(app.config['BACKGROUNDS_FOLDER'], filename)) and allowed_file(filename):
            backgrounds.append(filename)
    
    # Get current background from session (if any)
    current_background = session.get('background_image', None)
    
    return render_template('settings.html', 
                          backgrounds=backgrounds,
                          current_background=current_background)

@app.route('/upload-background', methods=['POST'])
def upload_background():
    """Handle background image upload."""
    # Check if a file was submitted
    if 'background_image' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('settings'))
    
    file = request.files['background_image']
    
    # Check if a file was selected
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('settings'))
    
    # Check if the file is allowed
    if file and allowed_file(file.filename):
        # Save the uploaded file with a secure filename
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['BACKGROUNDS_FOLDER'], filename)
        file.save(file_path)
        
        # Set the background in session
        session['background_image'] = filename
        
        flash('Background image uploaded successfully', 'success')
    else:
        flash('Invalid file type. Please upload a PNG, JPG, JPEG, or GIF file.', 'error')
    
    return redirect(url_for('settings'))

@app.route('/set-background/<filename>')
def set_background(filename):
    """Set the selected background image."""
    # Check if the file exists
    file_path = os.path.join(app.config['BACKGROUNDS_FOLDER'], filename)
    if os.path.exists(file_path) and allowed_file(filename):
        # Set the background in session
        session['background_image'] = filename
        flash('Background set successfully', 'success')
    else:
        flash('Background image not found', 'error')
    
    return redirect(url_for('settings'))

@app.route('/clear-background')
def clear_background():
    """Clear the background image setting."""
    if 'background_image' in session:
        session.pop('background_image')
    
    flash('Background cleared successfully', 'success')
    return redirect(url_for('settings'))

@app.route('/backgrounds/<filename>')
def get_background(filename):
    """Serve the background image file."""
    return send_file(os.path.join(app.config['BACKGROUNDS_FOLDER'], filename))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)