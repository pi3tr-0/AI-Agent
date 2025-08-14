from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic import BaseModel, Field

def ParseFile(uploaded_file, gemini_api_key):
    """
    Parse a financial PDF document and extract structured data using a predefined schema.
    Returns a validated output object containing financial metrics, analyst summary, and metadata.
    """
    # Initialize Gemini model for document analysis
    model = GeminiModel('gemini-2.5-flash', provider=GoogleGLAProvider(api_key=gemini_api_key))

    # --- Data Models for Output Structure ---
    class Financial(BaseModel):
        ticker: str = Field(description="An abbreviation used to uniquely identify publicly traded shares of a particular stock")
        year: int = Field(description="The year the report is generated")
        quarter: int = Field(default=None, description="The quarter the report is generated. Do not fill this value if it's a yearly report")
        totalrevenue: int = Field(default=None, description="Total income generated from a company's primary business activities before expenses; also known as revenue, total sales, gross revenue, net sales, turnover (UK), or sales revenue; usually found at the top of the income statement, often labeled 'Total Revenue', 'Revenue', or 'Sales', and expressed in thousands, millions, or billions depending on company size.")
        revenuegrowth: float = Field(default=None, description="The percentage increase or decrease in total revenue over a specific period (e.g., year-over-year or quarter-over-quarter); also referred to as revenue increase, sales growth, top-line growth, YoY revenue change, or revenue CAGR; typically found in management discussions, highlights, or charts labeled 'Revenue Growth', often expressed as a % with or without +/- sign.")
        ebitda: int = Field(default=None, description="Earnings Before Interest, Taxes, Depreciation, and Amortization; a measure of a company's core operational profitability excluding non-operating expenses and non-cash charges; also referred to as operating cash flow (informally), core earnings, or adjusted earnings; commonly found in financial highlights, income statement footnotes, or non-GAAP reconciliation sections, and often labeled 'EBITDA', 'Adjusted EBITDA', or 'EBITDA (non-GAAP)'.")
        ebitdamargins: float = Field(default=None, description="The percentage of EBITDA relative to total revenue, indicating operational profitability efficiency; also known as EBITDA to revenue ratio, EBITDA %, or operating margin (when loosely used); typically found in summary tables, investor presentations, or performance metrics, and expressed as a percentage")
        netincome: int = Field(default=None, description="The total profit a company earns after deducting all expenses, taxes, interest, and costs from total revenue; also known as net profit, net earnings, or bottom line; typically found at the bottom of the income statement and often labeled 'Net Income', 'Net Profit', 'Net Earnings', or 'Net Income Attributable to Shareholders'.")
        profitmargin: float = Field(default=None, description="The percentage of net income relative to total revenue, measuring overall profitability after all expenses; also known as net profit margin, net margin, or return on revenue; typically found in financial ratios, highlights, or summary sections labeled as 'Profit Margin', 'Net Margin', or 'Net Income Margin', and expressed as a percentage")
        operatingmargin: float = Field(default=None, description="The percentage of operating income relative to total revenue, reflecting the efficiency of a company's core operations; also called operating profit margin, EBIT margin, or return on sales (ROS); commonly shown as 'Operating Margin', 'Operating Profit %', or 'EBIT Margin' in summary tables, financial highlights, or investor presentations, and expressed as a percentage")
        basiceps: float = Field(default=None, description="Earnings Per Share (EPS) calculated using net income from the most recent 12 months (trailing twelve months or TTM); also called TTM EPS, last twelve months EPS, or trailing twelve months earnings per share; commonly found in earnings reports, financial summaries, or stock analysis sections, often labeled 'Trailing EPS', 'EPS (TTM)', or 'Last 12 Months EPS'")
        sharesoutstanding: int = Field(default=None, description="The total number of a company's common shares currently held by all shareholders, including institutional investors and insiders, but excluding treasury shares; also referred to as outstanding shares, common shares outstanding, or issued and outstanding shares; typically found in the equity section of the balance sheet, notes to financial statements, or in per-share calculations like EPS, often labeled 'Shares Outstanding' or 'Weighted Average Shares Outstanding'")
        dividendrate: float = Field(default=None, description="The amount of dividend paid per share over a specific period, usually annually or quarterly; also known as dividend per share, DPS, cash dividend rate, or declared dividend; typically found in dividend declarations, financial summaries, or shareholder communications, often labeled 'Dividend Rate', 'Dividend Per Share', or 'Annual Dividend'")
        dividendyield: float = Field(default=None, description="The ratio of a company's annual dividend per share to its current stock price, expressed as a percentage; also known as dividend rate yield or dividend payout yield; used by investors to assess income return on investment, typically found in financial summaries, stock analysis, or investor relations sections labeled 'Dividend Yield', 'Yield %', or 'Dividend Return'")

    class Analyst(BaseModel):
        summary: str = Field(description="A synthesized summary reflecting the analyst's interpretation of the company's performance, outlook, and strategic direction. Includes key takeaways, valuation commentary, sentiment (bullish/bearish/neutral), and notable catalysts or risks identified by the analyst. It should include 'priceTarget' (expected future stock price) and 'upside' (percentage change from current price to target).")
        priceTarget: str = Field(description="The analyst's estimated future share price, based on valuation models or market outlook.")
        upside: str = Field(description="The percentage gain or loss implied by the price target relative to the current share price; calculated as (priceTarget - currentPrice) / currentPrice.")
        sentiment: str = Field(description="A qualitative label of the analyst's tone or stance, e.g., 'Bullish', 'Neutral', 'Bearish'.")
        catalysts: str = Field(default=None, description="Upcoming events or trends that could significantly impact the stock, such as product launches, earnings, regulatory approvals, etc.")
        risks: str = Field(default=None, description="Key downside risks or uncertainties flagged by the analyst, such as market volatility, competitive pressure, or regulatory headwinds.")

    class Output(BaseModel):
        financialMetrics: Financial
        pdfSummary: str = Field(description="A concise, factual summary of the source document's key contents, focusing on the financial data, performance highlights, and narrative points provided by the company or reporting body. This includes earnings results, revenue performance, business updates, segment-level insights, and any major changes disclosed in the document. Should reflect the tone and content of the report without adding interpretation or opinion.")
        analyst: Analyst
        ticker: str = Field(description="An abbreviation used to uniquely identify publicly traded shares of a particular stock")
        period: str = Field(description="the quarter and year at which the report is produced, e.g. Q2 2025")

    # --- System Prompt for the Agent ---
    system_prompt = """
    You are an information extraction system that processes financial PDF documents (e.g., annual reports, filings) and outputs structured data using a predefined schema. You must extract only factual data that is explicitly present in the text and return it in the specified format.

    1. Financial metrics: Include only those fields explicitly present in the source text
    2. Do NOT fabricate or infer any values — only include data that is directly present in the source.
      - If a value is not explicitly stated in the document, **do not guess, estimate, or derive it**
      - Do not perform calculations (e.g., computing margin from revenue and profit)
      - If a field is missing or ambiguous, omit it from the output
    3. Output must be a single valid JSON object and nothing else — no extra text, commentary, or formatting.
    4. All percentage values should be expressed as **decimals** (e.g., 0.12 for 12%).
    5. All monetary values must be expressed as integers, without currency symbols or formatting (e.g., 10500000).

    ### IMPORTANT:
    - ALWAYS include ticker and year
    - Adhere strictly to this schema
    - Do not guess
    """

    # --- Run the agent to extract structured data from PDF ---
    agent = Agent(model=model, system_prompt=system_prompt, output_type=Output)
    result = agent.run_sync([BinaryContent(data=uploaded_file, media_type='application/pdf')])
    return result