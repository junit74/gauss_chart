import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import base64
import json
import io
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

from google import genai
from google.genai import types
from PIL import Image

# Get API key from Streamlit secrets or environment variable
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    api_key = os.getenv('GEMINI_API_KEY', '')

# Page configuration
st.set_page_config(
    page_title="Magnetic Field Chart Generator",
    layout="wide"
)

st.title("60°C 1hr Aging Test - Magnetic Field Change Analysis")
st.markdown("### Upload a table image to automatically generate charts")

# Sample data
SAMPLE_DATA = {
    "SDM_3X1": {
        "initial_n": 1667, "initial_s": 1631,
        "after_n": 1574, "after_s": 1544,
        "change_n": 93, "change_s": 87,
        "percent_n": 6, "percent_s": 5
    },
    "SDM_5X1": {
        "initial_n": 1584, "initial_s": 1469,
        "after_n": 1378, "after_s": 1382,
        "change_n": 206, "change_s": 87,
        "percent_n": 13, "percent_s": 6
    },
    "ASEN_3X1": {
        "initial_n": 1667, "initial_s": 1631,
        "after_n": 1518, "after_s": 1567,
        "change_n": 149, "change_s": 64,
        "percent_n": 9, "percent_s": 4
    },
    "ASEN_5X1": {
        "initial_n": 1553, "initial_s": 1570,
        "after_n": 1387, "after_s": 1205,
        "change_n": 166, "change_s": 365,
        "percent_n": 11, "percent_s": 23
    }
}


def extract_data_from_image(api_key, image_bytes, mime_type="image/png"):
    """Extract data from image using Google Gemini API"""
    client = genai.Client(api_key=api_key)

    prompt = """This image is a magnetic field measurement table. Please extract the data in the following JSON format.

For each manufacturer (SDM, ASEN) and size (3X1, 5X1) combination:
- initial_n: N pole value at Initial state (Gauss)
- initial_s: S pole value at Initial state (Gauss)
- after_n: N pole value after 60°C 1hr aging (Gauss)
- after_s: S pole value after 60°C 1hr aging (Gauss)
- change_n: N pole change amount (absolute value)
- change_s: S pole change amount (absolute value)
- percent_n: N pole change rate (%)
- percent_s: S pole change rate (%)

Your response MUST contain ONLY the JSON format below (no other text):
{
    "SDM_3X1": {"initial_n": value, "initial_s": value, "after_n": value, "after_s": value, "change_n": value, "change_s": value, "percent_n": value, "percent_s": value},
    "SDM_5X1": {"initial_n": value, "initial_s": value, "after_n": value, "after_s": value, "change_n": value, "change_s": value, "percent_n": value, "percent_s": value},
    "ASEN_3X1": {"initial_n": value, "initial_s": value, "after_n": value, "after_s": value, "change_n": value, "change_s": value, "percent_n": value, "percent_s": value},
    "ASEN_5X1": {"initial_n": value, "initial_s": value, "after_n": value, "after_s": value, "change_n": value, "change_s": value, "percent_n": value, "percent_s": value}
}"""

    # Create image part with correct mime type
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, image_part]
    )
    response_text = response.text.strip()

    # Parse JSON - handle various response formats
    if "```json" in response_text:
        start = response_text.find("```json") + 7
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()
    elif "```" in response_text:
        start = response_text.find("```") + 3
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()

    return json.loads(response_text)


def create_charts(data):
    """Create 4 charts based on data"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("60°C 1hr Aging Test - Magnetic Field Change Analysis\n(Unit: Gauss)",
                 fontsize=14, fontweight='bold')

    labels = list(data.keys())
    x_labels = [label.replace("_", "\n") for label in labels]
    x = np.arange(len(labels))
    width = 0.35

    # Calculate max Gauss value from data for Y-axis limit
    all_gauss_values = []
    for k in labels:
        all_gauss_values.extend([
            data[k]["initial_n"], data[k]["initial_s"],
            data[k]["after_n"], data[k]["after_s"]
        ])
    max_gauss = max(all_gauss_values) * 1.1  # Add 10% padding

    # Color settings
    initial_color = '#4a8bc2'
    after_color = '#2d5f8a'
    n_color = '#4a8bc2'
    s_color = '#9c4a7c'

    # 1. N Pole: Initial vs After Aging
    ax1 = axes[0, 0]
    initial_n = [data[k]["initial_n"] for k in labels]
    after_n = [data[k]["after_n"] for k in labels]

    bars1 = ax1.bar(x - width/2, initial_n, width, label='Initial', color=initial_color)
    bars2 = ax1.bar(x + width/2, after_n, width, label='After 60°C 1hr', color=after_color, hatch='//')

    ax1.set_ylabel('Gauss')
    ax1.set_title('N Pole: Initial vs After Aging')
    ax1.set_xticks(x)
    ax1.set_xticklabels(x_labels)
    ax1.legend()
    ax1.set_ylim(0, max_gauss)

    # Display values
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

    # 2. S Pole: Initial vs After Aging
    ax2 = axes[0, 1]
    initial_s = [data[k]["initial_s"] for k in labels]
    after_s = [data[k]["after_s"] for k in labels]

    bars3 = ax2.bar(x - width/2, initial_s, width, label='Initial', color=s_color, alpha=0.7)
    bars4 = ax2.bar(x + width/2, after_s, width, label='After 60°C 1hr', color=s_color)

    ax2.set_ylabel('Gauss')
    ax2.set_title('S Pole: Initial vs After Aging')
    ax2.set_xticks(x)
    ax2.set_xticklabels(x_labels)
    ax2.legend()
    ax2.set_ylim(0, max_gauss)

    # Display values
    for bar in bars3:
        height = bar.get_height()
        ax2.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    for bar in bars4:
        height = bar.get_height()
        ax2.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

    # 3. Absolute Change After Aging
    ax3 = axes[1, 0]
    change_n = [data[k]["change_n"] for k in labels]
    change_s = [data[k]["change_s"] for k in labels]

    bars5 = ax3.bar(x - width/2, change_n, width, label='N Pole', color=n_color)
    bars6 = ax3.bar(x + width/2, change_s, width, label='S Pole', color=s_color)

    ax3.axhline(y=100, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax3.set_ylabel('Gauss')
    ax3.set_title('Absolute Change After Aging')
    ax3.set_xticks(x)
    ax3.set_xticklabels(x_labels)
    ax3.legend()

    # Display values
    for bar in bars5:
        height = bar.get_height()
        ax3.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')
    for bar in bars6:
        height = bar.get_height()
        ax3.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')

    # 4. Percentage Change After Aging
    ax4 = axes[1, 1]
    percent_n = [data[k]["percent_n"] for k in labels]
    percent_s = [data[k]["percent_s"] for k in labels]

    bars7 = ax4.bar(x - width/2, percent_n, width, label='N Pole', color=n_color)
    bars8 = ax4.bar(x + width/2, percent_s, width, label='S Pole', color=s_color)

    ax4.axhline(y=10, color='red', linestyle='--', linewidth=1, alpha=0.7)
    ax4.set_ylabel('%')
    ax4.set_title('Percentage Change After Aging')
    ax4.set_xticks(x)
    ax4.set_xticklabels(x_labels)
    ax4.legend()

    # Display values
    for bar in bars7:
        height = bar.get_height()
        ax4.annotate(f'{int(height)}%', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')
    for bar in bars8:
        height = bar.get_height()
        ax4.annotate(f'{int(height)}%', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    return fig


def data_to_dataframe(data):
    """Convert data to DataFrame"""
    rows = []
    for key, values in data.items():
        manufacturer, size = key.split("_")
        rows.append({
            "Manufacturer": manufacturer,
            "Size": size,
            "Initial N": values["initial_n"],
            "Initial S": values["initial_s"],
            "After 60°C 1hr N": values["after_n"],
            "After 60°C 1hr S": values["after_s"],
            "Change N": values["change_n"],
            "Change S": values["change_s"],
            "Change Rate N (%)": values["percent_n"],
            "Change Rate S (%)": values["percent_s"]
        })
    return pd.DataFrame(rows)


# Main area
tab1, tab2 = st.tabs(["Image Upload", "Manual Input"])

with tab1:
    uploaded_file = st.file_uploader(
        "Upload a table image",
        type=["png", "jpg", "jpeg"],
        help="Upload a magnetic field measurement table image to automatically extract data"
    )

    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

        with col2:
            if not api_key:
                st.warning("Please set GEMINI_API_KEY in .env file or use the 'Manual Input' tab")
                st.info("Showing preview with sample data")
                data = SAMPLE_DATA
            else:
                with st.spinner("Extracting data from image..."):
                    try:
                        image_bytes = uploaded_file.getvalue()
                        mime_type = uploaded_file.type or "image/png"
                        data = extract_data_from_image(api_key, image_bytes, mime_type)
                        st.success("Data extraction complete!")
                    except Exception as e:
                        error_msg = str(e).encode('ascii', 'replace').decode('ascii')
                        st.error(f"Data extraction failed: {error_msg}")
                        st.info("Using sample data instead")
                        data = SAMPLE_DATA

            # Display data table
            st.markdown("### Extracted Data")
            df = data_to_dataframe(data)
            st.dataframe(df, use_container_width=True)

        # Generate charts
        st.markdown("---")
        st.markdown("### Generated Charts")

        fig = create_charts(data)
        st.pyplot(fig)

        # Download button
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)

        st.download_button(
            label="Download Chart (PNG)",
            data=buf,
            file_name="magnetic_field_chart.png",
            mime="image/png"
        )

with tab2:
    st.markdown("### Enter Data Manually")

    # Initialize session state
    if 'manual_data' not in st.session_state:
        st.session_state.manual_data = SAMPLE_DATA.copy()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### SDM")

        st.markdown("**3X1**")
        c1, c2, c3, c4 = st.columns(4)
        st.session_state.manual_data["SDM_3X1"]["initial_n"] = c1.number_input("Initial N", value=1667, key="sdm_3x1_in")
        st.session_state.manual_data["SDM_3X1"]["initial_s"] = c2.number_input("Initial S", value=1631, key="sdm_3x1_is")
        st.session_state.manual_data["SDM_3X1"]["after_n"] = c3.number_input("After N", value=1574, key="sdm_3x1_an")
        st.session_state.manual_data["SDM_3X1"]["after_s"] = c4.number_input("After S", value=1544, key="sdm_3x1_as")

        st.markdown("**5X1**")
        c1, c2, c3, c4 = st.columns(4)
        st.session_state.manual_data["SDM_5X1"]["initial_n"] = c1.number_input("Initial N", value=1584, key="sdm_5x1_in")
        st.session_state.manual_data["SDM_5X1"]["initial_s"] = c2.number_input("Initial S", value=1469, key="sdm_5x1_is")
        st.session_state.manual_data["SDM_5X1"]["after_n"] = c3.number_input("After N", value=1378, key="sdm_5x1_an")
        st.session_state.manual_data["SDM_5X1"]["after_s"] = c4.number_input("After S", value=1382, key="sdm_5x1_as")

    with col2:
        st.markdown("#### ASEN")

        st.markdown("**3X1**")
        c1, c2, c3, c4 = st.columns(4)
        st.session_state.manual_data["ASEN_3X1"]["initial_n"] = c1.number_input("Initial N", value=1667, key="asen_3x1_in")
        st.session_state.manual_data["ASEN_3X1"]["initial_s"] = c2.number_input("Initial S", value=1631, key="asen_3x1_is")
        st.session_state.manual_data["ASEN_3X1"]["after_n"] = c3.number_input("After N", value=1518, key="asen_3x1_an")
        st.session_state.manual_data["ASEN_3X1"]["after_s"] = c4.number_input("After S", value=1567, key="asen_3x1_as")

        st.markdown("**5X1**")
        c1, c2, c3, c4 = st.columns(4)
        st.session_state.manual_data["ASEN_5X1"]["initial_n"] = c1.number_input("Initial N", value=1553, key="asen_5x1_in")
        st.session_state.manual_data["ASEN_5X1"]["initial_s"] = c2.number_input("Initial S", value=1570, key="asen_5x1_is")
        st.session_state.manual_data["ASEN_5X1"]["after_n"] = c3.number_input("After N", value=1387, key="asen_5x1_an")
        st.session_state.manual_data["ASEN_5X1"]["after_s"] = c4.number_input("After S", value=1205, key="asen_5x1_as")

    # Calculate changes
    if st.button("Calculate Changes & Generate Charts", type="primary"):
        for key in st.session_state.manual_data:
            d = st.session_state.manual_data[key]
            d["change_n"] = abs(d["initial_n"] - d["after_n"])
            d["change_s"] = abs(d["initial_s"] - d["after_s"])
            d["percent_n"] = round(d["change_n"] / d["initial_n"] * 100) if d["initial_n"] != 0 else 0
            d["percent_s"] = round(d["change_s"] / d["initial_s"] * 100) if d["initial_s"] != 0 else 0

        # Display data table
        st.markdown("### Calculated Data")
        df = data_to_dataframe(st.session_state.manual_data)
        st.dataframe(df, use_container_width=True)

        # Generate charts
        st.markdown("---")
        st.markdown("### Generated Charts")

        fig = create_charts(st.session_state.manual_data)
        st.pyplot(fig)

        # Download button
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)

        st.download_button(
            label="Download Chart (PNG)",
            data=buf,
            file_name="magnetic_field_chart.png",
            mime="image/png"
        )

# Footer
st.markdown("---")
st.markdown("Made with Streamlit | Magnetic Field Change Analysis Tool")
