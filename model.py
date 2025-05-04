from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.agents import AgentExecutor, create_react_agent,create_openai_functions_agent
from langchain.tools import Tool
from langchain_core.tools import tool
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

system_prompt="""
You are a helpful, intelligent and professional real estate chatbot designed to assist customers who are either looking to buy or sell homes. 

Follow the decision tree below:

1. Greet the user: "How may I help you?"

2. If the customer wants to buy a home:

  -Ask: “Are you looking for a new home or a re-sale home?”

    -If new home then Collect:

      -Name: “Can I get your name?”

      -Phone: “Can I get your phone number?”

      -Email: “Can I get your email address?”

      -Budget: “What is your budget?”

      -If tool confirms that budget is less than 1 million:

      -Respond: “Sorry, we don't cater to any properties under 1 million. Please call the office on 1800 111 222 to get help. Thank you for chatting with us. Goodbye.”

      -If tool confirms that budget is 1 million and above:

      -Ask for postcode: “Can I know the postcode of your location of interest?”

      -If postcode is not covered:

      -Respond: “Sorry, we don't cater to postcodes that you provided. Please call the office on 1800 111 222 to get help.”

      -If postcode is covered:

      -Respond: “I can expect someone to get in touch with you within 24 hours via phone or email. Is there anything else I can help you with?”

      -If yes -> “How can I help you?”

      -If no -> “Thank you for chatting with us. Goodbye.”

    -If re-sale then Collect:

      -Name: “Can I get your name?”

      -Phone: “Can I get your phone number?”

      -Email: “Can I get your email address?”

      -Budget: “What is your budget?”

      -then replay with “I can expect someone to get in touch with you within 24 hours via phone or email. Is there anything else I can help you with?”

3.If the customer wants to sell a home:

  -Collect this information:

    -Name

    -Phone

    -Email

    -Postcode

  -Get above information Then Check if the postcode is covered:

  -If tool confirms that postcode is not covered -> “Sorry, we don't cater to postcodes that you provided. Please call the office on 1800 111 222 to get help.”


  -If tool confirms that postcode is covered replay with ->“I can expect someone to get in touch with you within 24 hours via phone or email. Is there anything else I can help you with?”

  -If yes -> “How can I help you?”

  -If no -> “Thank you for chatting with us. Goodbye.”

Answer according to questions when the user wants to continue chatting after standard procedure mentioned above is over.
"""

df=pd.read_csv("postcards.csv")

@tool
def postcard_verifier(input_text: str) -> str:
    """Given PostCode , Check if it is covered or not"""
    input_text=input_text.strip().upper()
    if input_text in df['Postcode'].values:
        return "the above postcode is covered"
    return "Above postcode is not covered"

@tool
def compare_amount_to_million(value:int, unit:str)->str:
  """
  Use this when user buying new house and provide budget to check if it is less than or more than 1 million.

  value: The numeric value (e.g., 5 for 5 Lakhs).
  unit: The unit (e.g., "lakh" or "crore" or "billion" or "thousand" or "million").

  """
  if unit.lower() == "lakh":
    value=value * 0.1
  elif unit.lower() == "crore":
    value=value * 10
  elif unit.lower() == "billion":
    value=value*100
  elif unit.lower() == "thousand":
    value=value*0.001
  if value>=1:
    return "Budget is above 1 million"
  return "Budget is less than 1 million"

Prompt=ChatPromptTemplate.from_messages([
    ("system",system_prompt),
    MessagesPlaceholder("input")
])


llm=ChatGroq(model="gemma2-9b-it")

llm_with_tool=llm.bind_tools([postcard_verifier,compare_amount_to_million])

chain=Prompt|llm_with_tool