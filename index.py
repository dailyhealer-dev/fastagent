# index.py
import streamlit as st
from main import get_response
import logging


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
    "🌐 Select Language:",
    ["English", "Spanish", "French", "Deutsch"]
)

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
                response = get_response(user_input, language)
            except Exception as e:
                logging.error(f"Error during get_response: {e}")
                response = "Sorry, something went wrong. Please try again later."
        st.markdown(f"** AI ({language}):** {response}")

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
    st.subheader("🩺 Available Health Services")
    st.markdown("""
    - ✅ Personalized Health Checkup  
    - 🥗 Nutrition & Diet Planning  
    - 💪 Physical Activity Recommendation  
    - 🧘 Lifestyle & Stress Management  
    - 💤 Sleep Optimization Tips  
    """)

# --------------------------------------------
# Contact Page
# --------------------------------------------
elif page == "Contact":
    st.subheader("📞 Contact Us")
    st.markdown("""
    **Email:** info@fastai.com  
    **Website:** [www.fastai.com](https://www.fastai.com)  
    **Phone:** +1 234 567 8900  
    """)
