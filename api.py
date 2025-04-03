"""
API Routes for Credit Card Parser Application
"""

from flask import Blueprint, request, jsonify, current_app
import os
import logging
import tempfile
from werkzeug.utils import secure_filename
import cc_parser_updated as cc_parser

# Configure the blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/parse', methods=['POST'])
def parse_data():
    """
    API endpoint to parse credit card data from a file
    
    Expects a multipart/form-data POST with:
    - file: The text file to process
    - country_filter (optional): Filter by country
    - card_type_filter (optional): Filter by card type
    
    Returns JSON with processing results
    """
    # Check if a file was submitted
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Check if a file was selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file extension
    if not file.filename.lower().endswith('.txt'):
        return jsonify({'error': 'Please upload a .txt file'}), 400
    
    # Get filter options
    country_filter = request.form.get('country_filter')
    card_type_filter = request.form.get('card_type_filter')
    
    # Create a temporary file
    fd, temp_path = tempfile.mkstemp(suffix='.txt')
    os.close(fd)
    
    try:
        # Save the uploaded file to temp
        file.save(temp_path)
        
        # Parse the data with filters
        data = cc_parser.parse_credit_card_data(
            temp_path, 
            country_filter=country_filter if country_filter and country_filter != 'all' else None, 
            card_type_filter=card_type_filter if card_type_filter and card_type_filter != 'all' else None
        )
        
        if not data:
            return jsonify({
                'error': 'No valid data found in the file (or no data matched your filters)'
            }), 404
        
        # Format the data for JSON response
        result = {
            'record_count': len(data),
            'filters_applied': {
                'country': country_filter if country_filter else None,
                'card_type': card_type_filter if card_type_filter else None
            },
            'data': data[:10],  # Return only first 10 records as preview
            'truncated': len(data) > 10
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"API Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_path)
        except Exception as e:
            logging.error(f"Failed to delete temporary file: {str(e)}")

@api_bp.route('/export', methods=['POST'])
def export_data():
    """
    API endpoint to export credit card data to Excel
    
    Expects a JSON body with:
    - data: Array of credit card records
    
    Returns a downloadable Excel file
    """
    # Check if we have data
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    data = request.json.get('data')
    if not data or not isinstance(data, list):
        return jsonify({'error': 'Invalid data format'}), 400
    
    # Create a temporary file for the Excel output
    fd, temp_excel_path = tempfile.mkstemp(suffix='.xlsx')
    os.close(fd)
    
    try:
        # Export to Excel
        if cc_parser.export_to_excel(data, temp_excel_path):
            # Read the Excel file and return it
            with open(temp_excel_path, 'rb') as f:
                excel_data = f.read()
            
            # Return the Excel file as an attachment
            response = current_app.response_class(
                excel_data,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response.headers.set('Content-Disposition', 'attachment', filename='credit_cards.xlsx')
            return response
        else:
            return jsonify({'error': 'Error exporting data to Excel'}), 500
    
    except Exception as e:
        logging.error(f"API Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_excel_path)
        except Exception as e:
            logging.error(f"Failed to delete temporary Excel file: {str(e)}")

@api_bp.route('/card-types', methods=['GET'])
def get_card_types():
    """
    API endpoint to get available card types
    
    Returns a JSON list of card types
    """
    card_types = cc_parser.get_card_types()
    return jsonify(card_types), 200

@api_bp.route('/countries', methods=['GET'])
def get_countries():
    """
    API endpoint to get available countries
    
    Expects a query parameter:
    - file_path (optional): Path to a specific file to scan for countries
    
    Returns a JSON list of countries
    """
    file_path = request.args.get('file_path', 'credit_cards.txt')
    
    if not os.path.exists(file_path):
        return jsonify([]), 200
    
    countries = cc_parser.get_available_countries(file_path)
    return jsonify(countries), 200

@api_bp.route('/validate-card', methods=['POST'])
def validate_card():
    """
    API endpoint to validate a credit card number
    
    Expects a JSON body with:
    - card_number: The credit card number to validate
    
    Returns a JSON object with validation results
    """
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    card_number = request.json.get('card_number', '')
    
    if not card_number:
        return jsonify({'error': 'Card number is required'}), 400
    
    is_valid = cc_parser.validate_card_number(card_number)
    card_type = cc_parser.detect_card_type(card_number) if is_valid else 'Unknown'
    
    return jsonify({
        'valid': is_valid,
        'card_type': card_type,
        'card_number': card_number
    }), 200