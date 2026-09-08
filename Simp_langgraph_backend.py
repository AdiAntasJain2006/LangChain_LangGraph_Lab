from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
import sqlite3

llm = ChatOllama(model="llama3.2:3b") 

class ChatState(TypedDict) :
    message : Annotated[list[BaseMessage], add_messages]
    
def chat_node(state : ChatState) -> ChatState :
    sys_msg = SystemMessage(content="You are a helpful AI assistant. Always keep answers concise and easy to read")
    full_message = [sys_msg] + state['messages']
    response = llm.invoke(full_message)
    return {"messages" : [response]}

conn = sqlite3.connect(database="AAJ_database.db", check_same_thread=False)

ck_pointer = SqliteSaver(conn = conn) # we use it because after completing this code one time chatstate gets empty so we store its last state in our memory using this checkpointer

graph = StateGraph(ChatState)

graph.add_node("ChatNode", chat_node)
graph.add_edge(START, "ChatNode")
graph.add_edge("ChatNode", END)

chatbot = graph.compile(checkpointer=ck_pointer)

# result = chatbot.invoke(
#                 {"message" : [HumanMessage(content="Hello buddy my name is adi")]},
#                 config={"configurable" : {"thread_id" : "thread_1"}})

# for checkpoint in ck_pointer.list(None) :
#     print(checkpoint.config["configurable"]["thread_id"])

def retrieve_all_threads() :
    all_threads = set()
    for checkpoint in ck_pointer.list(None) :
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
        
    return list(all_threads)
    
