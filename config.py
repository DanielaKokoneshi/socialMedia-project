"""
Configuration management for YouTube Data API access.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# YouTube Data API Configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')

# API Settings
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# Data Collection Settings
IT_TOPICS = [
    'cybersecurity tutorial',
    'machine learning tutorial',
    'cloud computing tutorial',
    'python programming tutorial',
    'web development tutorial',
    'data science tutorial'
]

# Search Parameters
MAX_RESULTS_PER_QUERY = 50  # Maximum videos per search query (API limit)
MAX_QUERIES_PER_TOPIC = 10  # Number of search queries per topic
PUBLISHED_AFTER = '2019-01-01T00:00:00Z'  # Last 5 years
LANGUAGE = 'en'  # English language content
VIDEO_TYPE = 'video'  # Only videos, not playlists or channels
ORDER_BY = 'relevance'  # Order by relevance (alternative: 'viewCount')

# Data Storage
RAW_DATA_DIR = 'data/raw'
PROCESSED_DATA_DIR = 'data/processed'

