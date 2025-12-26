"""
Data Cleaning and Preparation Script (Step 7)

This script cleans and preprocesses the collected YouTube data:
- Removes duplicate videos
- Converts publication dates to years
- Normalizes view counts
- Handles missing or unavailable metrics
"""

import os
import json
import pandas as pd
from datetime import datetime
import glob
import config


def load_raw_data(data_dir=None):
    """
    Load all raw JSON data files.
    
    Args:
        data_dir: Directory containing raw data files
    
    Returns:
        List of video dictionaries
    """
    if data_dir is None:
        data_dir = config.RAW_DATA_DIR
    
    all_data = []
    json_files = glob.glob(os.path.join(data_dir, '*.json'))
    
    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return all_data
    
    print(f"Found {len(json_files)} data file(s)")
    
    for filepath in json_files:
        print(f"  Loading: {os.path.basename(filepath)}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
        except Exception as e:
            print(f"  Error loading {filepath}: {e}")
    
    print(f"Total records loaded: {len(all_data)}")
    return all_data


def remove_duplicates(df):
    """
    Remove duplicate videos based on video_id.
    
    Args:
        df: DataFrame with video data
    
    Returns:
        DataFrame with duplicates removed
    """
    initial_count = len(df)
    df = df.drop_duplicates(subset=['video_id'], keep='first')
    removed = initial_count - len(df)
    
    if removed > 0:
        print(f"Removed {removed} duplicate video(s)")
    
    return df


def extract_year_from_date(date_string):
    """
    Extract year from ISO 8601 date string.
    
    Args:
        date_string: ISO 8601 formatted date string
    
    Returns:
        Year as integer, or None if parsing fails
    """
    try:
        if date_string:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.year
    except (ValueError, AttributeError):
        pass
    return None


def normalize_view_counts(df):
    """
    Normalize view counts by calculating average views per year.
    
    Args:
        df: DataFrame with video data
    
    Returns:
        DataFrame with normalized view counts
    """
    df = df.copy()
    
    # Calculate years since publication
    current_year = datetime.now().year
    df['years_since_publication'] = current_year - df['publication_year'] + 1
    df['years_since_publication'] = df['years_since_publication'].clip(lower=1)
    
    # Calculate average views per year
    df['avg_views_per_year'] = df['view_count'] / df['years_since_publication']
    df['avg_views_per_year'] = df['avg_views_per_year'].round(2)
    
    return df


def handle_missing_data(df):
    """
    Handle missing or unavailable metrics.
    
    Args:
        df: DataFrame with video data
    
    Returns:
        DataFrame with missing data handled
    """
    df = df.copy()
    
    # Fill missing numeric values with 0
    numeric_columns = ['view_count', 'like_count', 'comment_count']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # Fill missing string values
    string_columns = ['title', 'channel_title', 'description']
    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')
    
    # Handle missing publication dates
    df = df[df['publication_year'].notna()]  # Remove rows without valid dates
    
    return df


def clean_data(df):
    """
    Main data cleaning function.
    
    Args:
        df: Raw DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    print("\n" + "=" * 60)
    print("Data Cleaning and Preparation")
    print("=" * 60)
    
    print(f"\nInitial record count: {len(df)}")
    
    # Step 1: Remove duplicates
    print("\nStep 1: Removing duplicates...")
    df = remove_duplicates(df)
    
    # Step 2: Convert publication dates to years
    print("\nStep 2: Converting publication dates to years...")
    df['publication_year'] = df['published_at'].apply(extract_year_from_date)
    invalid_dates = df['publication_year'].isna().sum()
    if invalid_dates > 0:
        print(f"  Found {invalid_dates} records with invalid dates")
    
    # Step 3: Handle missing data
    print("\nStep 3: Handling missing data...")
    df = handle_missing_data(df)
    
    # Step 4: Normalize view counts
    print("\nStep 4: Normalizing view counts...")
    df = normalize_view_counts(df)
    
    # Step 5: Filter to last 5 years
    print("\nStep 5: Filtering to last 5 years...")
    current_year = datetime.now().year
    min_year = current_year - 5
    df = df[df['publication_year'] >= min_year]
    print(f"  Records after filtering: {len(df)}")
    
    # Step 6: Add additional derived fields
    print("\nStep 6: Adding derived fields...")
    df['engagement_rate'] = (df['like_count'] / df['view_count'].replace(0, 1) * 100).round(2)
    df['engagement_rate'] = df['engagement_rate'].fillna(0)
    
    # Extract main topic from topic string (remove "tutorial" suffix)
    df['main_topic'] = df['topic'].str.replace(' tutorial', '', case=False)
    
    print(f"\nFinal record count: {len(df)}")
    print("=" * 60)
    
    return df


def save_cleaned_data(df, filename=None):
    """
    Save cleaned data to CSV and JSON formats.
    
    Args:
        df: Cleaned DataFrame
        filename: Optional filename (without extension)
    """
    os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'cleaned_youtube_data_{timestamp}'
    
    # Save as CSV
    csv_path = os.path.join(config.PROCESSED_DATA_DIR, f'{filename}.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"\nCleaned data saved to CSV: {csv_path}")
    
    # Save as JSON
    json_path = os.path.join(config.PROCESSED_DATA_DIR, f'{filename}.json')
    df.to_json(json_path, orient='records', indent=2, date_format='iso')
    print(f"Cleaned data saved to JSON: {json_path}")


def main():
    """Main function to clean and prepare data."""
    # Load raw data
    raw_data = load_raw_data()
    
    if not raw_data:
        print("No data to clean. Please run collect_data.py first.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(raw_data)
    
    # Clean data
    cleaned_df = clean_data(df)
    
    # Save cleaned data
    save_cleaned_data(cleaned_df)
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("Data Summary")
    print("=" * 60)
    print(f"\nTotal videos: {len(cleaned_df)}")
    print(f"Date range: {cleaned_df['publication_year'].min()} - {cleaned_df['publication_year'].max()}")
    print(f"\nVideos by topic:")
    print(cleaned_df['main_topic'].value_counts().to_string())
    print(f"\nVideos by year:")
    print(cleaned_df['publication_year'].value_counts().sort_index().to_string())
    print("=" * 60)


if __name__ == '__main__':
    main()

