from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # load from .env

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load reusable instructions from prompt.txt (optional if using saved prompt)
with open("prompt.txt", "r", encoding="utf-8") as f:
    instructions = f.read()

# User input (real-world financial report summary)
user_financial_summary = """
Revenue is up 8%, net profit margin is stable at 10%, debt-to-equity is 0.6, and cash reserves grew 20% from last quarter.
"""

# Create response using the Responses API
response = client.responses.create(
    model="gpt-4.1",
    instructions=instructions,
    input=user_financial_summary
)

# Output result
print("\n📊 Financial Review Result:")
print(response.output_text)