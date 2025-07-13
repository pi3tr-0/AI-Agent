"""An Agent which takes a pdf file and read from the table"""

"""
1. Receive a pdf
2. Read from the table
3. Select what is needed
4. Populate the data with the structure: {}
5. Push to database
"""

from pydantic_ai import Agent, BinaryContent
from pydantic import BaseModel, Field
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

def ParseFile(uploaded_file, api_key):
    model = GeminiModel('gemini-2.0-flash', provider=GoogleGLAProvider(api_key=api_key))
    
    class Output(BaseModel):
        ticker: str = Field(description='An abbreviation used to uniquely identify publicly traded shares of a particular stock')
        year: int = Field(description='')
        totalRevenue: int = Field(description='')
        revenueGrowth: float = Field(description='')
        ebitda: int = Field(description='')
        ebitdaMargins: float = Field(description='')
        operatingIncome: int = Field(description='')
        operatingMargin: float = Field(description='')
        netIncomeToCommon: int = Field(description='')
        profitMargins: float = Field(description='')
        sharesOutstanding: int = Field(description='')
        trailingEps: float = Field(description='')
        dividendRate: float = Field(description='')
        priceToSales: float = Field(description='')
        trailingPE: float = Field(description='')
        priceCashFlow: float = Field(description='')
        dividendYield: float = Field(description='')
        priceToBook: float = Field(description='')
        enterpriseToEbitda: float = Field(description='')
        returnOnAssets: float = Field(description='')
        returnOnEquity: float = Field(description='')
        includedData: list = Field(description='')
    
    agent = Agent(model=model, output_type=Output)

    prompt = """You are a pdf-parser AI agent that read data from financial documents and 
    structure your output in JSON format. Make sure to always include the ticker and year.
    The output are always about the company as a whole and not for its segments, if any.
    EVERY TIME you have found a data which you include in the output, append the key into
    the includedData"""

    result = agent.run_sync(
    [
        prompt,
        BinaryContent(data=uploaded_file, media_type='application/pdf'),
    ]
    )
    return result