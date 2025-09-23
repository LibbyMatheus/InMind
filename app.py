import streamlit as st
import wikipedia

# Set page config
st.set_page_config(page_title="InMind", layout="wide")

# Greeting
st.markdown(
    "<h4 style='text-align: center;'>Welcome to InMind — your neuroscience and healthcare companion.</h4>",
    unsafe_allow_html=True
)

# Centered logo (no title)
LOGO_PATH = "LOGO_PATH.png"
st.markdown(
    f"<div style='text-align: center; margin-bottom:20px;'><img src='{LOGO_PATH}' width='250'></div>",
    unsafe_allow_html=True
)

# Sidebar FAQs
st.sidebar.header("FAQs")
FAQS = {
    "What is dementia?": "dementia",
    "What is Alzheimer’s disease?": "Alzheimer's disease",
    "What is Parkinson’s disease?": "Parkinson's disease",
    "What is ALS?": "Amyotrophic lateral sclerosis",
}

faq_choice = st.sidebar.radio("Choose a question:", list(FAQS.keys()), index=None)

# Chat messages storage
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Synonyms for detection ---
CAUSE_SYNONYMS = ["cause", "causes", "etiology", "risk factor", "risk factors", "origin", "trigger", "triggers", "reason", "reasons", "mechanism"]
PREVENT_SYNONYMS = ["prevent", "prevention", "preventable", "avoiding", "prophylaxis", "treatment", "therapy", "management", "intervention", "reduce risk"]

# --- Wikipedia search ---
def get_wikipedia_answer(query):
    try:
        query_lower = query.lower()

        # Force medical stroke
        if "stroke" in query_lower:
            query = "Stroke (medicine)"

        # Detect cause-related queries
        if any(word in query_lower for word in CAUSE_SYNONYMS):
            search_results = wikipedia.search(query, results=1)
            if not search_results:
                return "Sorry, I couldn’t find a clear cause."
            page = wikipedia.page(search_results[0])
            for section in page.content.split("=="):
                if any(word in section.lower() for word in CAUSE_SYNONYMS):
                    return section.strip()
            return wikipedia.summary(page.title, sentences=3)

        # Detect prevention/treatment/management queries
        if any(word in query_lower for word in PREVENT_SYNONYMS):
            search_results = wikipedia.search(query, results=1)
            if not search_results:
                return "Sorry, I couldn’t find clear prevention/treatment information."
            page = wikipedia.page(search_results[0])
            for section in page.content.split("=="):
                if any(word in section.lower() for word in PREVENT_SYNONYMS):
                    return section.strip()
            return wikipedia.summary(page.title, sentences=3)

        # General / subcategory queries
        search_results = wikipedia.search(query, results=3)
        if search_results:
            for result in search_results:
                if all(word in result.lower() for word in query_lower.split()):
                    return wikipedia.summary(result, sentences=3)
            return wikipedia.summary(search_results[0], sentences=3)

        return "Sorry, I couldn’t find an answer for that."

    except Exception as e:
        return f"Error: {str(e)}"

# --- Display FAQ ---
if faq_choice:
    st.subheader(faq_choice)
    answer = get_wikipedia_answer(FAQS[faq_choice])
    st.write(answer)

# --- User input ---
user_query = st.text_input("Ask InMind anything:")

if user_query:
    response = get_wikipedia_answer(user_query)
    st.subheader("Answer:")
    st.write(response)

# --- Clear chat ---
if st.button("Clear Chat"):
    st.session_state["messages"] = []
    st.rerun()

# --- Disclaimer ---
st.markdown(
    """
    <div style="text-align: center; margin-top: 30px; font-size: 13px; color: gray;">
        Disclaimer: InMind provides educational information only. It is not a substitute for professional medical advice.
    </div>
    """,
    unsafe_allow_html=True
)
