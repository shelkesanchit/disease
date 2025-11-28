#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads
mkdir -p static/uploads
mkdir -p static/pdfs
mkdir -p instance