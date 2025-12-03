#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "Warning: GEMINI_API_KEY is not set in .env file"
    echo "The app will run but image extraction will not work without an API key."
    echo ""
fi

# Activate virtual environment and run Streamlit with UTF-8 encoding
source venv/bin/activate
export PYTHONIOENCODING=utf-8
streamlit run app.py
