# Credit Card Information Parser
@Author Jeremy Bosch
@Date 04/02/2025


This tool parses credit card and personal information from a text file and exports it to a neatly formatted Excel file.

## Features

- Extracts credit card numbers, CVV, expiration dates, names, addresses, and other personal information
- Validates data format to catch obvious errors
- Exports data to a well-formatted Excel file with appropriate column widths
- Handles large files efficiently (tested with 18,000+ lines)
- Provides detailed logging and error reporting

## Requirements

- Python 3.6 or higher
- pandas library
- openpyxl library

## Installation

1. Ensure Python is installed on your system
2. Install the required packages:

```bash
pip install pandas openpyxl

