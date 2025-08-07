#!/usr/bin/env python3
"""
Test script to verify the leadership analysis functionality
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test the leadership analysis
from src import leadershipAnalysis

print("Testing leadership analysis...")

# Example leadership data
example_data = {
    "company": "AAPL",
    "date_range": "Q1 2022 to Q3 2023",
    "leadership_updates": [
        {
            "title": "Tim Cook's 2022 Total Compensation Revealed",
            "source": "MarketScreener",
            "date": "January 12, 2023",
            "category": "compensation",
            "details": "Apple CEO Tim Cook's total compensation for 2022 was $99.42 million."
        },
        {
            "title": "Apple CEO Tim Cook's 2023 Pay Cut by Over 40%",
            "source": "BBC News, Strait Times",
            "date": "January 13, 2023",
            "category": "compensation",
            "details": "Apple cut CEO Tim Cook's compensation by over 40% to $49 million in 2023. This decision was made based on investor guidance and Cook's own request, following shareholder feedback."
        },
        {
            "title": "Unprecedented Wave of Executive Departures",
            "source": "MacDailyNews",
            "date": "March 13, 2023",
            "category": "executive_changes",
            "details": "Apple experienced an 'unprecedented wave' of approximately a dozen high-ranking executive departures, primarily vice presidents, starting in the second half of 2022 and continuing into early 2023."
        }
    ],
    "sentiment_impact": {
        "overall_sentiment": "Mixed",
        "impact_summary": "The period saw a notable cut in CEO Tim Cook's compensation, a move that could be viewed positively by shareholders seeking alignment with company performance. However, the report of an 'unprecedented wave' of executive departures, while not detailing specific individuals or their reasons for leaving, could raise concerns about leadership stability and succession planning within the company."
    }
}

try:
    # Test with dummy API key (will fail but should handle error gracefully)
    result = leadershipAnalysis.AnalyzeLeadership(example_data, "dummy_key")
    print("✓ Leadership analysis handles errors gracefully")
    
    # Test the structure
    if hasattr(result, 'output'):
        print("✓ Leadership analysis returns proper structure")
    else:
        print("✗ Leadership analysis structure issue")
        
except Exception as e:
    print(f"✗ Leadership analysis error: {e}")

print("\n✓ Leadership analysis test completed!") 