import os

import streamlit as st
from openai import OpenAI

# Requires the OPENAI_API_KEY environment variable to be set.
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

st.set_page_config(page_title="Your Mountaineering Guide", page_icon="")

st.title("💬 Your Mountaineering Guide")

# Store conversation in Streamlit session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display previous messages
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get OpenAI response
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4o", "gpt-3.5-turbo"
        messages=st.session_state["messages"]
    )
    reply = response.choices[0].message.content

    # Add assistant message
    st.session_state["messages"].append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
