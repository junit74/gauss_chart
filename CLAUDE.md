# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Streamlit web application for analyzing magnetic field measurement data from aging tests. The app extracts data from table images using Google Gemini API (or manual input) and generates comparison charts for N/S pole measurements.

## Development Commands

```bash
# Activate virtual environment and run the app
./run.sh

# Or manually:
source venv/bin/activate
export PYTHONIOENCODING=utf-8
streamlit run app.py

# Install dependencies
pip install -r requirements.txt
```

## API Key Configuration

The app uses Google Gemini API. API key is loaded in this priority:
1. `st.secrets["GEMINI_API_KEY"]` (Streamlit Cloud)
2. `GEMINI_API_KEY` environment variable (local `.env` file)

For local development, copy `.env.example` to `.env` and add your key.

## Architecture

Single-file application (`app.py`) with three main components:

1. **Data Extraction** (`extract_data_from_image`): Uses Google Gemini 2.0 Flash to parse table images into structured JSON with magnetic field values (initial/after measurements for N/S poles)

2. **Chart Generation** (`create_charts`): Creates a 2x2 matplotlib figure with:
   - N Pole: Initial vs After Aging
   - S Pole: Initial vs After Aging
   - Absolute Change comparison
   - Percentage Change comparison

3. **Data Conversion** (`data_to_dataframe`): Transforms internal dict format to pandas DataFrame for display

## Data Structure

Data is keyed by `{Manufacturer}_{Size}` (e.g., `SDM_3X1`, `ASEN_5X1`) with values:
- `initial_n/s`: Initial Gauss readings
- `after_n/s`: Post-aging Gauss readings
- `change_n/s`: Absolute change
- `percent_n/s`: Percentage change

## Dependencies

- `google-genai`: Gemini API client for image-to-text extraction
- `streamlit`: Web interface
- `matplotlib`: Chart generation
- `pandas/numpy`: Data handling
