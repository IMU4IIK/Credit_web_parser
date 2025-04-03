#!/usr/bin/env python3
"""
Script to prepare the Credit Card Parser application for FTP upload
by creating a zip file with all necessary files.
"""

import os
import zipfile
import shutil
from datetime import datetime

def create_directory(dir_path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")

def main():
    # Define the output zip filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    zip_filename = f"credit_card_parser_{timestamp}.zip"
    
    # Define files to include
    python_files = [
        "main.py", 
        "api.py", 
        "cc_parser_updated.py", 
        "notification_service.py"
    ]
    
    # Get all template files
    template_files = []
    if os.path.exists("templates"):
        template_files = [os.path.join("templates", f) for f in os.listdir("templates") 
                         if f.endswith(".html")]
    
    # Include sample data files
    data_files = [
        "credit_cards.txt",
        "sample_input.txt",
        "deployment_guide.md"
    ]
    
    # Create temporary directories for the zip
    temp_dir = "temp_for_zip"
    create_directory(temp_dir)
    create_directory(os.path.join(temp_dir, "templates"))
    create_directory(os.path.join(temp_dir, "uploads"))
    create_directory(os.path.join(temp_dir, "output"))
    
    # Copy icon files if they exist
    if os.path.exists("icons"):
        shutil.copytree("icons", os.path.join(temp_dir, "icons"))
        print("Copied icons directory")
    
    # Copy Python files
    for file in python_files:
        if os.path.exists(file):
            shutil.copy2(file, temp_dir)
            print(f"Copied: {file}")
    
    # Copy template files
    for file in template_files:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(temp_dir, "templates"))
            print(f"Copied: {file}")
    
    # Copy data files
    for file in data_files:
        if os.path.exists(file):
            shutil.copy2(file, temp_dir)
            print(f"Copied: {file}")
    
    # Create the zip file
    print(f"Creating zip file: {zip_filename}")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    print(f"Removed temporary directory: {temp_dir}")
    
    print(f"\nZip file created successfully: {zip_filename}")
    print(f"Size: {os.path.getsize(zip_filename) / (1024*1024):.2f} MB")
    print("\nThis zip file contains all necessary files for FTP upload.")
    print("Refer to deployment_guide.md for installation instructions.")

if __name__ == "__main__":
    main()