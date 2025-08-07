from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
import json
import asyncio


async def AnalyzeLeadership(ticker: str, period: str, gemini_api_key: str):
    """
    Analyze leadership changes and their impact on a company using AI and internet search.
    Returns a structured leadership analysis output.
    
    Args:
        ticker: Company ticker symbol (e.g., "AAPL")
        period: Analysis period (e.g., "Q3 2023")
        gemini_api_key: Google Gemini API key
    """
    
    # --- Data Models for Output Structure ---
    class LeadershipChange(BaseModel):
        change_type: Literal["appointment", "departure", "promotion", "restructuring", "compensation_change"] = Field(..., description="Type of leadership change")
        position: str = Field(..., description="Executive position or title")
        person_name: Optional[str] = Field(None, description="Name of the person involved (if available)")
        date: str = Field(..., description="Date or timeframe of the change")
        description: str = Field(..., description="Detailed description of the change")
        source: str = Field(..., description="Source of the information")

    class LeadershipTrend(BaseModel):
        trend: str = Field(..., description="Leadership trend or pattern observed")
        impact_level: Literal["High", "Medium", "Low"] = Field(..., description="Assessed impact level of the trend")
        trend_direction: Literal["Positive", "Negative", "Neutral"] = Field(..., description="Direction of the trend's impact")
        supporting_evidence: List[str] = Field(..., description="Evidence supporting this trend")

    class StabilityAssessment(BaseModel):
        stability_score: float = Field(..., ge=0.0, le=10.0, description="Leadership stability score from 0-10 (10 being most stable)")
        key_risks: List[str] = Field(..., description="Key leadership risks identified")
        strengths: List[str] = Field(..., description="Leadership strengths identified")
        succession_readiness: Literal["Strong", "Moderate", "Weak", "Unknown"] = Field(..., description="Assessment of succession planning")

    class LeadershipAnalysisOutput(BaseModel):
        company_ticker: str = Field(..., description="Company ticker symbol")
        company_name: str = Field(..., description="Company name")
        analysis_period: str = Field(..., description="Period analyzed")
        key_trends: List[LeadershipTrend] = Field(..., description="Key leadership trends and patterns")
        stability_assessment: StabilityAssessment = Field(..., description="Overall leadership stability assessment")
        overall_impact: Literal["Very Positive", "Positive", "Neutral", "Negative", "Very Negative"] = Field(..., description="Overall impact of leadership changes")
        investor_implications: str = Field(..., description="Summary of implications for investors")

    # --- Parse period to create search timeframe ---
    try:
        quarter, year = period.split()
        year = int(year)
        start_period = f"Q1 {year - 1}"
        date_range = f"{start_period} to {period}"
    except:
        date_range = f"past 18 months to {period}"

    # --- System Prompt for the Agent ---
    system_prompt = f"""
    You are a corporate leadership analysis expert. Your task is to search for and analyze leadership changes for {ticker} from {date_range}.

    Search comprehensively for:
    1. Executive appointments, departures, and promotions (CEO, CFO, CTO, COO, etc.)
    2. Board of directors changes
    3. Executive compensation decisions
    4. Organizational restructuring
    5. Succession planning announcements
    6. Leadership controversies or issues

    After gathering information, provide a thorough analysis including:
    - Impact assessment of each change
    - Leadership stability trends
    - Succession planning strength
    - Investor implications
    - Overall leadership health score

    Focus on factual, verifiable information from reliable sources. If information is limited, clearly state the constraints in your analysis.
    """

    # --- Initialize Gemini Model and Agent with Search Tool ---
    model = GeminiModel('gemini-2.5-flash', provider=GoogleGLAProvider(api_key=gemini_api_key))
    
    search_agent = Agent(
        model=model,
        tools=[duckduckgo_search_tool()],
        system_prompt=system_prompt,
        output_type=LeadershipAnalysisOutput
    )

    # --- Create comprehensive search query ---
    search_query = f"""
    Search and analyze leadership changes for {ticker} from {date_range}. Find information about:
    
    1. Executive changes: CEO, CFO, CTO, COO appointments, departures, promotions
    2. Board of directors changes: new appointments, departures, chairman changes
    3. Executive compensation: salary changes, bonus structures, stock awards
    4. Organizational restructuring: new roles, department changes, reporting structure
    5. Leadership controversies: resignations, investigations, performance issues
    6. Succession planning: announced plans, internal promotions, external hires
    
    For each finding, assess:
    - Market reaction and investor sentiment
    - Leadership stability implications
    - Strategic direction impact
    - Succession planning strength
    
    Provide a comprehensive analysis with leadership stability score (0-10) and investor implications.
    """

    # --- Run Leadership Analysis ---
    try:
        result = await search_agent.run(search_query)
        
        # Ensure the analysis period is correctly set
        if hasattr(result, 'output') and result.output:
            result.output.analysis_period = date_range
            result.output.company_ticker = ticker.upper()
        
        return result
        
    except Exception as e:
        # Create a simple error response that matches the expected structure
        error_response = LeadershipAnalysisOutput(
            company_ticker=ticker.upper(),
            company_name="Unknown",
            analysis_period=date_range,
            key_trends=[],
            stability_assessment=StabilityAssessment(
                stability_score=5.0,
                key_risks=[f"Analysis failed: {str(e)[:100]}"],
                strengths=[],
                succession_readiness="Unknown"
            ),
            overall_impact="Neutral",
            investor_implications=f"Unable to complete leadership analysis due to error: {str(e)[:200]}"
        )
        
        # Create a simple object that mimics the pydantic output
        class SimpleErrorResult:
            def __init__(self, data):
                self.output = data
        
        return SimpleErrorResult(error_response)


# --- Synchronous wrapper function ---
def AnalyzeLeadershipSync(ticker: str, period: str, gemini_api_key: str):
    """
    Synchronous wrapper for the async leadership analysis function.
    """
    return asyncio.run(AnalyzeLeadership(ticker, period, gemini_api_key))


# --- Main function for command-line usage ---
def main():
    """Main function for command-line usage."""
    import os
    import sys
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Get API key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print(json.dumps({"error": "GEMINI_API_KEY not found in .env"}))
        return
    
    # Get arguments
    if len(sys.argv) < 3:
        print("Usage: python3 leadershipAnalysis.py <TICKER> <PERIOD>")
        print("Example: python3 leadershipAnalysis.py AAPL 'Q3 2023'")
        return
    
    ticker = sys.argv[1]
    period = f"{sys.argv[2]} {sys.argv[3]}" if len(sys.argv) > 3 else sys.argv[2]
    
    # Execute analysis
    try:
        result = AnalyzeLeadershipSync(ticker, period, gemini_key)
        
        # Output JSON
        if hasattr(result, 'output'):
            output_dict = result.output.dict() if hasattr(result.output, 'dict') else result.output
            print(json.dumps(output_dict, indent=2, default=str))
        else:
            print(json.dumps({"error": "No output received from analysis"}, indent=2))
            
    except Exception as e:
        error_output = {
            "error": f"Leadership analysis failed: {str(e)}",
            "company_ticker": ticker.upper(),
            "analysis_period": period
        }
        print(json.dumps(error_output, indent=2))


if __name__ == "__main__":
    main()