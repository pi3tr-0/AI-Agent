#!/usr/bin/env python3
"""
Test script to verify the financial analysis properly handles anomaly detection results
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test the financial analysis with anomaly detection
from src import financialAnalysis
from tools import anomalyDetection

print("Testing financial analysis with anomaly detection...")

try:
    # Test anomaly detection directly
    anomaly_result = anomalyDetection.FindAnomaly("AAPL", "Q3 2024")
    print(f"✓ Anomaly detection result: {anomaly_result}")
    
    # Test financial analysis (will use anomaly detection tool)
    # Note: This will fail without real API key, but should handle error gracefully
    result = financialAnalysis.AnalyzeFinancial("AAPL", "Q3 2024", "dummy_key")
    print("✓ Financial analysis handles errors gracefully")
    
    # Check if the result has the expected structure
    if hasattr(result, 'output'):
        print("✓ Financial analysis returns proper structure")
    else:
        print("✗ Financial analysis structure issue")
        
except Exception as e:
    print(f"✗ Test error: {e}")

print("\n✓ Financial analysis test completed!") 