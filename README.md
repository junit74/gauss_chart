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

## Architecture

### Image to Chart Generation Flow

The app uses a **3-step pipeline** to convert a table image into charts:

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Table Image │  →   │   Gemini    │  →   │    JSON     │
│   (input)   │      │  (vision)   │      │   (text)    │
└─────────────┘      └─────────────┘      └─────────────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐      ┌─────────────┐
                                          │ matplotlib  │  →   │ Chart PNG   │
                                          │  (local)    │      │  (output)   │
                                          └─────────────┘      └─────────────┘
```

#### Step 1: Image Upload
- User uploads a table image (PNG/JPG/JPEG) via Streamlit file uploader
- The uploaded image is displayed for preview

#### Step 2: Data Extraction via Gemini API
- **Function**: `extract_data_from_image()`
- Sends the image to Google Gemini 2.0 Flash with a detailed prompt
- Gemini acts as "OCR with understanding" - reads the table and extracts numbers
- Returns structured JSON with measurement values:
  - `initial_n/s`: Initial Gauss readings
  - `after_n/s`: Post-aging readings
  - `change_n/s`: Absolute change
  - `percent_n/s`: Percentage change

#### Step 3: Chart Generation (Local)
- **Function**: `create_charts()`
- Charts are rendered locally using matplotlib (NOT by Gemini)
- Creates a 2x2 figure with fixed layout and styling

### Chart Layout (Fixed Pattern)

The consistent 2x2 chart layout is hardcoded in `create_charts()`:

| Position | Chart Type |
|----------|------------|
| Top-left | N Pole: Initial vs After |
| Top-right | S Pole: Initial vs After |
| Bottom-left | Absolute Change (N vs S) |
| Bottom-right | Percentage Change (N vs S) |

#### Fixed Visual Elements
- **Colors**: Blue (`#4a8bc2`) for N pole, Purple (`#9c4a7c`) for S pole
- **Y-axis limits**: 0-2000 for Gauss charts
- **Reference lines**: 100 Gauss threshold, 10% threshold
- **Figure size**: 14x10 inches

The chart **template is static** (positions, colors, titles, axis settings). Only the **bar heights change** based on extracted/input data. This ensures visual consistency regardless of the source image content.

### Component Responsibilities

| Task | Tool Used |
|------|-----------|
| Extract data from image | Google Gemini API (Vision AI) |
| Generate charts | matplotlib (local Python) |
| Web interface | Streamlit |
| Data display | pandas DataFrame |

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
