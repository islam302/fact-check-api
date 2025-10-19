#!/usr/bin/env python3
"""
Test script for source percentage functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fact_check_with_openai.utils import classify_source_credibility, calculate_source_percentages

def test_source_classification():
    """Test the source classification function"""
    print("🧪 Testing source classification...")
    
    # Test cases for different types of sources
    test_sources = [
        {
            "title": "Official Government Announcement",
            "url": "https://spa.gov.sa/news/official-announcement",
            "snippet": "The ministry announced official statement"
        },
        {
            "title": "Reuters Breaking News",
            "url": "https://reuters.com/world/breaking-news",
            "snippet": "Reuters reports confirmed information"
        },
        {
            "title": "Twitter Post",
            "url": "https://twitter.com/user/status/123",
            "snippet": "Someone claims this happened"
        },
        {
            "title": "Blog Post",
            "url": "https://randomblog.blogspot.com/post",
            "snippet": "This is just a rumor"
        },
        {
            "title": "University Research",
            "url": "https://university.edu/research",
            "snippet": "Academic study confirms"
        }
    ]
    
    for i, source in enumerate(test_sources, 1):
        classification = classify_source_credibility(source)
        print(f"Source {i}: {classification}")
        print(f"  Title: {source['title']}")
        print(f"  URL: {source['url']}")
        print()
    
    # Test percentage calculation
    print("📊 Testing percentage calculation...")
    percentages = calculate_source_percentages(test_sources)
    print(f"Real percentage: {percentages['real_percentage']}%")
    print(f"Unconfirmed percentage: {percentages['unconfirmed_percentage']}%")
    print(f"Total sources: {percentages['total_sources']}")
    print(f"Real count: {percentages['real_count']}")
    print(f"Unconfirmed count: {percentages['unconfirmed_count']}")

if __name__ == "__main__":
    test_source_classification()
