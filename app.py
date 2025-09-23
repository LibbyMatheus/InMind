import streamlit as st
import wikipedia
import requests

# Set page config
st.set_page_config(page_title="InMind", layout="wide")

# Centered logo instead of title
LOGO_PATH = "LOGO_PATH.png"
st.markdown(
    f"<div style='text-align: center;'><img src='{LOGO_PATH}' width='250'></div>",
    unsafe_allow_html=True
)

# Sidebar FAQs
st.sidebar.header("FAQs")
FAQS = {
    "What is dementia?": "dementia",
    "What is Alzheimer’s disease?": "Alzheimer's disease",
    "What is a stroke?": "Stroke (medicine)",
    "What is Parkinson’s disease?": "Parkinson's disease",
    "What is ALS?": "Amyotrophic lateral sclerosis",
}

faq_choice = st.sidebar.radio("Choose a question:", list(FAQS.keys()))

# Query processor
def get_wikipedia_answer(query):
    try:
        # Prioritize medical pages
        if "stroke" in query.lower():
            query = "Stroke (medicine)"
        
        # If user asks for causes
        if "cause" in query.lower() or "etiology" in query.lower():
            search_results = wikipedia.search(query, results=1)
            if not search_results:
                return "Sorry, I couldn’t find a clear cause."
            page_title = search_results[0]
            page = wikipedia.page(page_title)
            
            # Try to extract causes section
            for section in page.content.split("=="):
                if "cause" in section.lower() or "etiology" in section.lower():
                    return section.strip()
            return wikipedia.summary(page_title, sentences=3)

        # Subcategories / niche queries
        search_results = wikipedia.search(query, results=3)
        if search_results:
            for result in search_results:
                if any(word in result.lower() for word in query.lower().split()):
                    return wikipedia.summary(result, sentences=3)
            return wikipedia.summary(search_results[0], sentences=3)

        return "Sorry, I couldn’t find an answer for that."

    except Exception as e:
        return f"Error: {str(e)}"

# Display FAQ or user query
if faq_choice:
    st.subheader(faq_choice)
    answer = get_wikipedia_answer(FAQS[faq_choice])
    st.write(answer)

# User input
user_query = st.text_input("Ask InMind anything:")

if user_query:
    response = get_wikipedia_answer(user_query)
    st.subheader("Answer:")
    st.write(response)
