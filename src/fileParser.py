"""An Agent which takes a pdf file and read from the table"""

"""
1. Receive a pdf
2. Read from the table
3. Select what is needed
4. Populate the data with the structure: {}
5. Push to database
"""

from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

def parseFile(pdf):
    model = GeminiModel('gemini-2.0-flash', provider=GoogleGLAProvider(api_key='AIzaSyCzt-xIo7eJjQ-ryQprOOwv9zkF0tmVR68'))
    agent = Agent(model=model)
    result = agent.run_sync(
    [
        'What is the main content of this document?',
        BinaryContent(data=pdf.read(), media_type='application/pdf'),
    ]
    )
    return result
