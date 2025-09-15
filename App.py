import streamlit as st
import requests
from datetime import datetime
from io import BytesIO
from docx import Document

# -------------------------------
# Config & Styling
# -------------------------------
st.set_page_config(page_title="InMind", layout="centered")

ACCENT = "#FDD2DC"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: #000000;
        color: #ffffff;
    }}
    h1, h2, h3 {{
        color: #ffffff;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
    }}
    a, .accent {{ color: {ACCENT}; }}
    .stChatMessage {{ font-size: 1.05em; line-height: 1.6; }}
    .footer {{ font-size: 0.8em; text-align: center; color: #888888; margin-top: 3em; }}
    div[data-baseweb="base-input"] > div {{
        border-color: {ACCENT} !important;
    }}
    button[kind="primary"] {{
        background: {ACCENT} !important;
        color: #000 !important;
        border-radius: 8px !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Branding
# -------------------------------
LOGO_PATH = "LOGO_PATH.png"

st.markdown(
    f"""
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px;">
        <img src="https://raw.githubusercontent.com/libbymatheus/InMind/main/LOGO_PATH.png" 
             alt="InMind Logo" width="200">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="text-align: center; font-size:18px;">
        A free, conversational assistant.</b>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Hugging Face API (free model)
# -------------------------------
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"
HF_HEADERS = {"Authorization": f"Bearer {st.secrets['HF_API_KEY']}"}

def query_huggingface(prompt):
    response = requests.post(
        HF_API_URL,
        headers=HF_HEADERS,
        json={"inputs": prompt, "parameters": {"max_new_tokens": 300}}
    )
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"].strip()
        elif isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"].strip()
        else:
            return "⚠️ Model returned an unexpected response."
    else:
        return f"⚠️ Error {response.status_code}: {response.text}"

# -------------------------------
# Conversation State
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm InMind. Ask me anything!", "time": datetime.now()}
    ]

# Show history
for msg in st.session_state.messages:
    with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
        st.markdown(msg["content"])

# -------------------------------
# Chat Input
# -------------------------------
if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "time": datetime.now()})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply = query_huggingface(prompt)

    st.session_state.messages.append({"role": "assistant", "content": reply, "time": datetime.now()})
    with st.chat_message("assistant"):
        st.markdown(reply)

# -------------------------------
# Disclaimer, Download, Clear Chat
# -------------------------------
st.markdown("---")
st.markdown(
    "<div class='footer'>Disclaimer: InMind AI is for educational purposes only and does not provide medical diagnoses. Always consult a licensed healthcare professional for medical advice.</div>",
    unsafe_allow_html=True
)

if st.session_state.get("messages"):
    # --- TXT transcript ---
    transcript_txt = "InMind Chat Transcript\n"
    transcript_txt += f"Session started: {st.session_state.messages[0]['time'].strftime('%Y-%m-%d %H:%M:%S')}\n"
    transcript_txt += "-" * 40 + "\n\n"
    for m in st.session_state.messages:
        timestamp = m["time"].strftime("%H:%M:%S")
        speaker = "You" if m["role"] == "user" else "InMind"
        transcript_txt += f"[{timestamp}] {speaker}: {m['content']}\n\n"

    st.download_button(
        label="📥 Download Chat History (.txt)",
        data=transcript_txt,
        file_name="inmind_chat.txt",
        mime="text/plain"
    )

    # --- DOCX transcript ---
    doc = Document()
    doc.add_heading("InMind Chat Transcript", 0)
    doc.add_paragraph(f"Session started: {st.session_state.messages[0]['time'].strftime('%Y-%m-%d %H:%M:%S')}")
    doc.add_paragraph("-" * 40)

    for m in st.session_state.messages:
        timestamp = m["time"].strftime("%H:%M:%S")
        speaker = "You" if m["role"] == "user" else "InMind"
        p = doc.add_paragraph()
        p.add_run(f"[{timestamp}] {speaker}: ").bold = True
        p.add_run(m["content"])

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        label="📥 Download Chat History (.docx)",
        data=buffer,
        file_name="inmind_chat.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# Clear chat
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm InMind. Ask me anything!", "time": datetime.now()}
    ]
    st.experimental_rerun()
