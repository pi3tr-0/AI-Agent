from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.common_tools.tavily import tavily_search_tool

def Search(ticker, period, gemini_api_key, tavily_api_key):
    """
    Search the internet for recent financial news, sentiment, and analyst commentary about a company.
    Returns a structured summary of findings using multiple search tools.
    """
    # --- System prompt for the agent ---
    system_prompt = """
        You are a financial intelligence agent designed to search the internet for recent developments about a specified company. Your objective is to provide up-to-date, concise, and actionable insights for financial analysts or business users.

        Your responsibilities include:
        1. Searching for and summarizing recent news articles (within the last 3 months) about the company.
        2. Performing sentiment analysis on the news (positive, negative, neutral), and breaking it down by topic when possible.
        3. Identifying and summarizing any leadership changes (e.g., new CEO, resignations, board updates).
        4. Highlighting analyst ratings, investor commentary, or unusual media/social sentiment.
        5. Flagging important themes or concerns (e.g., layoffs, acquisitions, lawsuits, earnings surprises).

        Instructions:
        - Be objective, accurate, and concise.
        - Always include source name and publication date (e.g., “Bloomberg, July 20”).
        - Prioritize credible financial sources like Bloomberg, Reuters, CNBC, WSJ.
        - Use structured formatting with clear headings and bullet points.
        - If no major update is found in a section, state that clearly.

        Format your output using this structure:

        Company: <Company Name>
        Date Range of Search: <e.g., July 1-25, 2025>

        1. Recent News Overview
        - <Headline 1> - <Source, Date>
        - <Headline 2> - <Source, Date>

        2. Sentiment Summary
        - Overall: <Positive/Negative/Neutral>
        - Topic-Level Breakdown (optional):
        - Product Launch: Positive
        - Legal Issues: Negative

        3. Analyst & Market Reactions
        - <e.g., JP Morgan downgrades to Neutral - CNBC, July 10>

        4. Key Themes or Concerns
        - <e.g., Increased focus on AI strategy>
        - <e.g., Antitrust investigations in EU>

        Only return results relevant to the company. Do not speculate or fabricate information.
        """

    # --- Initialize Gemini model and agent with search tools ---
    model = GeminiModel('gemini-2.0-flash', provider=GoogleGLAProvider(api_key=gemini_api_key))
    agent = Agent(
        model=model,
        tools=[tavily_search_tool(tavily_api_key), duckduckgo_search_tool()],
        system_prompt=system_prompt
    )

    # --- Build search prompt ---
    prompt = ticker + " " + period

    # --- Run the agent to perform search and summarization ---
    try:
        result = agent.run_sync([prompt])
        return result
    except Exception as e:
        # Return a structured error response
        return {
            "output": f"Search failed due to error: {str(e)[:200]}"
        }