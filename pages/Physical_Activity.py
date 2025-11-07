# physical_activity_component.py
import streamlit as st
from agents.physical_activity_agent import get_physical_activity_response
import datetime

st.header('Physical Activity Dashboard')

# ----------------------------
# User inputs (inline)
# ----------------------------
age = st.number_input("Age", min_value=0, max_value=120, value=30, key="pa_age")
sex = st.selectbox("Sex", ["Male", "Female", "Other"], key="pa_sex")
condition = st.selectbox(
    "Health Condition (Optional)", 
    ["None", "Hypertension", "Diabetes", "Arthritis"], 
    key="pa_condition"
)
goal = st.selectbox(
    "Fitness Goal", 
    ["General Health", "Strength", "Endurance", "Balance", "Flexibility"], 
    key="pa_goal"
)

# ----------------------------
# Exercise Recommendation
# ----------------------------
st.subheader("Exercise Recommendation")
if st.button("Get Recommendations", key="pa_recommend_btn"):
    query = f"Provide personalized exercise recommendations for a {age}-year-old {sex} with {condition}, focusing on {goal}. Include practical daily tips and simple exercises."
    recommendation = get_physical_activity_response(query)
    st.text_area("AI Exercise Guidance", recommendation, height=200)

# ----------------------------
# Importance of Exercise (static)
# ----------------------------
st.subheader("Why Exercise Matters")
importance_text = (
    "Regular physical activity improves cardiovascular health, strengthens muscles and bones, "
    "improves balance and coordination, enhances mental well-being, reduces risk of chronic disease, "
    "and boosts overall quality of life."
)
st.info(importance_text)

# ----------------------------
# Daily Tips (AI RAG-driven)
# ----------------------------
st.subheader("Daily Tips to Improve Physical Activity")
if st.button("Get Daily Tips", key="pa_daily_tips"):
    query_tips = f"Generate 3 practical daily tips for a {age}-year-old {sex} with {condition} based on physical activity guidelines."
    tips_response = get_physical_activity_response(query_tips)
    st.text_area("AI Daily Tips", tips_response, height=150)

# ----------------------------
# Exercise Reminder / Tracker
# ----------------------------
st.subheader("Exercise Reminder")
today = datetime.date.today()
if "exercise_done" not in st.session_state:
    st.session_state["exercise_done"] = {}

done_today = st.session_state["exercise_done"].get(str(today), False)

if done_today:
    st.info("You have completed your exercise for today.")
else:
    if st.button("Mark Exercise Done Today", key="pa_done_today"):
        st.session_state["exercise_done"][str(today)] = True
        st.info("Exercise for today has been marked as completed.")
