import streamlit as st

# ---------------------
# Page Config
# ---------------------
st.set_page_config(page_title="InMind AI", layout="wide")

# ---------------------
# Logo (centered)
# ---------------------
st.markdown(
    """
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 20px;">
        <img src="LOGO_PATH.png" alt="Logo" style="max-width: 250px;">
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------
# Custom CSS for chat bubbles
# ---------------------
st.markdown(
    """
    <style>
    .chat-bubble {
        display: inline-block;
        background-color: #f1f1f1;
        padding: 12px 18px;
        border-radius: 20px;
        margin: 6px 6px 6px 0;
        cursor: pointer;
        transition: background-color 0.2s ease;
        border: 1px solid #ddd;
    }
    .chat-bubble:hover {
        background-color: #e0e0e0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------
# Initialize session state
# ---------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        ("InMind AI", "👋 Hi, I’m InMind AI. I can share information about brain health, dementia, and Alzheimer’s. What would you like to know?")
    ]

# ---------------------
# FAQ Quick Replies (clickable bubbles)
# ---------------------
st.markdown("### Commonly Asked Questions")

faq_list = [
    "What are early signs of Alzheimer’s?",
    "How can I keep my brain healthy?",
    "What is dementia?",
    "Are memory lapses normal with aging?",
    "What lifestyle changes can reduce risk?",
]

# Create clickable FAQ bubbles
cols = st.columns(len(faq_list))
faq_clicked = None
for i, faq in enumerate(faq_list):
    if cols[i].button(faq, key=f"faq_{i}"):
        faq_clicked = faq
    cols[i].markdown(f"<div class='chat-bubble'>{faq}</div>", unsafe_allow_html=True)

# ---------------------
# Chatbot Section
# ---------------------
st.subheader("Chat with InMind AI")

# User input
user_input = st.text_input("You:", placeholder="Type your question here...")

# Use FAQ as input if clicked
if faq_clicked:
    user_input = faq_clicked

# Predefined responses
responses = {
    "What are early signs of Alzheimer’s?": "Early signs may include memory loss, difficulty completing familiar tasks, confusion with time/place, and changes in mood or personality.",
    "How can I keep my brain healthy?": "Regular exercise, balanced diet, social engagement, quality sleep, and mental stimulation are all key for brain health.",
    "What is dementia?": "Dementia is a general term for conditions that impair memory, thinking, and decision-making, such as Alzheimer’s disease.",
    "Are memory lapses normal with aging?": "Some memory lapses can be normal with age, but frequent or severe issues may need medical evaluation.",
    "What lifestyle changes can reduce risk?": "Staying active, avoiding smoking, eating a healthy diet, and managing blood pressure and diabetes can reduce risk."
}

# Generate response
if user_input:
    st.session_state["messages"].append(("You", user_input))
    response = responses.get(
        user_input,
        "Sorry, I couldn’t find information on that. Please try another term or consult a healthcare professional."
    )
    st.session_state["messages"].append(("InMind AI", response))

# Display chat history
for sender, msg in st.session_state["messages"]:
    if sender == "You":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**🤖 InMind AI:** {msg}")

# Clear chat button
if st.button("Clear Chat"):
    st.session_state["messages"] = [
        ("InMind AI", " Hi, I’m InMind AI. I can share information about brain health, dementia, and Alzheimer’s. What would you like to know?")
    ]
    st.rerun()

# ---------------------
# Disclaimer (centered)
# ---------------------
st.markdown(
    """
    <div style="text-align: center; margin-top: 30px; font-size: 12px; color: gray;">
         This tool is for informational purposes only and is not a substitute for professional medical advice.  
        Always consult a qualified healthcare provider with questions regarding your health.
    </div>
    """,
    unsafe_allow_html=True,
)
