import streamlit as st
import json
import requests

base_url="http://127.0.0.1:5000/api/v1/"

if "messages" not in st.session_state:
    st.session_state.messages=[{"role":"assistant","content":"How may I help you?"}]

for data in st.session_state.messages:
    with st.chat_message(data['role']):
        st.write(data["content"])

input=st.chat_input("Chat with bot")

if input:
    with st.chat_message("user"):
        st.markdown(input)
    st.session_state.messages.append({"role":"user","content":input})
    url=base_url+"chat"
    response=json.loads(requests.post(url,json={"data":st.session_state.messages}).content)
    with st.chat_message("assistant"):
        st.markdown(response.get("content"))
    st.session_state.messages.append({"role":"assistant","content":response.get("content")})