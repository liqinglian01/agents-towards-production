# app_deepseek.py
# DeepSeek 版：与原 app.py 的 UI 完全一致，只是把 LLM 后端从 OpenAI 换成 DeepSeek。
# DeepSeek 提供 OpenAI 兼容接口，所以仍然用 openai SDK，只需改 base_url 和 model。
# 需要环境变量 DEEPSEEK_API_KEY（写在 .env 里，本目录已有 .env 占位文件）。

import os
import openai
import streamlit as st

from dotenv import load_dotenv
import PyPDF2

load_dotenv()  # Load environment variables from .env

client = openai.OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://ai-api.d-robotics.cc/v1",  # DeepSeek 的 OpenAI 兼容接口
)


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text


def process_uploaded_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "text/plain":
        return uploaded_file.getvalue().decode("utf-8")
    else:
        return "Unsupported file type. Please upload a TXT or PDF file."


def generate_response(user_prompt, file_content=None):
    messages = []

    if file_content:
        messages.append({
            "role": "system",
            "content": f"The user has uploaded a file with the following content:\n\n{file_content}\n\nPlease consider this information when responding to their query."
        })

    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model="deepseek-flash",  # DeepSeek 对话模型
        messages=messages,
    )
    return response.choices[0].message.content


st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 AI Chatbot Assistant (DeepSeek)")
st.markdown("**Welcome!** Ask anything or upload a file for the bot to analyze.")

uploaded_file = st.sidebar.file_uploader("Upload a file (optional):", type=["txt", "pdf"])
file_content = None

if uploaded_file is not None:
    st.sidebar.write("Uploaded file:", f"**{uploaded_file.name}** ({uploaded_file.size} bytes)")
    with st.sidebar.spinner("Processing file..."):
        file_content = process_uploaded_file(uploaded_file)
    with st.sidebar.expander("File Content Preview"):
        st.write(file_content[:500] + "..." if len(file_content) > 500 else file_content)

if "messages" not in st.session_state:
    st.session_state.messages = []
if not st.session_state.messages:
    st.session_state.messages.append(
        {"role": "assistant", "content": "Hello! I'm here to help. Feel free to ask me anything or upload a file."}
    )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_msg := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            assistant_msg = generate_response(user_msg, file_content)
            st.markdown(assistant_msg)
    st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
