import streamlit as st
from main import get_response
import logging
import re

# --------------------------------------------
# Streamlit Page Config
# --------------------------------------------
st.set_page_config(page_title="Fast AI Health Advisor", layout="wide")

st.title("Fast AI – Your Personal Health Advisor")

# --------------------------------------------
# Sidebar Navigation
# --------------------------------------------
page = st.sidebar.selectbox(
    "Navigate to:",
    ["Home", "Physical Activity", "List of Services", "Contact"]
)

language = st.sidebar.selectbox(
    "Select Language:",
    ["English", "Spanish", "French", "Deutsch"]
)

# --------------------------------------------
# Helper: clean and format AI Markdown
# --------------------------------------------
def format_ai_response(response: str) -> str:
    if not response:
        return "No response generated."

    # Remove redundant "Assistant:" prefixes
    response = re.sub(r"(?i)^assistant:\s*", "", response.strip())
    response = re.sub(r"(?i)assistant:", "", response)

    # Replace inline citations <1>, <2>, <3> with [1], [2], [3]
    response = re.sub(r"<(\d+)>", r"[\1]", response)

    # Split citations block
    if "Citations:" in response:
        main_text, citations = response.split("Citations:", 1)
        main_text = main_text.strip()
        citations = citations.strip()

        # Reformat citations as numbered Markdown list
        citation_lines = [line.strip() for line in citations.split("\n") if line.strip()]
        formatted_citations = "\n\n**Citations:**\n" + "\n".join(f"{i+1}. {line}" for i, line in enumerate(citation_lines))

        response = main_text + formatted_citations

    # Ensure proper line breaks for Markdown
    response = response.replace("\r\n", "\n").replace("\n\n", "\n\n")
    return response


# --------------------------------------------
# Home Page
# --------------------------------------------
if page == "Home":
    st.subheader("Chat with your AI Health Advisor")
    st.write("Ask any question related to health, wellness, or lifestyle.")

    user_input = st.text_input("Type your question below:")

    if st.button("Send") and user_input.strip():
        with st.spinner("Thinking..."):
            try:
                # Get AI response
                response = get_response(user_input, language)
            except Exception as e:
                logging.error(f"Error during get_response: {e}")
                response = "Sorry, something went wrong. Please try again later."

        # --------------------------------------------
        # Render AI response with Markdown formatting
        # --------------------------------------------
        st.markdown(f"**AI ({language}):**")

        formatted_response = format_ai_response(response)
        st.markdown(formatted_response, unsafe_allow_html=False)

    else:
        st.info("Example: 'What is the best exercise for heart health?'")

# --------------------------------------------
# Physical Activity Page
# --------------------------------------------
elif page == "Physical Activity":
    st.switch_page("pages/physical_activity.py")

# --------------------------------------------
# List of Services
# --------------------------------------------
elif page == "List of Services":
    st.subheader("Available Health Services")
    st.markdown("""
    - Personalized Health Checkup  
    - Nutrition and Diet Planning  
    - Physical Activity Recommendation  
    - Lifestyle and Stress Management  
    - Sleep Optimization Tips  
    """)

# --------------------------------------------
# Contact Page
# --------------------------------------------
elif page == "Contact":
    st.subheader("Contact Us")
    st.markdown("""
    **Email:** info@fastai.com  
    **Website:** [www.fastai.com](https://www.fastai.com)  
    **Phone:** +1 234 567 8900  
    """)
