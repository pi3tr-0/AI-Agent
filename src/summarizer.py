"""
Summarizer Agent: Takes a PDF file and returns a summary, all numerical data, and future outlook for the company.
"""

# --- Imports for AI agent and model ---
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

def SummarizeFile(uploaded_file, api_key):
    """
    Summarize a financial/analyst PDF report, extract all numerical data, and provide future outlook.
    Returns a summary string or structured output from the agent.
    """
    # Initialize Gemini model for summarization
    model = GeminiModel('gemini-2.0-flash', provider=GoogleGLAProvider(api_key=api_key))
    agent = Agent(model=model)

    # Prompt for summarization and extraction
    prompt = (
        "You are an AI agent that works on financial/analyst reports of companies. "
        "Summarize the file content uploaded to you, list out all the numerical data in the document, "
        "and provide the future outlook of the company based on the data."
    )

    # Run the agent with the prompt and PDF file
    result = agent.run_sync([
        prompt,
        BinaryContent(uploaded_file, media_type='application/pdf'),
    ])
    return result