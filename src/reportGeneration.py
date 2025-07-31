from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

def GenerateReport(sentiment, financial, api_key):
    """
    Generate a financial report
    """

    # Initialize Gemini model for summarization
    model = GeminiModel('gemini-2.0-flash', provider=GoogleGLAProvider(api_key=api_key))

    system_prompt = """"
    You are an AI agent that works on financial reports. Your task is to generate a comprehensive financial report based on the provided sentiment analysis and financial data.
    Summarize the key findings, highlight important trends, and provide actionable insights for investors.
    Ensure the report is structured, clear, and concise.
    """

    agent = Agent(model=model, system_prompt=system_prompt)

    # Run the agent with the prompt and PDF file
    result = agent.run_sync([
        sentiment,
        financial
    ])
    return result