#!/usr/bin/env python3
"""
Credit Card Information Parser

This script parses credit card and personal information from a text file
and exports it to a neatly formatted Excel file.

Usage:
    python cc_parser.py input_file.txt output_file.xlsx
"""

import sys
import os
import logging
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def validate_card_number(card_num):
    """
    Basic validation for credit card number format.
    """
    if not card_num:
        return False

    # Remove spaces and dashes
    card_num = card_num.replace(' ', '').replace('-', '')

    # Check if it's numeric and within typical length range (13-19 digits)
    if not card_num.isdigit() or not (13 <= len(card_num) <= 19):
        return False

    return True


def validate_cvv(cvv):
    """
    Basic validation for CVV format.
    """
    if not cvv:
        return False

    # Check if it's numeric and 3-4 digits
    if not cvv.isdigit() or not (3 <= len(cvv) <= 4):
        return False

    return True


def validate_exp_date(month, year):
    """
    Basic validation for expiration date.
    """
    try:
        month = int(month)
        year = int(year)

        if not (1 <= month <= 12):
            return False

        # Check if the year is reasonable (not too far in the past or future)
        current_year = datetime.now().year
        short_current_year = current_year % 100

        # Handle two-digit years
        if year < 100:
            # If the year is in the past by more than 5 years
            if year < (short_current_year - 5):
                return False
            # If the year is more than 20 years in the future
            if year > (short_current_year + 20):
                return False
        else:
            # For four-digit years
            if year < (current_year - 5) or year > (current_year + 20):
                return False

        return True
    except ValueError:
        return False


def parse_credit_card_data(input_file):
    """
    Parse credit card information from a text file.
    
    Args:
        input_file (str): Path to the input text file.
        
    Returns:
        list: List of dictionaries containing parsed data.
    """
    data = []
    error_lines = []
    line_num = 0

    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue

                # Split the line by pipe character
                parts = [part.strip() for part in line.split('|')]

                # Check if we have enough fields
                if len(parts) < 11:
                    error_lines.append(f"Line {line_num}: Not enough fields")
                    continue

                # Extract the fields
                card_number = parts[0]
                exp_month = parts[1]
                exp_year = parts[2]
                cvv = parts[3]
                name = parts[4]
                address = parts[5]
                town = parts[6]
                state = parts[7]
                zip_code = parts[8]
                phone = parts[9]
                email = parts[10]

                # Basic validation
                if not validate_card_number(card_number):
                    error_lines.append(f"Line {line_num}: Invalid card number")
                    continue

                if not validate_cvv(cvv):
                    error_lines.append(f"Line {line_num}: Invalid CVV")
                    continue

                if not validate_exp_date(exp_month, exp_year):
                    error_lines.append(
                        f"Line {line_num}: Invalid expiration date")
                    continue

                # Create a record
                record = {
                    'Credit Card Number': card_number,
                    'CVV': cvv,
                    'Expiration Month': exp_month,
                    'Expiration Year': exp_year,
                    'Name': name,
                    'Address': address,
                    'Town': town,
                    'State': state,
                    'ZIP Code': zip_code,
                    'Phone': phone,
                    'Email': email
                }

                data.append(record)

                # Log progress every 1000 lines
                if line_num % 1000 == 0:
                    logging.info(f"Processed {line_num} lines...")

    except FileNotFoundError:
        logging.error(f"Input file not found: {input_file}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading input file: {str(e)}")
        sys.exit(1)

    # Log error summary
    if error_lines:
        logging.warning(f"Found {len(error_lines)} errors while parsing.")
        for idx, error in enumerate(error_lines[:10], 1):
            logging.warning(f"Error {idx}: {error}")

        if len(error_lines) > 10:
            logging.warning(f"... and {len(error_lines) - 10} more errors.")

    logging.info(
        f"Successfully parsed {len(data)} records from {line_num} lines.")
    return data


def export_to_excel(data, output_file):
    """
    Export the parsed data to an Excel file.
    
    Args:
        data (list): List of dictionaries containing the parsed data.
        output_file (str): Path to the output Excel file.
    """
    if not data:
        logging.error("No data to export.")
        return False

    try:
        # Convert the data to a pandas DataFrame
        df = pd.DataFrame(data)

        # Create a writer object
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Write the DataFrame to Excel
            df.to_excel(writer, sheet_name='Credit Card Data', index=False)

            # Access the worksheet and format it
            workbook = writer.book
            worksheet = writer.sheets['Credit Card Data']

            # Set column widths
            column_widths = {
                'A': 20,  # Credit Card Number
                'B': 10,  # CVV
                'C': 10,  # Expiration Month
                'D': 10,  # Expiration Year
                'E': 30,  # Name
                'F': 40,  # Address
                'G': 20,  # Town
                'H': 10,  # State
                'I': 10,  # ZIP Code
                'J': 15,  # Phone
                'K': 30,  # Email
            }

            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width

        logging.info(f"Successfully exported data to {output_file}")
        return True

    except Exception as e:
        logging.error(f"Error exporting data to Excel: {str(e)}")
        return False


def main():
    """
    Main function to parse credit card information and export to Excel.
    """
    # Check command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python cc_parser.py input_file.txt output_file.xlsx")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Validate file extensions
    if not input_file.lower().endswith('.txt'):
        logging.error("Input file must be a .txt file.")
        sys.exit(1)

    if not output_file.lower().endswith('.xlsx'):
        logging.error("Output file must be a .xlsx file.")
        sys.exit(1)

    # Check if the input file exists
    if not os.path.isfile(input_file):
        logging.error(f"Input file not found: {input_file}")
        sys.exit(1)

    # Parse the data
    logging.info(f"Parsing credit card data from {input_file}...")
    data = parse_credit_card_data(input_file)

    # Export to Excel
    if data:
        logging.info(f"Exporting data to {output_file}...")
        if export_to_excel(data, output_file):
            logging.info("Export completed successfully.")
        else:
            logging.error("Export failed.")
            sys.exit(1)
    else:
        logging.error("No data parsed from the input file.")
        sys.exit(1)


if __name__ == "__main__":
    main()
