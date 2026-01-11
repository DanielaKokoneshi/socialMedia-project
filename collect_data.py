"""
YouTube Data Collection Script (Steps 5 & 6)

This script collects video metadata from YouTube using the YouTube Data API v3.
It searches for tutorial videos on various IT topics and stores the results.
"""

import os
import json
import time
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config


def create_youtube_client():
    """Create and return a YouTube API client."""
    if not config.YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY not found. Please set it in .env file.")
    
    return build(config.API_SERVICE_NAME, config.API_VERSION, 
                 developerKey=config.YOUTUBE_API_KEY)


def search_videos(youtube, query, max_results=50, published_after=None, 
                  order='relevance', page_token=None):
    """
    Search for videos on YouTube.
    
    Args:
        youtube: YouTube API client
        query: Search query string
        max_results: Maximum number of results (default: 50, max: 50)
        published_after: ISO 8601 date string (e.g., '2019-01-01T00:00:00Z')
        order: Sort order ('relevance', 'viewCount', 'rating', 'date')
        page_token: Token for pagination
    
    Returns:
        Dictionary containing search results
    """
    try:
        request_params = {
            'part': 'snippet',
            'q': query,
            'type': config.VIDEO_TYPE,
            'maxResults': min(max_results, 50), 
            'order': order,
            'relevanceLanguage': config.LANGUAGE,
        }
        
        if published_after:
            request_params['publishedAfter'] = published_after
        
        if page_token:
            request_params['pageToken'] = page_token
        
        request = youtube.search().list(**request_params)
        response = request.execute()
        
        return response
    
    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_video_details(youtube, video_ids):
    """
    Get detailed information for a list of video IDs.
    
    Args:
        youtube: YouTube API client
        video_ids: List of video ID strings
    
    Returns:
        Dictionary containing video details
    """
    try:
        # API allows up to 50 video IDs per request
        video_ids_str = ','.join(video_ids[:50])
        
        request = youtube.videos().list(
            part='statistics,snippet,contentDetails',
            id=video_ids_str
        )
        response = request.execute()
        
        return response
    
    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def extract_video_metadata(video_item):
    """
    Extract relevant metadata from a video item.
    
    Args:
        video_item: Video item from API response
    
    Returns:
        Dictionary with extracted metadata
    """
    snippet = video_item.get('snippet', {})
    statistics = video_item.get('statistics', {})
    
    return {
        'video_id': video_item.get('id', ''),
        'title': snippet.get('title', ''),
        'description': snippet.get('description', ''),
        'published_at': snippet.get('publishedAt', ''),
        'channel_id': snippet.get('channelId', ''),
        'channel_title': snippet.get('channelTitle', ''),
        'view_count': int(statistics.get('viewCount', 0)),
        'like_count': int(statistics.get('likeCount', 0)),
        'comment_count': int(statistics.get('commentCount', 0)),
        'tags': snippet.get('tags', []),
        'category_id': snippet.get('categoryId', ''),
    }


def collect_topic_data(youtube, topic, max_queries=10):
    """
    Collect video data for a specific IT topic.
    
    Args:
        youtube: YouTube API client
        topic: Topic keyword string
        max_queries: Maximum number of search queries to perform
    
    Returns:
        List of video metadata dictionaries
    """
    print(f"\nCollecting data for topic: {topic}")
    all_videos = []
    seen_video_ids = set()
    next_page_token = None
    query_count = 0
    
    while query_count < max_queries:
        query_count += 1
        print(f"  Query {query_count}/{max_queries}...")
        
        
        search_response = search_videos(
            youtube, 
            topic,
            max_results=config.MAX_RESULTS_PER_QUERY,
            published_after=config.PUBLISHED_AFTER,
            order=config.ORDER_BY,
            page_token=next_page_token
        )
        
        if not search_response:
            print(f"  No results or error for query {query_count}")
            break
        
        video_ids = [item['id']['videoId'] 
                    for item in search_response.get('items', []) 
                    if item['id']['kind'] == 'youtube#video']
       
        new_video_ids = [vid for vid in video_ids if vid not in seen_video_ids]
        if not new_video_ids:
            print(f"  No new videos found in query {query_count}")
            break
        
        seen_video_ids.update(new_video_ids)
        
        print(f"  Fetching details for {len(new_video_ids)} videos...")
        details_response = get_video_details(youtube, new_video_ids)
        
        if details_response:
            for video_item in details_response.get('items', []):
                metadata = extract_video_metadata(video_item)
                metadata['topic'] = topic 
                all_videos.append(metadata)
        
        next_page_token = search_response.get('nextPageToken')
        if not next_page_token:
            print(f"  No more pages available for topic: {topic}")
            break
        
        time.sleep(0.1)
    
    print(f"  Collected {len(all_videos)} unique videos for topic: {topic}")
    return all_videos


def save_data(data, filename):
    """Save collected data to a JSON file."""
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
    filepath = os.path.join(config.RAW_DATA_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nData saved to: {filepath}")


def main():
    """Main function to collect data for all IT topics."""
    print("=" * 60)
    print("YouTube IT Skills Data Collection")
    print("=" * 60)
   
    try:
        youtube = create_youtube_client()
        print("YouTube API client created successfully")
    except Exception as e:
        print(f"Error creating YouTube client: {e}")
        return
 
    all_data = []
    
    for topic in config.IT_TOPICS:
        try:
            topic_videos = collect_topic_data(
                youtube, 
                topic, 
                max_queries=config.MAX_QUERIES_PER_TOPIC
            )
            all_data.extend(topic_videos)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_data(all_data, f'youtube_data_{timestamp}.json')

            time.sleep(1)
            
        except Exception as e:
            print(f"Error collecting data for topic '{topic}': {e}")
            continue

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_data(all_data, f'youtube_data_final_{timestamp}.json')
    
    print("\n" + "=" * 60)
    print(f"Data collection complete!")
    print(f"Total videos collected: {len(all_data)}")
    print(f"Unique videos: {len(set(v['video_id'] for v in all_data))}")
    print("=" * 60)


if __name__ == '__main__':
    main()

