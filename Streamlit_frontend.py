import streamlit as st
from backend_with_tools import chatbot
from langchain_core.messages import HumanMessage, AIMessage
from Simp_langgraph_backend import retrieve_all_threads
import uuid



def create_thread_id() : # creates random thread_id
    th_id = uuid.uuid4()
    return th_id

def add_thread(thread_id) : # add thread_id to chat_threads list where all threads are present 
    if thread_id not in st.session_state["chat_threads"] :
        st.session_state["chat_threads"].append(thread_id)

def reset_chat() : # if we create new chat then it is used
    th_id = create_thread_id()
    st.session_state["thread_id"] = th_id
    add_thread(st.session_state["thread_id"])
    st.session_state["message_hist"] = []
    
def load_conv(thread_id):
  state = chatbot.get_state({"configurable": {"thread_id": thread_id}})
  # Safely check if values and messages exist to prevent KeyErrors
  if state and state.values:
    return state.values.get("messages", [])
  return []
    


# we will use streamlit inbuilt dictionary for message history storage which is {session_state -> dict}
st.title("AAJ's Chatbot")

if "message_hist" not in st.session_state :
    st.session_state["message_hist"] = []
    
if "thread_id" not in st.session_state :
    st.session_state["thread_id"] = create_thread_id()
    
if "chat_threads" not in st.session_state :
    st.session_state["chat_threads"] = retrieve_all_threads()
    
add_thread(st.session_state["thread_id"])
    
with st.sidebar:
    st.title("AAJ Chatbot")
    
    # Start chat button
    if st.button("New Chat", type="primary", use_container_width=True):
        reset_chat()
    
    st.markdown("---")
    st.header("Chat History")
    
    for thread_id in reversed(st.session_state["chat_threads"]) :
        if st.button(str(thread_id)) :
            st.session_state["thread_id"] = thread_id
            messages = load_conv(thread_id)
            
            temp_messages = []
            for message in messages :
                if isinstance(message, HumanMessage): # isinstance(object, class): A built-in Python function that returns True if the object matches the class, and False otherwise
                    role = "user"
                else :
                    role = "assistant"
                
                temp_messages.append({"role" : role, "content" : message.content})
            
            st.session_state["message_hist"] = temp_messages
            

for message in st.session_state["message_hist"] :
    with st.chat_message(message["role"]) :
        st.text(message["content"])

input = st.chat_input("Please enter query")

if input :  
    # adding message to history
    st.session_state["message_hist"].append({"role" : "user", "content" : input})
    with st.chat_message('user') : # here we just add user animated block in our frontend 
        st.write(input)
    
    with st.chat_message("assistant") : # here we just add assistant animated block in our frontend
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=input)]},
                config={"configurable" : {"thread_id" : st.session_state["thread_id"]}},
                stream_mode="messages",
            ):
                if isinstance(message_chunk, AIMessage):
                    # yield only assistant tokens
                    yield message_chunk.content


        ai_message = st.write_stream(ai_only_stream())
        # ai_message = st.write_stream(
        #     message_chunk.content for message_chunk, metadata in chatbot.stream(
        #         {"messages" : [HumanMessage(content=input)]},
        #         config={"configurable" : {"thread_id" : st.session_state["thread_id"]}}, 
        #         stream_mode="messages")
        # )
    
    st.session_state["message_hist"].append({"role" : "assistant", "content" : ai_message})