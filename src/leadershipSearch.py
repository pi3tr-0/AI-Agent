import json
import os
import re
from typing import Dict
from dotenv import load_dotenv
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai import Agent
import asyncio  

"""
LeadershipSearch.py - Search leadership changes for a specific quarter range
"""

example_output = """{
  "company": "AAPL",
  "date_range": "Q1 2022 to Q3 2023",
  "leadership_updates": [
    {
      "title": "Tim Cook's 2022 Total Compensation Revealed",
      "source": "MarketScreener",
      "date": "January 12, 2023",
      "category": "compensation",
      "details": "Apple CEO Tim Cook's total compensation for 2022 was $99.42 million."
    },
    {
      "title": "Apple CEO Tim Cook's 2023 Pay Cut by Over 40%",
      "source": "BBC News, Strait Times",
      "date": "January 13, 2023",
      "category": "compensation",
      "details": "Apple cut CEO Tim Cook's compensation by over 40% to $49 million in 2023. This decision was made based on investor guidance and Cook's own request, following shareholder feedback."
    },
    {
      "title": "Unprecedented Wave of Executive Departures",
      "source": "MacDailyNews",
      "date": "March 13, 2023",
      "category": "executive_changes",
      "details": "Apple experienced an 'unprecedented wave' of approximately a dozen high-ranking executive departures, primarily vice presidents, starting in the second half of 2022 and continuing into early 2023."
    }
  ]
}"""

async def LeadershipSearch(ticker: str, period: str, gemini_api_key: str) -> Dict:
    """
    Search for leadership changes from Q1 of previous year to specified period.
    
    Args:
        ticker: Company ticker symbol (e.g., "AAPL")
        period: Target period (e.g., "Q3 2023")
        gemini_api_key: Google Gemini API key
        
    Returns:
        JSON with leadership events from Q1 (year-1) to specified period
    """
    # Parse period
    [quarter, year] = period.split()
    year = int(year)
    
    # Define date range
    start_period = f"Q1 {year - 1}"
    end_period = period
    date_range = f"{start_period} to {end_period}"
    
    # Use stable model with good rate limits
    model = GeminiModel(
        "gemini-2.5-flash",
        provider=GoogleGLAProvider(api_key=gemini_api_key)
    )
    
    # Single comprehensive search query
    search_query = f"""
    {ticker} leadership changes from {start_period} through {end_period}:
    - CEO CFO CTO COO executive appointments resignations departures
    - Board of directors chairman changes
    - Executive compensation decisions
    - Management restructuring succession planning
    """
    
    # Single agent for search and structure
    agent = Agent(
        model=model,
        tools=[duckduckgo_search_tool()],
        system_prompt=f"""Search for {ticker} leadership changes from {start_period} to {end_period}.

TASK:
1. Search comprehensively for ALL leadership events in this period
2. Extract and structure findings chronologically

SEARCH FOCUS:
- C-Suite changes (CEO, CFO, CTO, COO, CMO, etc.)
- Board member appointments/departures
- Executive compensation updates
- Leadership restructuring
- Succession planning

DATE RANGE: You MUST find events from {start_period} through {end_period}
This covers approximately 15-21 months of leadership activity.

OUTPUT FORMAT - Return ONLY this JSON:
{{
    "company": "{ticker}",
    "date_range": "{date_range}",
    "leadership_updates": [
        {{
            "title": "Event headline",
            "source": "Publication name",
            "date": "Specific date or quarter",
            "category": "executive_changes|board_changes|compensation|restructuring",
            "details": "Full description of what happened"
        }}
    ]
}}

IMPORTANT:
- Include ALL events from {start_period} to {end_period}
- Sort events chronologically
- Only include verified events with sources
- If no events found, return empty leadership_updates array"""
    )
    
    try:
        # Execute search directly without asyncio.to_thread
        result = agent.run_sync(search_query)
        
        # Parse JSON response
        if result.output:
            json_match = re.search(r'\{[\s\S]*\}', result.output)
            if json_match:
                data = json.loads(json_match.group())
                # Ensure date_range is set correctly
                data["date_range"] = date_range
                return data
        
        # Fallback if no valid JSON
        return {
            "company": ticker,
            "date_range": date_range,
            "leadership_updates": []
        }
        
    except Exception as e:
        # Handle errors gracefully
        return {
            "company": ticker,
            "date_range": date_range,
            "leadership_updates": []
        }


def main():
    """Main function for command-line usage."""
    load_dotenv()
    
    # Get API key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print(json.dumps({"error": "GEMINI_API_KEY not found in .env"}))
        return
    
    # Get arguments
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 leadershipSearch.py <TICKER> <PERIOD>")
        print("Example: python3 leadershipSearch.py AAPL Q3 2023")
        return
    
    ticker = sys.argv[1]
    period = f"{sys.argv[2]} {sys.argv[3]}" if len(sys.argv) > 3 else sys.argv[2]
    
    # Execute search
    result = LeadershipSearch(ticker, period, gemini_key)
    
    # Output JSON
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()