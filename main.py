import socket
import uvicorn
from fastapi import FastAPI
from model import chain,postcard_verifier,compare_amount_to_million
from langchain_core.messages import AIMessage,HumanMessage
from schema import chatData
app=FastAPI()

@app.get("/")
def start():
    return f"Hey, I am Running !! {socket.gethostname()}"

@app.post("/api/v1/chat")
def model_output(session_state_messages:chatData):
    formatted_messages = [
        HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"])
        for msg in session_state_messages.data
    ]
    print(formatted_messages)
    response=chain.invoke({"input":formatted_messages})
    tool_called=response.additional_kwargs.get("tool_calls",None)
    if tool_called:
        if response.tool_calls[0]["name"]=="postcard_verifier":
            formatted_messages.append(postcard_verifier.invoke(response.tool_calls[0]))
            response=chain.invoke({"input":formatted_messages})
        elif response.tool_calls[0]["name"]=="compare_amount_to_million":
            formatted_messages.append(compare_amount_to_million.invoke(response.tool_calls[0]))
            response=chain.invoke({"input":formatted_messages})
    return response

if __name__=="__main__":
    uvicorn.run(app="main:app",host="0.0.0.0",port=5000,reload=True)