# Database Structure Documentation

## Overview
The financial analysis database has been enhanced to include three new relational tables that store comprehensive analysis data for companies. The database now supports:

- **Financial Analysis**: Price targets, analyst summaries, performance metrics, and investment outlooks
- **Sentiment Analysis**: Analyst and market sentiment, risk assessments
- **Leadership Analysis**: Stability assessments, investor implications, and overall impact

## Database Schema

### Core Tables

#### 1. `financials`
Stores basic financial metrics for companies.
```sql
CREATE TABLE financials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    quarter TEXT,
    metric TEXT,
    value REAL
);
```

#### 2. `quarter`
Reference table for quarters.
```sql
CREATE TABLE quarter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quarter TEXT NOT NULL
);
```

### New Analysis Tables

#### 3. `financial_analysis`
Stores comprehensive financial analysis results.
```sql
CREATE TABLE financial_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    quarter TEXT NOT NULL,
    analyst_name TEXT NOT NULL,
    price_target REAL,
    analyst_summary TEXT,
    performance_summary TEXT,
    investment_outlook TEXT,
    expected_values_future_quarters TEXT,
    risk_assessment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker) REFERENCES financials(ticker),
    FOREIGN KEY (quarter) REFERENCES quarter(quarter)
);
```

#### 4. `sentiment_analysis`
Stores sentiment analysis results.
```sql
CREATE TABLE sentiment_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    quarter TEXT NOT NULL,
    analyst_name TEXT NOT NULL,
    analyst_sentiment TEXT,
    market_sentiment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker) REFERENCES financials(ticker),
    FOREIGN KEY (quarter) REFERENCES quarter(quarter)
);
```

#### 5. `leadership_analysis`
Stores leadership analysis results.
```sql
CREATE TABLE leadership_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    quarter TEXT NOT NULL,
    analyst_name TEXT NOT NULL,
    stability_assessment TEXT,
    investor_implications TEXT,
    overall_impact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker) REFERENCES financials(ticker),
    FOREIGN KEY (quarter) REFERENCES quarter(quarter)
);
```

## Usage

### File Naming Convention
Files must be named in the following format for proper analyst attribution:
```
<analyst name> - <ticker> <quarter> <year>.pdf
```

**Examples:**
- `Goldman Sachs - AAPL Q2 2025.pdf`
- `Morgan Stanley - MSFT Q3 2025.pdf`
- `JPMorgan Chase - AMZN Q1 2025.pdf`

If the filename doesn't follow this format, the system will use "Analyst A" as the default analyst name.

### Database Creation
To create the database with all tables:
```bash
python src/createDb.py
```

### Updating Analysis Data

#### Financial Analysis
```python
from src.updateDb import update_financial_analysis

financial_data = {
    'analyst_name': 'Goldman Sachs - John Smith',
    'price_target': 150.0,
    'analyst_summary': 'Strong performance with positive outlook',
    'performance_summary': 'Revenue growth exceeded expectations',
    'investment_outlook': 'Buy',
    'expected_values_future_quarters': 'Q3: $95B, Q4: $98B',
    'risk_assessment': 'Risk Level: Low - Stable fundamentals'
}

update_financial_analysis('AAPL', 'Q2 2025', financial_data)
```

#### Sentiment Analysis
```python
from src.updateDb import update_sentiment_analysis

sentiment_data = {
    'analyst_name': 'Goldman Sachs - John Smith',
    'analyst_sentiment': 'Positive - Strong buy recommendations',
    'market_sentiment': 'Bullish - Market confidence high'
}

update_sentiment_analysis('AAPL', 'Q2 2025', sentiment_data)
```

#### Leadership Analysis
```python
from src.updateDb import update_leadership_analysis

leadership_data = {
    'analyst_name': 'Goldman Sachs - John Smith',
    'stability_assessment': 'High stability - Strong leadership team',
    'investor_implications': 'Positive - Leadership continuity expected',
    'overall_impact': 'Positive - Strong management execution'
}

update_leadership_analysis('AAPL', 'Q2 2025', leadership_data)
```

### Integration with Analysis Scripts

Use the `example_integration.py` script to automatically process analysis and update the database:

```python
from src.example_integration import process_company_analysis_sync

# Process comprehensive analysis for a company
process_company_analysis_sync(
    ticker="AAPL",
    quarter="Q2 2025",
    gemini_api_key="your_api_key",
    content_data=content_for_sentiment_analysis
)
```

## Key Features

1. **Relational Design**: Foreign key constraints ensure data integrity
2. **Upsert Support**: Update functions handle both insert and update operations
3. **Timestamp Tracking**: Automatic creation and update timestamps
4. **Flexible Data Storage**: TEXT fields allow for rich, structured analysis data
5. **Integration Ready**: Functions designed to work with existing analysis scripts
6. **Analyst Tracking**: Extracts analyst name from filename format "<analyst name> - <ticker> <quarter> <year>" (NOT NULL constraint with "Analyst A" fallback)

## Data Flow

1. **File Upload** → Extract analyst name from filename format "<analyst name> - <ticker> <quarter> <year>"
2. **PDF Parsing** → fileParser extracts financial data and content
3. **Analysis Scripts** → Process the data and generate insights
4. **Database Updates** → Update functions store results with analyst attribution from filename
5. **Data Storage** → Relational structure maintains data relationships
6. **Data Retrieval** → Query across tables for comprehensive analysis with analyst tracking

## Notes

- All update functions use upsert logic (INSERT OR UPDATE)
- Foreign key constraints ensure referential integrity
- Timestamps are automatically managed
- The database supports multiple quarters and companies
- Analysis data can be updated incrementally as new information becomes available
- **Analyst name is MANDATORY** - NOT NULL constraint with "Analyst A" fallback if not found
- **Filename format required**: "<analyst name> - <ticker> <quarter> <year>" for proper analyst attribution
- fileParser focuses on financial data extraction (analyst name comes from filename) 