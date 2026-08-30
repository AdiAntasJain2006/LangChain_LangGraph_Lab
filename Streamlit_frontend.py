import streamlit as st
from Simp_langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

# we will use streamlit inbuilt dictionary for message history storage which is {session_state -> dict}
st.title("LangGraph Ollama Chatbot")

if "message_hist" not in st.session_state :
    st.session_state["message_hist"] = []

for message in st.session_state["message_hist"] :
    with st.chat_message(message["role"]) :
        st.text(message["content"])

input = st.chat_input("Please enter query")

if input :  
    # adding message to history
    st.session_state["message_hist"].append({"role" : "user", "content" : input})
    with st.chat_message('user') :
        st.write(input)
    
    with st.chat_message("assistant") :
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {"message" : [HumanMessage(content=input)]},
                config={"configurable" : {"thread_id" : "id_1"}}, 
                stream_mode="messages")
        )
    
    st.session_state["message_hist"].append({"role" : "assistant", "content" : ai_message})