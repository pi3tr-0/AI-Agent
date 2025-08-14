# AI-Agent Project Structure

This document explains the restructured organization of the AI-Agent project, which follows Python best practices and provides better maintainability and scalability.

## Overview

The project has been restructured from a flat `src/` directory to a modular, hierarchical structure that separates concerns and improves code organization.

## Directory Structure

```
AI-Agent/
├── main.py                          # Entry point for the application
├── requirements.txt                 # Python dependencies
├── README.md                       # Project documentation
├── STRUCTURE.md                    # This file - structure documentation
├── test_structure.py               # Import structure verification
├── src/                            # Main source code directory
│   ├── __init__.py                 # Makes src a Python package
│   ├── database/                   # Database operations
│   │   ├── __init__.py
│   │   └── createDb.py             # Database creation and schema
│   ├── analysis/                   # Analysis modules
│   │   ├── __init__.py
│   │   ├── financialAnalysis.py    # Financial health analysis
│   │   ├── sentimentAnalysis.py    # Market sentiment analysis
│   │   ├── leadershipAnalysis.py   # Leadership change analysis
│   │   └── anomalyDetection.py     # Financial anomaly detection
│   ├── data/                       # Data processing modules
│   │   ├── __init__.py
│   │   ├── dbextract.py            # Data extraction from database
│   │   ├── fileParser.py           # PDF file parsing
│   │   └── updateDb.py             # Database update operations
│   ├── search/                     # Search functionality
│   │   ├── __init__.py
│   │   ├── internetSearch.py       # Internet search for news/sentiment
│   │   └── leadershipSearch.py     # Leadership change search
│   ├── tools/                      # AI tools and utilities
│   │   ├── __init__.py
│   │   └── anomalyDetection.py     # Anomaly detection tool for AI agents
│   ├── utils/                      # Utility functions
│   │   ├── __init__.py
│   │   └── summarizer.py           # PDF summarization utility
│   └── web/                        # Web interface (future use)
│       └── __init__.py
├── tests/                          # Test files
│   ├── test_financial_analysis.py
│   ├── test_leadership_analysis.py
│   └── test_fixes.py
└── util/                           # Static resources
    ├── database/                   # SQLite database files
    ├── image/                      # Images and diagrams
    ├── markdown/                   # Documentation files
    └── pdf-reports/                # Sample PDF reports
```

## Module Organization

### Main Modules (`src/`)

The functionality is organized into four main categories:

#### 1. Database (`src/database/`)
- **createDb.py**: Handles database creation, schema definition, and initial data population
- Responsible for setting up the SQLite database with financial metrics tables

#### 2. Analysis (`src/analysis/`)
- **financialAnalysis.py**: Performs comprehensive financial health analysis using AI
- **sentimentAnalysis.py**: Analyzes market and analyst sentiment from various sources
- **leadershipAnalysis.py**: Evaluates leadership changes and their impact on companies
- **anomalyDetection.py**: Detects financial anomalies using statistical methods

#### 3. Data (`src/data/`)
- **dbextract.py**: Extracts financial data from the database for analysis
- **fileParser.py**: Parses PDF financial reports and extracts structured data
- **updateDb.py**: Updates the database with new financial and analysis data

#### 4. Search (`src/search/`)
- **internetSearch.py**: Searches the internet for recent financial news and sentiment
- **leadershipSearch.py**: Searches for leadership changes and executive updates

### Tools (`src/tools/`)
- **anomalyDetection.py**: AI tool for anomaly detection that can be used by AI agents

### Utils (`src/utils/`)
- **summarizer.py**: Utility for summarizing PDF documents

## Import Structure

The new structure uses explicit import paths that clearly indicate the module hierarchy:

```python
# Before (flat structure)
from src import fileParser, financialAnalysis, sentimentAnalysis

# After (organized structure)
from src.data import fileParser
from src.analysis import financialAnalysis, sentimentAnalysis
from src.search import internetSearch
from src.tools import anomalyDetection
```

## Benefits of This Structure

### 1. **Separation of Concerns**
- Database operations are isolated in their own module
- Analysis logic is separated from data processing
- Search functionality is independent of core analysis

### 2. **Maintainability**
- Related functionality is grouped together
- Easy to locate specific features
- Clear dependencies between modules

### 3. **Scalability**
- Easy to add new analysis types
- Simple to extend data processing capabilities
- Modular design allows for independent development

### 4. **Testability**
- Each module can be tested independently
- Clear boundaries make unit testing straightforward
- Mock dependencies are easier to implement

### 5. **Code Reusability**
- Analysis modules can be reused across different contexts
- Data processing utilities can be shared
- Tools can be used by multiple AI agents


This will verify that all modules can be imported with the new structure and that the restructuring was successful. 