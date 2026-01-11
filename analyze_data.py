"""
Data Analysis Script (Step 8)

This script analyzes the cleaned YouTube data to identify trends in IT skill popularity:
- Number of tutorial videos published per topic per year
- Average views and likes per topic over time
- Growth or decline trends in engagement
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import glob
import config

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


def load_cleaned_data(data_dir=None):
    """
    Load cleaned data from CSV or JSON files.
    
    Args:
        data_dir: Directory containing processed data files
    
    Returns:
        DataFrame with cleaned data
    """
    if data_dir is None:
        data_dir = config.PROCESSED_DATA_DIR
    
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
    
    if csv_files:
        latest_file = max(csv_files, key=os.path.getctime)
        print(f"Loading data from: {os.path.basename(latest_file)}")
        df = pd.read_csv(latest_file)
        return df

    json_files = glob.glob(os.path.join(data_dir, '*.json'))
    if json_files:
        latest_file = max(json_files, key=os.path.getctime)
        print(f"Loading data from: {os.path.basename(latest_file)}")
        df = pd.read_json(latest_file)
        return df
    
    print(f"No data files found in {data_dir}")
    print("Please run clean_data.py first.")
    return None


def analyze_publication_trends(df):
    """
    Analyze number of tutorial videos published per topic per year.
    
    Args:
        df: DataFrame with cleaned data
    
    Returns:
        DataFrame with publication trends
    """
    print("\n" + "=" * 60)
    print("Analysis 1: Publication Trends")
    print("=" * 60)
    
    publication_trends = df.groupby(['main_topic', 'publication_year']).size().reset_index(name='video_count')

    trends_pivot = publication_trends.pivot(index='publication_year', 
                                           columns='main_topic', 
                                           values='video_count').fillna(0)
    
    print("\nVideos published per topic per year:")
    print(trends_pivot.to_string())
    
    return publication_trends, trends_pivot


def analyze_engagement_trends(df):
    """
    Analyze average views and likes per topic over time.
    
    Args:
        df: DataFrame with cleaned data
    
    Returns:
        Dictionary with engagement metrics
    """
    print("\n" + "=" * 60)
    print("Analysis 2: Engagement Trends")
    print("=" * 60)
    
    engagement = df.groupby(['main_topic', 'publication_year']).agg({
        'view_count': 'mean',
        'like_count': 'mean',
        'avg_views_per_year': 'mean',
        'engagement_rate': 'mean'
    }).round(2).reset_index()
    
    print("\nAverage engagement metrics per topic per year:")
    print(engagement.to_string())
    
    return engagement


def analyze_growth_trends(df):
    """
    Analyze growth or decline trends in engagement.
    
    Args:
        df: DataFrame with cleaned data
    
    Returns:
        DataFrame with growth rates
    """
    print("\n" + "=" * 60)
    print("Analysis 3: Growth/Decline Trends")
    print("=" * 60)

    current_year = datetime.now().year
    min_year = current_year - 5

    yearly_stats = df.groupby(['main_topic', 'publication_year']).agg({
        'video_id': 'count',
        'view_count': 'mean',
        'like_count': 'mean',
        'avg_views_per_year': 'mean'
    }).reset_index()
    yearly_stats.columns = ['topic', 'year', 'video_count', 'avg_views', 'avg_likes', 'avg_views_per_year']

    growth_data = []
    for topic in yearly_stats['topic'].unique():
        topic_data = yearly_stats[yearly_stats['topic'] == topic].sort_values('year')
        
        for i in range(1, len(topic_data)):
            prev_row = topic_data.iloc[i-1]
            curr_row = topic_data.iloc[i]
            
            video_growth = ((curr_row['video_count'] - prev_row['video_count']) / 
                          prev_row['video_count'] * 100) if prev_row['video_count'] > 0 else 0
            view_growth = ((curr_row['avg_views'] - prev_row['avg_views']) / 
                          prev_row['avg_views'] * 100) if prev_row['avg_views'] > 0 else 0
            
            growth_data.append({
                'topic': topic,
                'year': curr_row['year'],
                'video_count_growth_pct': round(video_growth, 2),
                'avg_views_growth_pct': round(view_growth, 2)
            })
    
    growth_df = pd.DataFrame(growth_data)
    
    if not growth_df.empty:
        print("\nYear-over-year growth rates:")
        print(growth_df.to_string())
    
    return growth_df, yearly_stats


def create_visualizations(df, publication_trends, trends_pivot, engagement, yearly_stats):
    """
    Create visualizations for the analyses.
    
    Args:
        df: Original DataFrame
        publication_trends: Publication trends DataFrame
        trends_pivot: Pivoted publication trends
        engagement: Engagement trends DataFrame
        yearly_stats: Yearly statistics DataFrame
    """
    print("\n" + "=" * 60)
    print("Creating Visualizations")
    print("=" * 60)
    
    os.makedirs('results', exist_ok=True)
    
    # Figure 1: Videos published per topic per year
    plt.figure(figsize=(14, 8))
    for topic in trends_pivot.columns:
        plt.plot(trends_pivot.index, trends_pivot[topic], marker='o', label=topic, linewidth=2)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Number of Videos Published', fontsize=12)
    plt.title('IT Tutorial Videos Published per Topic Over Time', fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/publication_trends.png', dpi=300, bbox_inches='tight')
    print("Saved: results/publication_trends.png")
    plt.close()
    
    # Figure 2: Average views per topic over time
    plt.figure(figsize=(14, 8))
    for topic in engagement['main_topic'].unique():
        topic_data = engagement[engagement['main_topic'] == topic].sort_values('publication_year')
        plt.plot(topic_data['publication_year'], topic_data['view_count'], 
                marker='o', label=topic, linewidth=2)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Average View Count', fontsize=12)
    plt.title('Average Views per Topic Over Time', fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/engagement_views.png', dpi=300, bbox_inches='tight')
    print("Saved: results/engagement_views.png")
    plt.close()
    
    # Figure 3: Average likes per topic over time
    plt.figure(figsize=(14, 8))
    for topic in engagement['main_topic'].unique():
        topic_data = engagement[engagement['main_topic'] == topic].sort_values('publication_year')
        plt.plot(topic_data['publication_year'], topic_data['like_count'], 
                marker='o', label=topic, linewidth=2)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Average Like Count', fontsize=12)
    plt.title('Average Likes per Topic Over Time', fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/engagement_likes.png', dpi=300, bbox_inches='tight')
    print("Saved: results/engagement_likes.png")
    plt.close()
    
    # Figure 4: Heatmap of videos by topic and year
    plt.figure(figsize=(12, 8))
    heatmap_data = trends_pivot.T
    sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd', 
                cbar_kws={'label': 'Number of Videos'})
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Topic', fontsize=12)
    plt.title('Heatmap: Videos Published by Topic and Year', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/publication_heatmap.png', dpi=300, bbox_inches='tight')
    print("Saved: results/publication_heatmap.png")
    plt.close()
    
    # Figure 5: Total videos by year (all topics combined)
    plt.figure(figsize=(10, 6))
    yearly_total = df.groupby('publication_year').size()
    plt.bar(yearly_total.index, yearly_total.values, color='steelblue', alpha=0.7)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Total Videos', fontsize=12)
    plt.title('Total IT Tutorial Videos Published per Year', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y')
    for year, count in yearly_total.items():
        plt.text(year, count, str(count), ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig('results/yearly_total.png', dpi=300, bbox_inches='tight')
    print("Saved: results/yearly_total.png")
    plt.close()
    
    print("\nAll visualizations saved to 'results/' directory")


def generate_summary_report(df, publication_trends, engagement, growth_df):
    """
    Generate a text summary report of findings.
    
    Args:
        df: Original DataFrame
        publication_trends: Publication trends DataFrame
        engagement: Engagement trends DataFrame
        growth_df: Growth trends DataFrame
    """
    os.makedirs('results', exist_ok=True)
    report_path = 'results/analysis_report.txt'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("YouTube IT Skills Trend Analysis Report\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("EXECUTIVE SUMMARY\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total videos analyzed: {len(df)}\n")
        f.write(f"Date range: {df['publication_year'].min()} - {df['publication_year'].max()}\n")
        f.write(f"Topics analyzed: {df['main_topic'].nunique()}\n\n")
        
        f.write("KEY FINDINGS\n")
        f.write("-" * 60 + "\n")
        
        # Most popular topics by video count
        topic_counts = df['main_topic'].value_counts()
        f.write(f"\nMost popular topics (by video count):\n")
        for topic, count in topic_counts.head(5).items():
            f.write(f"  - {topic}: {count} videos\n")
        
        # Topics with highest average views
        avg_views_by_topic = df.groupby('main_topic')['view_count'].mean().sort_values(ascending=False)
        f.write(f"\nTopics with highest average views:\n")
        for topic, views in avg_views_by_topic.head(5).items():
            f.write(f"  - {topic}: {views:,.0f} average views\n")
        
        # Growth trends
        if not growth_df.empty:
            f.write(f"\nGrowth Trends:\n")
            recent_growth = growth_df[growth_df['year'] == growth_df['year'].max()]
            if not recent_growth.empty:
                fastest_growing = recent_growth.nlargest(3, 'video_count_growth_pct')
                f.write(f"  Fastest growing topics (by video count):\n")
                for _, row in fastest_growing.iterrows():
                    f.write(f"    - {row['topic']}: {row['video_count_growth_pct']:.1f}% growth\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("For detailed visualizations, see the PNG files in this directory.\n")
    
    print(f"\nSummary report saved to: {report_path}")


def main():
    """Main function to perform data analysis."""
    print("=" * 60)
    print("YouTube IT Skills Trend Analysis")
    print("=" * 60)

    df = load_cleaned_data()
    
    if df is None or df.empty:
        print("No data available for analysis.")
        return
   
    df['publication_year'] = df['publication_year'].astype(int)
    
    publication_trends, trends_pivot = analyze_publication_trends(df)
    engagement = analyze_engagement_trends(df)
    growth_df, yearly_stats = analyze_growth_trends(df)

    create_visualizations(df, publication_trends, trends_pivot, engagement, yearly_stats)
    
    generate_summary_report(df, publication_trends, engagement, growth_df)
    
    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()

