from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from src.tools.anomalyDetection import AnomalyDetection



async def AnalyzeFinancial(ticker, period, gemini_api_key):
    """
    Analyze the financial health of a company using financial tools.
    Returns a structured financial analysis output.
    """
    
    # --- Data Models for Output Structure ---
    class FinancialMetric(BaseModel):
        metric_name: str = Field(..., description="Name of the financial metric")
        simple_average_assessment: str = Field(..., description="Assessment compared to historical averages")
        trend_analysis_assessment: str = Field(..., description="Assessment based on trend analysis")
        overall_trend: Literal["Improving", "Declining", "Stable", "Unknown"] = Field(..., description="Overall trend direction based on both analyses")
        significance: Literal["High", "Medium", "Low"] = Field(..., description="Significance of this metric")
        key_insights: str = Field(..., description="Key insights about this metric's performance")

    class RiskAssessment(BaseModel):
        risk_level: Literal["Low", "Medium", "High", "Critical"] = Field(..., description="Overall financial risk level")
        key_risks: List[str] = Field(..., description="List of identified financial risks")
        risk_factors: List[str] = Field(..., description="Specific factors contributing to risk")
        mitigation_suggestions: List[str] = Field(..., description="Suggested risk mitigation strategies")

    class FinancialHealthScore(BaseModel):
        overall_score: float = Field(..., ge=0.0, le=10.0, description="Overall financial health score (0-10)")
        liquidity_score: float = Field(..., ge=0.0, le=10.0, description="Liquidity health score (0-10)")
        profitability_score: float = Field(..., ge=0.0, le=10.0, description="Profitability health score (0-10)")
        efficiency_score: float = Field(..., ge=0.0, le=10.0, description="Operational efficiency score (0-10)")
        growth_score: float = Field(..., ge=0.0, le=10.0, description="Growth potential score (0-10)")

    class FinancialAnalysisOutput(BaseModel):
        company_ticker: str = Field(..., description="Company ticker symbol")
        company_name: str = Field(..., description="Company name")
        analysis_period: str = Field(..., description="Period analyzed")
        financial_health_score: FinancialHealthScore = Field(..., description="Comprehensive financial health scoring")
        key_metrics: List[FinancialMetric] = Field(..., description="Key financial metrics and trends")
        risk_assessment: RiskAssessment = Field(..., description="Financial risk evaluation")
        performance_summary: str = Field(..., description="Overall performance summary")
        investment_outlook: Literal["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"] = Field(..., description="Investment recommendation")
        analyst_notes: List[str] = Field(..., description="Key analytical insights and observations")

    # --- System Prompt for the Agent ---
    system_prompt = f"""
    You are a financial analysis assistant with access to specialized tools for evaluating company performance. Your goal is to provide comprehensive financial health analysis for {ticker} during {period}.

    You have access to the anomaly detection tool. IMPORTANT: When using the anomaly detection tool, you MUST provide both the ticker symbol and the period in the format 'Q<1-4> YYYY' (e.g., 'Q3 2024').

    Use the anomaly detection tool when:
    - You need to analyze financial performance for {ticker} for period {period}
    - You want to detect financial anomalies or irregularities
    - You need to compare current performance to historical trends

    ALWAYS call the anomaly detection tool with both parameters: ticker="{ticker}" and period="{period}"

    The anomaly detection tool returns analysis results with two main sections:
    1. "simpleAverages" - compares current metrics to historical averages
    2. "linearRegression" - uses trend analysis to predict expected vs actual performance

    When analyzing the tool results:
    - "Higher than expected" indicates positive performance
    - "Lower than expected" indicates concerning performance  
    - "Changes within the tolerable range" indicates stable performance
    - "No Historical Data" means insufficient data for comparison

    IMPORTANT: Use the tool results to populate the FinancialMetric fields:
    - simple_average_assessment: Use the value from "simpleAverages" section
    - trend_analysis_assessment: Use the value from "linearRegression" section  
    - overall_trend: Determine based on both assessments
    - significance: Assess based on the metric's importance and deviation
    - key_insights: Provide analysis of what the results mean

    Your analysis should include:
    1. Financial health scoring based on the anomaly detection results
    2. Key financial metrics with trend analysis from the tool output
    3. Risk assessment based on detected anomalies
    4. Performance summary and investment outlook
    5. Analytical insights based on the tool results

    Only use tools when necessary. Do not fabricate financial data or metrics. Base your analysis entirely on tool results and established financial analysis principles.

    Provide accurate, data-driven analysis suitable for investment decision-making.
    """

    # --- Initialize Gemini Model and Agent ---
    model = GeminiModel('gemini-2.5-flash', provider=GoogleGLAProvider(api_key=gemini_api_key))
    agent = Agent(
        model=model, 
        system_prompt=system_prompt, 
        tools=[AnomalyDetection],
        output_type=FinancialAnalysisOutput
    )

    # --- Run Financial Analysis ---
    try:
        prompt = f"Analyze financial data for {ticker} for period {period}"
        result = agent.run_sync(prompt)
        
        # Ensure the analysis period and ticker are correctly set
        if hasattr(result, 'output') and result.output:
            result.output.analysis_period = period
            result.output.company_ticker = ticker.upper()
        
        return result
        
    except Exception as e:
        # Create a simple error response that matches the expected structure
        error_response = FinancialAnalysisOutput(
            company_ticker=ticker.upper(),
            company_name="Unknown",
            analysis_period=period,
            financial_health_score=FinancialHealthScore(
                overall_score=5.0,
                liquidity_score=5.0,
                profitability_score=5.0,
                efficiency_score=5.0,
                growth_score=5.0
            ),
            key_metrics=[],
            risk_assessment=RiskAssessment(
                risk_level="Medium",
                key_risks=[f"Analysis failed: {str(e)[:100]}"],
                risk_factors=[],
                mitigation_suggestions=[]
            ),
            performance_summary=f"Unable to complete financial analysis due to error: {str(e)[:200]}",
            investment_outlook="Hold",
            analyst_notes=[f"Error occurred during analysis: {str(e)[:150]}"]
        )
        
        # Create a simple object that mimics the pydantic output
        class SimpleErrorResult:
            def __init__(self, data):
                self.output = data
        
        return SimpleErrorResult(error_response)