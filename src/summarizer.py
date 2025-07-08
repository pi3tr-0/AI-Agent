"""An Agent which takes a pdf file and summarizes it"""

from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

def SummarizeFile(pdf, api_key):
    model = GeminiModel('gemini-2.0-flash', provider=GoogleGLAProvider(api_key=api_key))
    agent = Agent(model=model)

    prompt = 'You are an AI agent that works on financial/analyst reports of companies. Summarize the file content uploaded to you, list out all the numerical data in the document, and provide the future outlook of the company based on the data'

    result = agent.run_sync(
    [
        prompt,
        BinaryContent(data=pdf.read(), media_type='application/pdf'),
    ]
    )
    return result