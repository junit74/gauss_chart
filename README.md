# Magnetic Field Chart Generator

A Streamlit web application for analyzing magnetic field measurement data from aging tests. The app extracts data from table images using Google Gemini API (or manual input) and generates comparison charts for N/S pole measurements.

## Features

- **Image-based Data Extraction**: Upload table images and automatically extract magnetic field data using Google Gemini 2.0 Flash API
- **Manual Data Input**: Enter measurement data manually if preferred
- **Chart Generation**: Creates a 2x2 chart comparing:
  - N Pole: Initial vs After Aging
  - S Pole: Initial vs After Aging
  - Absolute Change comparison
  - Percentage Change comparison
- **Export**: Download generated charts as PNG files

## Installation

1. Clone the repository:
```bash
git clone https://github.com/junit74/gauss_chart.git
cd gauss_chart
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

## Configuration

### Local Development

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_api_key_here
```

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey).

### Streamlit Cloud

When deploying to Streamlit Cloud, add your API key in the app's Secrets settings:
```toml
GEMINI_API_KEY = "your_api_key_here"
```

## Usage

Run the application:
```bash
./run.sh
```

Or manually:
```bash
source venv/bin/activate
export PYTHONIOENCODING=utf-8
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" and select your repository
4. Set `app.py` as the main file
5. In Advanced settings → Secrets, add your `GEMINI_API_KEY`
6. Click Deploy

## Data Structure

Data is organized by `{Manufacturer}_{Size}` (e.g., `SDM_3X1`, `ASEN_5X1`) with values:
- `initial_n/s`: Initial Gauss readings
- `after_n/s`: Post-aging Gauss readings
- `change_n/s`: Absolute change
- `percent_n/s`: Percentage change

## Dependencies

- `streamlit`: Web interface
- `google-genai`: Gemini API client for image-to-text extraction
- `matplotlib`: Chart generation
- `pandas`: Data handling
- `numpy`: Numerical operations
- `Pillow`: Image processing
- `python-dotenv`: Environment variable management

## License

MIT License
