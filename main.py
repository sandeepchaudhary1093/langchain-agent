import os

import streamlit as st

from app import create_agent_executor


st.set_page_config(page_title="News & Weather Agent", page_icon="🌐")
st.title("News & Weather Agent")
st.caption("Ask for current news, weather, or both.")

missing_keys = [
    key
    for key in ("OPENAI_API_KEY", "TAVILY_API_KEY")
    if not os.getenv(key)
]
if missing_keys:
    st.error(
        "Add the following required keys to your .env file before chatting: "
        + ", ".join(missing_keys)
    )

if "messages" not in st.session_state:
    st.session_state.messages = []


@st.cache_resource
def get_agent_executor():
    return create_agent_executor()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input(
    "For example: What's the latest AI news and the weather in Bengaluru?",
    disabled=bool(missing_keys),
)

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching and preparing an answer..."):
            try:
                agent_executor = get_agent_executor()
                response = agent_executor.invoke({"input": question})
                answer = response["output"]
            except Exception as exc:
                st.error(f"Request failed ({type(exc).__name__}): {exc}")
            else:
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
