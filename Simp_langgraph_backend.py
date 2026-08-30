from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatOllama(model="llama3.2:3b") 

class ChatState(TypedDict) :
    message : Annotated[list[BaseMessage], add_messages]
    
def chat_node(state : ChatState) -> ChatState :
    sys_msg = SystemMessage(content="You are a helpful AI assistant. Always keep answers concise and easy to read")
    full_message = [sys_msg] + state['message']
    response = llm.invoke(full_message)
    return {"message" : [response]}

checkpointer = InMemorySaver()

graph = StateGraph(ChatState)

graph.add_node("ChatNode", chat_node)
graph.add_edge(START, "ChatNode")
graph.add_edge("ChatNode", END)

chatbot = graph.compile(checkpointer=checkpointer)