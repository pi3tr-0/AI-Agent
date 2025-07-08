"""An Agent which takes a pdf file and read from the table"""

"""
1. Receive a pdf
2. Read from the table
3. Select what is needed
4. Populate the data with the structure: {}
5. Push to database
"""

from pydantic_ai import Agent, BinaryContent
from pydantic import BaseModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

def ParseFile(pdf, api_key):
    model = GeminiModel('gemini-2.0-flash', provider=GoogleGLAProvider(api_key=api_key))
    
    class Output(BaseModel):
        totalRevenue: int
        revenueGrowth: float
        ebitda: int
        ebitdaMargins: float
        operatingIncome: int
        operatingMargin: float
        netIncomeToCommon: int
        profitMargins: float
        sharesOutstanding: int
        trailingEps: float
        dividenRate: float
        priceToSales: float
        trailingPE: float
        priceCashFlow: float
        dividendYield: float
        priceToBook: float
        enterpriseToEbitda: float
        returnOnAssets: float
        returnOnEquity: float
    
    agent = Agent(model=model, output_type=Output)

    prompt = 'You are a pdf-parser AI agent that read data from financial documents, structure your output in JSON format and if the value is not in the document do not include in output'


    result = agent.run_sync(
    [
        prompt,
        BinaryContent(data=pdf.read(), media_type='application/pdf'),
    ]
    )
    return result