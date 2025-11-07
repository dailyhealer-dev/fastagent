import streamlit as st
from agents.nutrition_agent import get_nutrition_response
import datetime

st.header("Nutrition & Healthy Lifestyle Dashboard")

# ------------------------------------------------------------
# Tabs for different nutrition components
# ------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Personalized Nutrition Plan",
    "Daily Nutrition Tips",
    "Hydration & Meal Tracker",
    "Nutrition Insights"
])

# ------------------------------------------------------------
# TAB 1 — Personalized Nutrition Plan
# ------------------------------------------------------------
with tab1:
    st.subheader("Personalized Nutrition Recommendations")

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age", min_value=0, max_value=120, value=30, key="nt_age")
    with col2:
        sex = st.selectbox("Sex", ["Male", "Female", "Other"], key="nt_sex")
    with col3:
        goal = st.selectbox(
            "Goal",
            ["Weight Loss", "Muscle Gain", "Balanced Diet", "Heart Health"],
            key="nt_goal"
        )

    condition = st.selectbox(
        "Health Condition (Optional)",
        ["None", "Diabetes", "Hypertension", "High Cholesterol", "Anemia"],
        key="nt_condition"
    )

    if st.button("Get Nutrition Plan", key="nt_plan_btn"):
        query = (
            f"Provide a detailed nutrition plan for a {age}-year-old {sex} with {condition}. "
            f"The goal is {goal}. Include meal balance, nutrient focus, and portion guidance."
        )
        plan = get_nutrition_response(query)
        st.text_area("AI Nutrition Plan", plan, height=220)

# ------------------------------------------------------------
# TAB 2 — Daily Nutrition Tips
# ------------------------------------------------------------
with tab2:
    st.subheader("Daily Tips for Healthier Eating")

    if st.button("Get Daily Tips", key="nt_tips_btn"):
        query_tips = (
            f"Generate 3 practical daily nutrition tips for a {age}-year-old {sex} with {condition}, "
            f"aiming for {goal}. Focus on hydration, food diversity, and meal timing."
        )
        tips = get_nutrition_response(query_tips)
        st.text_area("AI Daily Tips", tips, height=180)

# ------------------------------------------------------------
# TAB 3 — Hydration & Meal Tracker
# ------------------------------------------------------------
with tab3:
    st.subheader("Hydration & Meal Tracker")

    today = datetime.date.today()
    if "hydration" not in st.session_state:
        st.session_state["hydration"] = {}
    if "meals_logged" not in st.session_state:
        st.session_state["meals_logged"] = {}

    water_intake = st.number_input("Water intake (cups) today:", min_value=0, max_value=30, step=1)
    if st.button("Log Hydration", key="nt_hydration_btn"):
        st.session_state["hydration"][str(today)] = water_intake
        st.success(f"Hydration logged for {today}: {water_intake} cups")

    st.divider()
    meal = st.text_input("Describe your recent meal")
    if st.button("Log Meal", key="nt_meal_btn"):
        meals = st.session_state["meals_logged"].get(str(today), [])
        meals.append(meal)
        st.session_state["meals_logged"][str(today)] = meals
        st.success("Meal logged successfully.")

    if st.checkbox("Show Today’s Logs", key="nt_show_logs"):
        st.write("### Today's Logs")
        st.write("Hydration:", st.session_state["hydration"].get(str(today), "Not logged"))
        st.write("Meals:", st.session_state["meals_logged"].get(str(today), []))

# ------------------------------------------------------------
# TAB 4 — Nutrition Insights
# ------------------------------------------------------------
with tab4:
    st.subheader("AI-Driven Nutrition Insights")

    insights_query = st.text_area(
        "Ask a question about nutrition (e.g., 'What are good sources of protein for heart health?')",
        height=100
    )
    if st.button("Get Insight", key="nt_insight_btn"):
        response = get_nutrition_response(insights_query)
        st.text_area("AI Nutrition Insight", response, height=220)
