import streamlit as st
import requests

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
LOGO_PATH = "LOGO_PATH.PNG"

try:
    st.image(LOGO_PATH, use_column_width=True)
except Exception:
    st.write("*Logo not found — upload it to your repo.*")
st.write(
    "A free, conversational assistant specialized in **health and brain awareness**. "
    "This is **not** a diagnostic tool."
)
# -------------------------------
# Hugging Face API
# -------------------------------
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HF_HEADERS = {"Authorization": f"Bearer {st.secrets['HF_API_KEY']}"}

def query_huggingface(prompt):
    response = requests.post(
        HF_API_URL,
        headers=HF_HEADERS,
        json={"inputs": prompt, "parameters": {"max_new_tokens": 300}}
    )
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
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
        {"role": "assistant", "content": "Hi! I'm InMind. Ask me anything — I specialize in health but can chat about anything."}
    ]

# Show history
for msg in st.session_state.messages:
    with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
        st.markdown(msg["content"])

# -------------------------------
# Chat Input
# -------------------------------
if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply = query_huggingface(prompt)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

# -------------------------------
# Disclaimer
# -------------------------------
st.markdown("---")
st.markdown(
    "<div class='footer'>Disclaimer: InMind AI is for educational purposes only and does not provide medical diagnoses. Always consult a licensed healthcare professional for medical advice.</div>",
    unsafe_allow_html=True
)
