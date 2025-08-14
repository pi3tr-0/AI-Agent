# Combined Analysis Feature

This feature combines all analysis results (financial, sentiment, leadership, and parsed content) into a single comprehensive JSON file with a Streamlit download button.

## Features

### 1. Combined Analysis Structure
The combined JSON includes:
- **Metadata**: Timestamp, analyst name, original filename, analysis version
- **Parsed Content**: Full output from fileParser
- **Financial Analysis**: Complete financial health assessment
- **Sentiment Analysis**: Market and analyst sentiment analysis
- **Leadership Analysis**: Leadership stability and impact assessment
- **Summary**: Overview of analysis status and key metrics

### 2. Streamlit Integration
- **Download Button**: Users can download the combined analysis as a JSON file
- **Summary Display**: Shows analysis status, total sections, version, and timestamp
- **Expandable View**: Full combined results available in an expandable section
- **Error Handling**: Graceful handling of analysis failures

### 3. File Management
- **Automatic Naming**: Files are named with format: `{TICKER}_{PERIOD}_{TIMESTAMP}_combined_analysis.json`
- **Reports Directory**: All generated files are saved to the `reports/` directory
- **JSON Format**: Properly formatted JSON with indentation and UTF-8 encoding

## Usage

### In Streamlit App
1. Upload a PDF file through the chat interface
2. Wait for all analyses to complete
3. View the "Combined Analysis Summary" section
4. Click the "📥 Download Combined Analysis (JSON)" button
5. Optionally expand "📋 View Complete Combined Analysis" to see full results

### Programmatic Usage
```python
from src.utils.combineAnalysis import combine_analysis_results, get_combined_results_json

# Combine results
combined_results = combine_analysis_results(
    parsed_content=content,
    financial_analysis=financial_result,
    sentiment_analysis=sentiment_result,
    leadership_analysis=leadership_result,
    analyst_name="Analyst Name",
    filename="original_file.pdf"
)

# Get JSON string for download
json_string = get_combined_results_json(combined_results)
```

## JSON Structure Example

```json
{
  "metadata": {
    "analysis_timestamp": "2025-08-13T02:52:26.099184",
    "analyst_name": "Analyst A",
    "original_filename": "A - AAPL Q2 2025.pdf",
    "analysis_version": "1.0"
  },
  "parsed_content": {
    "ticker": "AAPL",
    "period": "Q2 2025",
    "financialMetrics": {...},
    "analyst": {...}
  },
  "financial_analysis": {
    "company_ticker": "AAPL",
    "financial_health_score": {...},
    "investment_outlook": "Buy",
    "performance_summary": "..."
  },
  "sentiment_analysis": {
    "overall_sentiment": "Positive",
    "analyst_sentiment": {...},
    "market_sentiment": {...}
  },
  "leadership_analysis": {
    "stability_assessment": {...},
    "overall_impact": "Positive",
    "investor_implications": "..."
  },
  "summary": {
    "ticker": "AAPL",
    "period": "Q2 2025",
    "analyst_name": "Analyst A",
    "analysis_status": "completed",
    "total_sections": 4
  }
}
```

## Error Handling

The system handles various error scenarios:
- **Missing Analysis Results**: If any analysis fails, it's marked as an error in the JSON
- **Serialization Errors**: If data can't be serialized, error details are included
- **File System Errors**: Graceful handling of directory creation and file writing
- **Streamlit Errors**: User-friendly error messages in the interface

## Files Modified

1. **`src/utils/combineAnalysis.py`**: New utility module for combining results
2. **`main.py`**: Added import and integration of combine functionality
3. **`reports/`**: New directory for storing generated JSON files

## Benefits

- **Comprehensive View**: All analysis results in one place
- **Easy Export**: Simple download functionality for data portability
- **Structured Data**: Well-organized JSON format for further processing
- **Error Resilience**: Continues working even if some analyses fail
- **User-Friendly**: Clear interface with progress indicators and summaries 