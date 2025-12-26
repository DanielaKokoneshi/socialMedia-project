# YouTube IT Skills Trend Analysis

This project investigates how public interest in IT-related skills has changed over time on YouTube by analyzing tutorial videos covering topics such as programming, data analysis, cybersecurity, AI, and cloud computing.

## Project Overview

The application collects and analyzes data from YouTube tutorial videos to identify which IT topics have gained or lost popularity during the past five years. The results provide insights into changing learning trends and demonstrate YouTube's role as a platform for developing digital skills.

## Features

- **Data Collection**: Automated collection of YouTube video metadata using YouTube Data API v3
- **Data Cleaning**: Preprocessing and normalization of collected data
- **Trend Analysis**: Analysis of publication trends, view counts, and engagement metrics over time
- **Visualizations**: Charts and graphs showing trends in IT skill popularity

## Setup

### Prerequisites

- Python 3.8 or higher
- Google Cloud Project with YouTube Data API v3 enabled
- YouTube Data API v3 API key

### Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root:
   ```
   YOUTUBE_API_KEY=your_api_key_here
   ```

## Usage

### Step 1: Collect Data
```bash
python collect_data.py
```

### Step 2: Clean and Prepare Data
```bash
python clean_data.py
```

### Step 3: Analyze Data
```bash
python analyze_data.py
```

## Project Structure

```
.
├── collect_data.py      # Data collection script (Steps 5 & 6)
├── clean_data.py        # Data cleaning script (Step 7)
├── analyze_data.py      # Analysis script (Step 8)
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── data/               # Data storage directory
    ├── raw/            # Raw collected data
    └── processed/      # Cleaned and processed data
```

## API Quota Limits

The YouTube Data API v3 has the following default quota limits:
- **Daily quota**: 10,000 units per day (default)
- **Search request**: 100 units per request
- **Video details request**: 1 unit per request

This means approximately 100 search queries per day with the default quota. For larger datasets, consider:
- Requesting a quota increase from Google Cloud Console
- Implementing rate limiting and caching
- Collecting data over multiple days

## Notes

- The prototype is intended for analysis and experimentation, not for production use.
- Data collection respects YouTube's Terms of Service and API usage policies.
- Results are based on publicly available video metadata only.

