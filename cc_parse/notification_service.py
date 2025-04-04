"""
Email Notification Service for Credit Card Parser

This module provides functionality to send email notifications when files are processed.
Uses external email services like Mailgun or SendGrid.
"""

import os
import logging
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class MailgunService:
    """Email notification service using Mailgun API"""

    def __init__(self):
        self.api_key = os.environ.get('MAILGUN_API_KEY')
        self.domain = os.environ.get('MAILGUN_DOMAIN', '')
        self.from_email = os.environ.get('NOTIFICATION_FROM_EMAIL', f'noreply@{self.domain}')
        self.api_base_url = f"https://api.mailgun.net/v3/{self.domain}" if self.domain else None

    def is_configured(self):
        """Check if the service is properly configured"""
        return bool(self.api_key and self.domain)

    def send_notification(self, to_email, subject, body, attachment=None):
        """
        Send an email notification
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            body (str): Email body (HTML supported)
            attachment (str, optional): Path to a file to attach
            
        Returns:
            bool: True if the email was sent successfully, False otherwise
        """
        if not self.is_configured():
            logging.warning("Mailgun is not properly configured. Email not sent.")
            return False
            
        if not to_email:
            logging.error("No recipient email provided")
            return False
        
        try:
            logging.info(f"Sending email to {to_email}")
            data = {
                "from": self.from_email,
                "to": to_email,
                "subject": subject,
                "html": body
            }
            
            files = {}
            if attachment and os.path.exists(attachment):
                with open(attachment, 'rb') as f:
                    files = {'attachment': (os.path.basename(attachment), f)}
            
            # Only send API key if it exists
            auth_tuple = ("api", self.api_key) if self.api_key else None
            
            response = requests.post(
                f"{self.api_base_url}/messages",
                auth=auth_tuple,
                data=data,
                files=files
            )
            
            if response.status_code == 200:
                logging.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logging.error(f"Failed to send email: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending email: {str(e)}")
            return False


class SendGridService:
    """Email notification service using SendGrid API"""

    def __init__(self):
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        self.from_email = os.environ.get('NOTIFICATION_FROM_EMAIL', 'noreply@creditcardparser.com')
        self.api_url = "https://api.sendgrid.com/v3/mail/send"

    def is_configured(self):
        """Check if the service is properly configured"""
        return bool(self.api_key)

    def send_notification(self, to_email, subject, body, attachment=None):
        """
        Send an email notification
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            body (str): Email body (HTML supported)
            attachment (str, optional): Path to a file to attach
            
        Returns:
            bool: True if the email was sent successfully, False otherwise
        """
        if not self.is_configured():
            logging.warning("SendGrid is not properly configured. Email not sent.")
            return False
            
        if not to_email:
            logging.error("No recipient email provided")
            return False
        
        try:
            logging.info(f"Sending email to {to_email}")
            
            # Prepare the email data
            data = {
                "personalizations": [
                    {
                        "to": [{"email": to_email}],
                        "subject": subject
                    }
                ],
                "from": {"email": self.from_email},
                "content": [
                    {
                        "type": "text/html",
                        "value": body
                    }
                ]
            }
            
            # Add attachment if provided
            if attachment and os.path.exists(attachment):
                import base64
                with open(attachment, "rb") as f:
                    attachment_content = f.read()
                    
                attachment_data = {
                    "content": base64.b64encode(attachment_content).decode(),
                    "filename": os.path.basename(attachment),
                    "type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "disposition": "attachment"
                }
                
                data["attachments"] = [attachment_data]
            
            # Send the request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data
            )
            
            if response.status_code in [200, 202]:
                logging.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logging.error(f"Failed to send email: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending email: {str(e)}")
            return False


# Factory function to get the appropriate email service
def get_email_service():
    """
    Factory function to get the configured email service
    Returns the first configured service in order: Mailgun, SendGrid
    """
    mailgun = MailgunService()
    if mailgun.is_configured():
        return mailgun
    
    sendgrid = SendGridService()
    if sendgrid.is_configured():
        return sendgrid
    
    # Return Mailgun as default (will log warning if not configured)
    return mailgun


# Helper function for creating a summary email
def create_summary_email(data, country_filter=None, card_type_filter=None):
    """
    Create a summary email body with the processing results
    
    Args:
        data (list): List of processed credit card records
        country_filter (str, optional): Country filter that was applied
        card_type_filter (str, optional): Card type filter that was applied
        
    Returns:
        str: HTML email body
    """
    # Count card types
    card_types = {}
    countries = {}
    for record in data:
        card_type = record.get('Card Type', 'Unknown')
        card_types[card_type] = card_types.get(card_type, 0) + 1
        
        country = record.get('Country', 'Unknown')
        countries[country] = countries.get(country, 0) + 1
    
    # Create the email body
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2>Credit Card Processing Summary</h2>
        <p>Successfully processed <strong>{len(data)}</strong> credit card records.</p>
        
        <h3>Filters Applied</h3>
        <ul>
            <li>Country: <strong>{country_filter if country_filter else 'None'}</strong></li>
            <li>Card Type: <strong>{card_type_filter if card_type_filter else 'None'}</strong></li>
        </ul>
        
        <h3>Card Type Distribution</h3>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
            <tr style="background-color: #f0f0f0;">
                <th>Card Type</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
    """
    
    for card_type, count in sorted(card_types.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(data)) * 100
        body += f"""
            <tr>
                <td>{card_type}</td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
            </tr>
        """
    
    body += """
        </table>
        
        <h3>Country Distribution</h3>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
            <tr style="background-color: #f0f0f0;">
                <th>Country</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
    """
    
    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(data)) * 100
        body += f"""
            <tr>
                <td>{country}</td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
            </tr>
        """
    
    body += """
        </table>
        
        <p style="margin-top: 20px;">
            <em>This is an automated message. The Excel file with the complete results is attached.</em>
        </p>
    </body>
    </html>
    """
    
    return body


# Example usage
def send_processing_notification(to_email, data, output_file, country_filter=None, card_type_filter=None):
    """
    Send a notification email with the processing results
    
    Args:
        to_email (str): Recipient email address
        data (list): List of processed credit card records
        output_file (str): Path to the generated Excel file
        country_filter (str, optional): Country filter that was applied
        card_type_filter (str, optional): Card type filter that was applied
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    if not to_email:
        return False
    
    # Get the email service
    email_service = get_email_service()
    
    # Create email content
    subject = "Credit Card Processing Results"
    body = create_summary_email(data, country_filter, card_type_filter)
    
    # Send the email with the Excel file attached
    return email_service.send_notification(to_email, subject, body, output_file)