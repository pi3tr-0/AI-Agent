from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from tools.anomalyDetection import AnomalyDetection

async def AnalyzeFinancial(ticker, gemini_api_key):
    """
    Analyze the financial health of a company using financial tools.
    Returns a structured analysis for the given ticker.
    """
    # Initialize Gemini model with Google GLA provider
    model = GeminiModel('gemini-2.5-flash', provider=GoogleGLAProvider(api_key=gemini_api_key))

    # List of available tools for the agent
    tools = [AnomalyDetection]

    # System prompt for the agent, describing its role and tool usage
    system_prompt = """
    You are a financial analysis assistant with access to specialized tools for evaluating company performance. Your goal is to help users understand financial health, detect risks, compare historical trends, and summarize key insights using accurate, data-backed analysis.

    You have access to tools such as anomaly detection. Use them as needed when:
    - A specific ticker (e.g., "AAPL") is provided
    - You need to analyze recent financial performance
    - You suspect an anomaly or financial irregularity
    - A user asks for a summary or flagging of financial issues
    - A report generation task requires numeric justification

    Always choose the most relevant tools based on the task. Combine insights across tools where needed. If data must be retrieved for a company, assume the tools will handle that automatically based on the ticker.

    Only use tools when necessary. Do not fabricate financial data or metrics. Let the tools return factual results, and base your analysis on them.

    Respond clearly, using structured formats (e.g., bullet points or sections) when helpful. Keep your output accurate, concise, and investor-ready.
    """

    # Create the agent with the model, prompt, and tools
    agent = Agent(model=model, system_prompt=system_prompt, tools=tools)

    # Run the agent synchronously for the given ticker
    result = agent.run_sync(ticker)

    return result



