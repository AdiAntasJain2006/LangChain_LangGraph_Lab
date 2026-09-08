from langgraph.graph import START, END, StateGraph, MessagesState
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import SystemMessage, HumanMessage
from functools import partial
import sqlite3
import requests

search_tool = DuckDuckGoSearchRun()

@tool("Calci", description="this is calculator and it can only do four operations Addition, Multiplication, Subtraction and Division")
def calculator(num1 : float, num2 : float, operation : str) :
    """This function act as a calculator where we provide 2 numbers and provide operation 
    so that it can do calculation based on given operation such as 
    Multiplication, Division, Addition, Subtraction"""
    try :
        if(operation == "add") :
            result = num1 + num2
        elif(operation == "subtract") :
            result = num1 - num2
        elif(operation == "multiplication") :
            result = num2 * num1
        elif(operation == "division") :
            if(num2 == 0) :
                return {"error" : "divide by zero error"}
            result = num1 / num2
        else :
            return {"error" : "invalid operator"}
        
        return {"result" : result, "num1" : num1, "num2" : num2, "operation" : operation}
        
    except Exception as e :
        return {"error" : str(e)}


tools = [search_tool, calculator]

llm = ChatOllama(model="llama3.2:3b") 

llm_with_tools = llm.bind_tools(tools)

# class ChatState(TypedDict) :
#     messages : Annotated[list[BaseMessage], add_messages]
    
def chat_node(state : MessagesState) -> MessagesState :
    sys_msg = SystemMessage(content="You are a helpful AI assistant. Always keep answers concise and easy to read")
    full_message = [sys_msg] + state['messages']
    response = llm_with_tools.invoke(full_message)
    return {"messages" : [response]}

conn = sqlite3.connect(database="AAJ_database.db", check_same_thread=False)

ck_pointer = SqliteSaver(conn = conn) # we use it because after completing this code one time chatstate gets empty so we store its last state in our memory using this checkpointer

graph = StateGraph(MessagesState)

graph.add_node("ChatNode", chat_node)
graph.add_node("tools", ToolNode(tools=tools))

graph.add_edge(START, "ChatNode")
graph.add_conditional_edges("ChatNode", tools_condition)
graph.add_edge("tools", "ChatNode")
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
    
