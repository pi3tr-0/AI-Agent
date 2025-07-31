from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import List, Literal
import json


async def AnalyzeSentiment(content, gemini_api_key):
    """
    Analyze market and analyst sentiment for a company using AI.
    Returns a structured sentiment analysis output.
    """
    # --- Data Models for Output Structure ---
    class SentimentTrend(BaseModel):
        theme: str = Field(..., description="The topic or theme under discussion")
        sentiment_trend: Literal["Increasing", "Decreasing", "Stable"] = Field(..., description="Direction of sentiment movement over time")
        source: str = Field(..., description="Source(s) where the trend was observed (e.g., 'News, Social Media')")

    class SentimentClassification(BaseModel):
        sentiment: Literal["Positive", "Neutral", "Negative"] = Field(..., description="Sentiment classification for this source")
        confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the sentiment (0.0 to 1.0)")
        supporting_quotes: List[str] = Field(..., description="Key phrases or quotes supporting the sentiment classification")
        source: str = Field(..., description="Source(s) where the trend was observed")

    class SentimentAnalysisOutput(BaseModel):
        company_name: str = Field(..., description="The name of the company being analyzed")
        overall_sentiment: Literal["Positive", "Neutral", "Negative"] = Field(..., description="Overall sentiment across all sources")
        confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score for the sentiment result (0.0 to 1.0)")
        analyst_sentiment: SentimentClassification = Field(..., description="Analyst sentiment/outlook for the company")
        market_sentiment: SentimentClassification = Field(..., description="Market sentiment/outlook for the company")
        key_themes: List[str] = Field(..., description="High-level topics or concerns that influenced sentiment")
        detected_trends: List[SentimentTrend] = Field(..., description="Sentiment direction trends around specific themes")

    # --- System Prompt for the Agent ---
    system_prompt = """
    You are a financial analysis assistant specialized in parsing and interpreting market and analyst sentiment about public companies from structured or unstructured data such as earnings call transcripts, analyst reports, news articles, and financial summaries.

    Your task is to:
    1. Identify and summarize the overall sentiment (positive, neutral, or negative) expressed toward the company.
    2. Highlight key phrases or statements that influence the sentiment.
    3. Extract and summarize analyst opinions such as buy/sell/hold ratings, price targets, and perceived strengths or concerns.
    4. Detect market sentiment trends by analyzing tone shifts, repeated themes, or changes in analyst outlook.
    5. Output your findings in a structured format with the following fields:
    - `company_name`: The name of the company.
    - `overall_sentiment`: Positive, Neutral, or Negative.
    - `analyst_summary`: A brief synthesis of analyst recommendations and key insights.
    - `market_reaction_summary`: A short paragraph capturing broader market tone and reaction.
    - `key_highlights`: A list of major points or quotes supporting the sentiment.

    You are accurate, concise, and avoid speculation. If the data is insufficient to determine sentiment, state that clearly.
    """

    # --- Initialize Gemini Model and Agent ---
    model = GeminiModel('gemini-2.5-flash', provider=GoogleGLAProvider(api_key=gemini_api_key))
    agent = Agent(model=model, system_prompt=system_prompt, output_type=SentimentAnalysisOutput)

    # --- Run Sentiment Analysis ---
    result = agent.run_sync([json.dumps(content)])

    return result