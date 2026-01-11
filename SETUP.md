# Setup Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key**
   - Create a `.env` file in the project root
   - Add your YouTube Data API v3 key:
     ```
     YOUTUBE_API_KEY=your_actual_api_key_here
     ```

3. **Run the Pipeline**
   ```bash
   # Step 1: Collect data
   python collect_data.py
   
   # Step 2: Clean data
   python clean_data.py
   
   # Step 3: Analyze data
   python analyze_data.py
   ```

## API Key Setup

If you haven't already set up your YouTube Data API v3 key (Step 4):

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3
4. Create credentials (API Key)
5. Copy the API key to your `.env` file

## Understanding the Quota

- **Default daily quota**: 10,000 units
- **Search request**: 100 units per request
- **Video details request**: 1 unit per video

With default settings:
- Each topic searches up to 10 times (10 × 100 = 1,000 units)
- Each search can return up to 50 videos (50 × 1 = 50 units per search)
- Total per topic: ~1,500 units


## Output Files

- **Raw data**: `data/raw/youtube_data_*.json`
- **Cleaned data**: `data/processed/cleaned_youtube_data_*.csv`
- **Visualizations**: `results/*.png`
- **Analysis report**: `results/analysis_report.txt`

