# Data Directory

This directory contains JSON files for investment analysis reports.

## File Naming Convention

For automatic parsing and display, use the following naming convention:

```
COMPANY_Q#_YEAR_ANALYST_combined_analysis.json
```

Examples:
- `AAPL_Q2_2025_Analyst_A_combined_analysis.json`
- `AMZN_Q1_2025_John_Smith_combined_analysis.json`
- `GOOGL_Q4_2024_Financial_Team_combined_analysis.json`

**Note**: The analyst name should use underscores instead of spaces, hyphens, or periods.

## Adding New Files

1. Place your JSON file in this directory (`public/data/`)
2. Follow the naming convention above for automatic parsing
3. The file selector will automatically detect and display new files
4. Files are sorted by year (newest first), then by quarter, then by company ticker

## File Structure

Each JSON file should contain the following structure:

```json
{
  "metadata": {
    "analysis_timestamp": "string",
    "analyst_name": "string",
    "original_filename": "string",
    "analysis_version": "string"
  },
  "parsed_content": {
    "financialMetrics": { ... },
    "analyst": { ... }
  },
  "financial_analysis": { ... },
  "sentiment_analysis": { ... },
  "leadership_analysis": { ... }
}
```

## Automatic Features

- **Dynamic Loading**: Files are automatically detected and listed
- **Smart Parsing**: Company ticker, quarter, and year are extracted from filename
- **Sorting**: Files are automatically sorted by date and company
- **Error Handling**: Invalid files are gracefully handled
- **Refresh**: Use the refresh button to reload the file list

## Current Files

- `AAPL_Q2_2025_combined_analysis.json` - Apple Inc. Q2 2025 Analysis (Legacy format)
- `AMZN_Q2_2025_combined_analysis.json` - Amazon.com Inc. Q2 2025 Analysis (Legacy format)

**Note**: These files use the old naming convention without analyst names. New files will include analyst names in the format shown above. 