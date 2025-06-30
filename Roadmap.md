# AI Agent Roadmap
[Figma Link](https://www.figma.com/board/cicoU002Rqsgz9tCknewgn/Welcome-to-FigJam?node-id=0-1&t=1d9werCLVVBJdkXF-1)
---

## Phase 1 – Core Intelligence Layer

![Phase 1 Structure](./image/phase%20structure/Phase%201.png)

### 1. Financial Report Summarizer
- **Purpose:** Automatically generate concise summaries of quarterly earnings call transcripts or 10-K/10-Q filings.
- **Tech:**
  - Extractive + abstractive summarization using LLMs
  - RAG over vectorized filings (using FAISS + LangChain)
  - Table & text extraction from PDFs (e.g., `pdfplumber`, `PyMuPDF`)

### 2. Red Flag Detection (Anomaly/Concern Detection)
- **Purpose:** Identify sudden financial shifts, audit red flags, or outlier ratios vs. historical data.
- **Tech:**
  - Ratio analysis with rules (e.g., >30% YoY debt growth triggers flag)
  - Historical z-score deviation checks (e.g., 3σ method)

### 3. Basic Forecasting (Rule-Based or Linear)
- **Purpose:** Predict basic financial metrics like revenue growth, bankruptcy risk, or cash flow trajectory.
- **Tech:**
  - Time series modeling (linear regression, exponential smoothing)
  - Feature engineering from 5+ years of financials

### Limitations / Risks
1. **Unstructured data:** Parsing tables and notes from PDF/HTML filings is error-prone and non-standardized.
2. **Inconsistent terminology:** Metrics vary by company (e.g., “Sales Revenue” vs. “Net Turnover”)—requires normalization layer.
3. **Data sparsity:** Some companies (especially new or private ones) have too little historical data for meaningful forecasts.
4. **Forecasting oversimplification:** Rule-based and linear models may miss nonlinear patterns, shocks, or macro effects.

### Outcome
A working prototype that:
- Reads and summarizes a financial report
- Detects anomalies or potential concerns
- Provides basic projections of future performance

---

## Phase 2 – Smart Retrieval & Executive Insight

### 1. Management Team Insight
- **Purpose:** Profile current executives and assess their historical impact on company performance.
- **Tech:**
  - Named Entity Recognition (NER) for identifying executives in filings
  - NLP over bios, news articles (e.g., career history, tenure)
  - Sentiment analysis (e.g., FinBERT) to gauge tone in recent mentions

### 2. Query-Based Report Search (RAG)
- **Purpose:** Enable users to ask natural language questions about the company (e.g., “How has debt changed over 5 years?”) and get direct answers from past reports.
- **Tech:**
  - Retrieval-Augmented Generation (RAG) using LangChain/LlamaIndex + vector DB (FAISS, Weaviate)
  - Semantic chunking of filings and fine-tuned query retrievers
  - Post-processing layer to format numeric answers (e.g., trends, tables, charts)

### Limitations / Risks
1. **Executive name ambiguity:** Common names make entity linking difficult without company-specific context.
2. **Missing or incomplete bios:** Smaller or private companies often don’t disclose detailed background data.
3. **RAG latency/accuracy:** Chunking errors or weak embeddings may return irrelevant or redundant answers.

### Outcome
An agent that can:
- Answer contextual queries about financial trends, leadership, and operational data
- Provide detailed insights into a company's current leadership team and potential impact

---

## Phase 3 – Peer Benchmarking & Competitor Monitoring

### 1. Peer Comparison Module
- **Purpose:** Analyze how a company compares against peers using key financial ratios and growth indicators.
- **Tech:**
  - Industry/sector classification using GICS/NAICS codes
  - Ratio normalization across companies (e.g., ROE, Current Ratio, Debt/Equity)

### 2. Competitor Flagging System
- **Purpose:** Detect when a peer company is significantly outperforming or underperforming based on key indicators.
- **Tech:**
  - Real-time comparison dashboard with API-sourced competitor data (Yahoo Finance, Edgar, Finnhub)
  - Threshold-based or relative performance scoring
  - Optional: alert system for underperformance warnings

### Limitations / Risks
1. **Industry classification ambiguity:** Multi-sector companies (e.g., Amazon = retail + cloud) may be hard to benchmark fairly.
2. **Missing comparable data:** Private companies or foreign entities may lack public filings or timely data.
3. **Metric misalignment:** Companies may report different KPIs (e.g., GMV, ARR, EBIT vs. EBITDA), making 1:1 comparison tricky.

### Outcome
A comparative analytics dashboard that:
- Benchmarks financials across peer companies
- Highlights strengths, weaknesses, and competitive threats
