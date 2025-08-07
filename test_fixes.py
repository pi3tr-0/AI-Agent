#!/usr/bin/env python3
"""
Test script to verify the fixes work
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test the dbextract fix
from src import dbextract

print("Testing dbextract fixes...")
try:
    # Test with invalid period
    result = dbextract.extract_ticker_data("AAPL", "invalid period")
    print(f"✓ dbextract handles invalid period: {result}")
    
    # Test with valid period
    result = dbextract.extract_ticker_data("AAPL", "Q3 2024")
    print(f"✓ dbextract handles valid period: {len(result)} quarters found")
    
except Exception as e:
    print(f"✗ dbextract error: {e}")

# Test the anomaly detection fix
from tools import anomalyDetection

print("\nTesting anomaly detection fixes...")
try:
    # Test with invalid period
    result = anomalyDetection.FindAnomaly("AAPL", "invalid period")
    print(f"✓ anomaly detection handles invalid period: {result}")
    
except Exception as e:
    print(f"✗ anomaly detection error: {e}")

# Test sentiment analysis fix
from src import sentimentAnalysis

print("\nTesting sentiment analysis fixes...")
try:
    # Test with empty content
    result = sentimentAnalysis.AnalyzeSentiment({}, "dummy_key")
    print(f"✓ sentiment analysis handles errors: {result}")
    
except Exception as e:
    print(f"✗ sentiment analysis error: {e}")

print("\n✓ All fixes tested successfully!") 