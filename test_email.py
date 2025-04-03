"""
Test script for email notification service

Usage:
    python test_email.py test@example.com

This script will test the email notification service by attempting to send
a test email to the specified address.
"""

import sys
import os
import logging
import notification_service as notifications
import cc_parser_updated as cc_parser

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_test_data():
    """Create some sample data for testing"""
    return [
        {
            'Credit Card Number': '4111111111111111',
            'Card Type': 'Visa',
            'CVV': '123',
            'Expiration Month': '12',
            'Expiration Year': '25',
            'Name': 'John Doe',
            'Address': '123 Main St',
            'Town': 'Anytown',
            'State': 'CA',
            'ZIP Code': '12345',
            'Phone': '555-123-4567',
            'Email': 'john@example.com',
            'Country': 'USA'
        },
        {
            'Credit Card Number': '5555555555554444',
            'Card Type': 'Mastercard',
            'CVV': '321',
            'Expiration Month': '10',
            'Expiration Year': '24',
            'Name': 'Jane Smith',
            'Address': '456 Oak St',
            'Town': 'Somewhere',
            'State': 'NY',
            'ZIP Code': '67890',
            'Phone': '555-987-6543',
            'Email': 'jane@example.com',
            'Country': 'USA'
        },
        {
            'Credit Card Number': '378282246310005',
            'Card Type': 'American Express',
            'CVV': '1234',
            'Expiration Month': '06',
            'Expiration Year': '26',
            'Name': 'Bob Johnson',
            'Address': '789 Pine St',
            'Town': 'Otherplace',
            'State': 'TX',
            'ZIP Code': '45678',
            'Phone': '555-567-8901',
            'Email': 'bob@example.com',
            'Country': 'USA'
        }
    ]

def display_service_config():
    """Display the current service configuration"""
    print("\nEmail Service Configuration:")
    print("----------------------------")
    
    # Check Mailgun config
    mailgun_api_key = os.environ.get('MAILGUN_API_KEY')
    mailgun_domain = os.environ.get('MAILGUN_DOMAIN')
    print(f"Mailgun API Key: {'Configured' if mailgun_api_key else 'Not Configured'}")
    print(f"Mailgun Domain: {'Configured' if mailgun_domain else 'Not Configured'}")
    
    # Check SendGrid config
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
    print(f"SendGrid API Key: {'Configured' if sendgrid_api_key else 'Not Configured'}")
    
    # Check notification email
    from_email = os.environ.get('NOTIFICATION_FROM_EMAIL')
    print(f"From Email: {from_email if from_email else 'Not Configured (will use default)'}")
    
    # Get the active service
    service = notifications.get_email_service()
    print(f"\nActive service: {service.__class__.__name__}")
    print(f"Service configured: {'Yes' if service.is_configured() else 'No'}")

def test_email_service(to_email):
    """Test the email notification service by sending a test email"""
    print(f"\nSending test email to {to_email}...")
    
    # Create test data
    data = create_test_data()
    
    # Create a test Excel file
    output_file = 'test_email_output.xlsx'
    if cc_parser.export_to_excel(data, output_file):
        print(f"Created test Excel file: {output_file}")
        
        # Send the email
        result = notifications.send_processing_notification(
            to_email,
            data,
            output_file,
            country_filter='USA',
            card_type_filter=None
        )
        
        if result:
            print("✅ Email sent successfully!")
        else:
            print("❌ Failed to send email.")
            print("   Check your email service configuration and try again.")
    else:
        print("❌ Failed to create test Excel file.")
    
    # Clean up
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed test file: {output_file}")

def main():
    """Main function"""
    # Display header
    print("\n" + "="*50)
    print("Email Notification Service Test")
    print("="*50)
    
    # Display current configuration
    display_service_config()
    
    # Check if an email address was provided
    if len(sys.argv) < 2:
        print("\nUsage: python test_email.py <email_address>")
        print("Example: python test_email.py test@example.com")
        sys.exit(1)
    
    # Get the email address
    to_email = sys.argv[1]
    
    # Test the email service
    test_email_service(to_email)
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()