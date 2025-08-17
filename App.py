import streamlit as st

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="InMind Chatbot", layout="centered")

# Dark theme styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    h1 {
        color: #ffffff;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stChatMessage {
        font-size: 1.05em;
        line-height: 1.6;
    }
    .footer {
        font-size: 0.8em;
        text-align: center;
        color: #888888;
        margin-top: 3em;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Branding
# -------------------------------
st.title("🧠 InMind: Neuro Chatbot")
st.write("This chatbot provides **educational insights** into possible early symptoms of neurodegenerative diseases. It does not provide medical diagnoses. Always consult a physician for concerns.")

# -------------------------------
# Chat Session Setup
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------
# Chat Input
# -------------------------------
if prompt := st.chat_input("Describe the symptoms you’re noticing..."):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # -------------------------------
    # Simple Inference Engine
    # -------------------------------
    response = "I’m not sure yet, but here are some things to consider."

    text = prompt.lower()

    if "memory" in text or "forget" in text or "confusion" in text:
        response = (
            "🔎 These symptoms may be consistent with **early Alzheimer's-type changes**.\n\n"
            "**What to watch for next:** speech difficulties, poor judgment, and disorientation.\n\n"
            "**Next steps:**\n"
            "- Schedule a memory screening with a doctor.\n"
            "- Keep a symptom diary.\n"
            "- Share changes with family members.\n"
            "- Encourage regular cognitive activity and exercise."
        )
    elif "tremor" in text or "stiffness" in text or "movement" in text:
        response = (
            "🔎 These symptoms may suggest **Parkinson’s-related changes**.\n\n"
            "**What to watch for next:** fine motor decline, sleep disturbances, and mood changes.\n\n"
            "**Next steps:**\n"
            "- Visit a neurologist for a movement evaluation.\n"
            "- Track motor changes daily.\n"
            "- Encourage physical therapy and regular stretching.\n"
            "- Monitor sleep quality."
        )
    elif "speech" in text or "words" in text or "talk" in text:
        response = (
            "🔎 These symptoms could relate to **Frontotemporal Degeneration (FTD)**.\n\n"
            "**What to watch for next:** mood swings, risky behavior, and disorientation.\n\n"
            "**Next steps:**\n"
            "- Consult a neurologist specializing in dementia.\n"
            "- Encourage structured routines.\n"
            "- Track changes in decision-making and communication."
        )
    else:
        response = (
            "🔎 The description doesn’t strongly match a specific condition yet.\n\n"
            "**What to do meanwhile:**\n"
            "- Keep a diary of symptoms over the next 3–6 months.\n"
            "- Encourage healthy lifestyle habits (sleep, diet, exercise).\n"
            "- Consult a physician if symptoms progress or worsen."
        )

    # -------------------------------
    # Show AI Response
    # -------------------------------
    with st.chat_message("assistant"):
        st.markdown(response)

    # Save to session
    st.session_state.messages.append({"role": "assistant", "content": response})

# -------------------------------
# Disclaimer
# -------------------------------
st.markdown("---")
st.markdown(
    "<div class='footer'>Disclaimer: This tool is for educational purposes only and not a medical diagnosis. Always consult a healthcare provider for medical advice.</div>",
    unsafe_allow_html=True
)
