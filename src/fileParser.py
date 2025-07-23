from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic import BaseModel, Field

def ParseFile(uploaded_file, api_key):
    model = GeminiModel('gemini-2.5-flash', provider=GoogleGLAProvider(api_key=api_key))

    class Output(BaseModel):
        ticker: str = Field(description="An abbreviation used to uniquely identify publicly traded shares of a particular stock")
        year: int = Field(description="The year the report is generated")
        quarter: int = Field(default=None, description="The quarter the report is generated. Do not fill this value if it's a yearly report")
        totalrevenue: int = Field(default=None, description="Total income generated from a company's primary business activities before expenses; also known as revenue, total sales, gross revenue, net sales, turnover (UK), or sales revenue; usually found at the top of the income statement, often labeled 'Total Revenue', 'Revenue', or 'Sales', and expressed in thousands, millions, or billions depending on company size.")
        revenuegrowth: float = Field(default=None, description="The percentage increase or decrease in total revenue over a specific period (e.g., year-over-year or quarter-over-quarter); also referred to as revenue increase, sales growth, top-line growth, YoY revenue change, or revenue CAGR; typically found in management discussions, highlights, or charts labeled 'Revenue Growth', often expressed as a % with or without +/- sign.")
        ebitda: int = Field(default=None, description="Earnings Before Interest, Taxes, Depreciation, and Amortization; a measure of a company's core operational profitability excluding non-operating expenses and non-cash charges; also referred to as operating cash flow (informally), core earnings, or adjusted earnings; commonly found in financial highlights, income statement footnotes, or non-GAAP reconciliation sections, and often labeled 'EBITDA', 'Adjusted EBITDA', or 'EBITDA (non-GAAP)'.")
        ebitdamargins: float = Field(default=None, description="The percentage of EBITDA relative to total revenue, indicating operational profitability efficiency; also known as EBITDA to revenue ratio, EBITDA %, or operating margin (when loosely used); typically found in summary tables, investor presentations, or performance metrics, and expressed as a percentage")
        operatingincome: int = Field(default=None, description="Profit earned from a company's core business operations before interest and taxes; also known as operating profit, operating earnings, or EBIT (when depreciation and amortization are not separated); typically found in the income statement under 'Operating Income' or 'Income from Operations', and represents revenue minus operating expenses including COGS and SG&A")
        operatingmargin: float = Field(default=None, description="The percentage of operating income relative to total revenue, reflecting the efficiency of a company's core operations; also called operating profit margin, EBIT margin, or return on sales (ROS); commonly shown as 'Operating Margin', 'Operating Profit %', or 'EBIT Margin' in summary tables, financial highlights, or investor presentations, and expressed as a percentage")
        netincometocommon: int = Field(default=None, description="The portion of net income attributable to common shareholders after preferred dividends are deducted; also referred to as net earnings available to common shareholders, profit attributable to common stock, or net income applicable to common shares; typically found near the bottom of the income statement or in earnings per share (EPS) calculations, often labeled 'Net Income to Common', 'Net Income Attributable to Common Shareholders', or similar")
        profitmargins: float = Field(default=None, description="The percentage of net income relative to total revenue, measuring overall profitability after all expenses; also known as net profit margin, net margin, or return on revenue; typically found in financial ratios, highlights, or summary sections labeled as 'Profit Margin', 'Net Margin', or 'Net Income Margin', and expressed as a percentage")
        sharesoutstanding: int = Field(default=None, description="The total number of a company's common shares currently held by all shareholders, including institutional investors and insiders, but excluding treasury shares; also referred to as outstanding shares, common shares outstanding, or issued and outstanding shares; typically found in the equity section of the balance sheet, notes to financial statements, or in per-share calculations like EPS, often labeled 'Shares Outstanding' or 'Weighted Average Shares Outstanding'")
        trailingeps: float = Field(default=None, description="Earnings Per Share (EPS) calculated using net income from the most recent 12 months (trailing twelve months or TTM); also called TTM EPS, last twelve months EPS, or trailing twelve months earnings per share; commonly found in earnings reports, financial summaries, or stock analysis sections, often labeled 'Trailing EPS', 'EPS (TTM)', or 'Last 12 Months EPS'")
        dividendrate: float = Field(default=None, description="The amount of dividend paid per share over a specific period, usually annually or quarterly; also known as dividend per share, DPS, cash dividend rate, or declared dividend; typically found in dividend declarations, financial summaries, or shareholder communications, often labeled 'Dividend Rate', 'Dividend Per Share', or 'Annual Dividend'")
        pricetosales: float = Field(default=None, description="A valuation ratio comparing a company's stock price to its revenue per share; also called P/S ratio, price/revenue ratio, or sales multiple; commonly used to assess how much investors pay for each dollar of sales, typically found in financial metrics, stock analysis reports, or valuation sections labeled 'Price to Sales', 'P/S Ratio', or 'Price/Sales'.")
        trailingpe: float = Field(default=None, description="The Price-to-Earnings ratio calculated using net income from the past 12 months (trailing twelve months); also known as trailing price-earnings ratio, PE (TTM), or last twelve months PE; commonly found in stock valuation metrics, earnings reports, or investment analyses, often labeled 'Trailing P/E', 'P/E (TTM)', or 'TTM Price-to-Earnings'")
        pricecashflow: float = Field(default=None, description="A valuation metric comparing a company's current share price to its cash flow per share; also known as P/CF ratio or price-to-operating cash flow; used to evaluate stock value relative to cash generated by operations, typically found in financial summaries, valuation reports, or investment analyses labeled 'Price to Cash Flow', 'P/CF Ratio', or 'Price/Cash Flow'")
        dividendyield: float = Field(default=None, description="The ratio of a company's annual dividend per share to its current stock price, expressed as a percentage; also known as dividend rate yield or dividend payout yield; used by investors to assess income return on investment, typically found in financial summaries, stock analysis, or investor relations sections labeled 'Dividend Yield', 'Yield %', or 'Dividend Return'")
        pricetobook: float = Field(default=None, description="A financial ratio comparing a company's market price per share to its book value per share; also called P/B ratio or price-to-equity ratio; used to evaluate if a stock is undervalued or overvalued relative to net asset value, commonly found in valuation metrics, financial analysis, or investment reports labeled 'Price to Book', 'P/B Ratio', or 'Price/Book Value'")
        enterprisetoebitda: float = Field(default=None, description="A valuation multiple comparing a company's enterprise value (market capitalization plus debt minus cash) to its EBITDA; also known as EV/EBITDA ratio or enterprise value to earnings before interest, taxes, depreciation, and amortization; used to assess company value relative to operating cash flow, commonly found in financial analysis, valuation reports, or investment summaries labeled 'EV/EBITDA', 'Enterprise Value to EBITDA', or 'Enterprise Multiple'")
        returnonassets: float = Field(default=None, description="A profitability ratio measuring net income generated per dollar of total assets, indicating how efficiently a company uses its assets to produce profit; also called ROA or return on total assets; typically found in financial ratios, performance metrics, or investor reports labeled 'Return on Assets', 'ROA', or 'Return on Total Assets', expressed as a percentage")
        returnonequity: float = Field(default=None, description="A financial metric measuring net income generated per dollar of shareholders' equity, reflecting how effectively a company uses invested capital to generate profits; also known as ROE; commonly found in financial ratios, investor reports, or performance summaries labeled 'Return on Equity', 'ROE', or 'Return on Shareholders' Equity', expressed as a percentage.")
  
    system_prompt = """You are an information extraction system that processes financial PDF documents (e.g., annual reports, filings) and outputs structured data using a predefined schema. You must extract only factual data that is explicitly present in the text and return it in the specified format.

                        ### Your rules:

                        1. Use the following JSON schema structure for your output:
                          - `ticker`: string (e.g., "AAPL")
                          - `year`: integer (e.g., 2023)
                          - Financial metrics: Include only those fields explicitly present in the source text

                        2. Do NOT fabricate or infer any values — only include data that is directly present in the source.
                          - If a value is not explicitly stated in the document, **do not guess, estimate, or derive it**
                          - Do not perform calculations (e.g., computing margin from revenue and profit)
                          - If a field is missing or ambiguous, omit it from the output

                        3. Output must be a single valid JSON object and nothing else — no extra text, commentary, or formatting.
                        4. All percentage values should be expressed as **decimals** (e.g., 0.12 for 12%).
                        5. All monetary values must be expressed as integers, without currency symbols or formatting (e.g., 10500000).

                        ### Example (only partial data found):

                        {
                          "ticker": "AAPL",
                          "year": 2023,
                          "totalRevenue": 394328000000,
                          "netIncomeToCommon": 99803000000,
                        }

                        If nothing is found:

                        {
                          "ticker": "AAPL",
                          "year": 2023,
                        }

                        ### IMPORTANT:
                        - ALWAYS include ticker and year
                        - Adhere strictly to this schema
                        - Do not guess

                        """
    
    agent = Agent(model=model, system_prompt=system_prompt, output_type=Output)
    
    result = agent.run_sync([BinaryContent(data=uploaded_file, media_type='application/pdf')])
    
    return result