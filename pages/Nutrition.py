# nutrition_dashboard.py
import streamlit as st
import datetime
import sqlite3
from agents.nutrition_agent import get_nutrition_response

# ---------------------------- Helper Functions ----------------------------
def get_user_data(username):
    """
    Fetch user nutrition-related info from SQLite database as a dictionary.
    Returns empty dict if no data found.
    """
    try:
        conn = sqlite3.connect("health_advisor.db")
        c = conn.cursor()
        c.execute("SELECT age, gender, goal, condition FROM personal_info WHERE username = ?", (username,))
        row = c.fetchone()
        if row:
            columns = [desc[0] for desc in c.description]
            return dict(zip(columns, row))
        return {}
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return {}
    finally:
        conn.close()

# ---------------------------- Streamlit App ----------------------------
st.header("🍎 Nutrition & Healthy Lifestyle Dashboard")

# ---------------------------- Step 1: Get Username ----------------------------
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.username:
    st.subheader("Enter your username")
    username_input = st.text_input("Username")
    if st.button("Continue"):
        if username_input.strip():
            st.session_state.username = username_input.strip()
        else:
            st.warning("Please enter a valid username.")
else:
    username = st.session_state.username
    st.success(f"Welcome, {username}!")

    # ---------------------------- Fetch User Data ----------------------------
    user_data = get_user_data(username)
    age = user_data.get("age", 30)
    sex = user_data.get("gender", "Other")
    goal = user_data.get("goal", "Balanced Diet")
    condition = user_data.get("condition", "None")

    # ---------------------------- Tabs ----------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "Personalized Nutrition Plan",
        "Daily Nutrition Tips",
        "Hydration & Meal Tracker",
        "Nutrition Insights"
    ])

    # ---------------------------- TAB 1: Personalized Nutrition Plan ----------------------------
    with tab1:
        st.subheader("Personalized Nutrition Recommendations")

        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=age, key="nt_age")
        with col2:
            sex = st.selectbox("Sex", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(sex), key="nt_sex")
        with col3:
            goal = st.selectbox(
                "Goal",
                ["Weight Loss", "Muscle Gain", "Balanced Diet", "Heart Health"],
                index=["Weight Loss", "Muscle Gain", "Balanced Diet", "Heart Health"].index(goal),
                key="nt_goal"
            )

        condition = st.selectbox(
            "Health Condition (Optional)",
            ["None", "Diabetes", "Hypertension", "High Cholesterol", "Anemia"],
            index=["None", "Diabetes", "Hypertension", "High Cholesterol", "Anemia"].index(condition),
            key="nt_condition"
        )

        if st.button("Get Nutrition Plan", key="nt_plan_btn"):
            query = (
                f"Provide a detailed nutrition plan for a {age}-year-old {sex} with {condition}. "
                f"The goal is {goal}. Include meal balance, nutrient focus, and portion guidance."
            )
            plan = get_nutrition_response(query)
            st.markdown("### AI Nutrition Plan")
            st.markdown(plan.replace("\n", "  \n"))  # preserve line breaks

    # ---------------------------- TAB 2: Daily Nutrition Tips ----------------------------
    with tab2:
        st.subheader("Daily Tips for Healthier Eating")

        if st.button("Get Daily Tips", key="nt_tips_btn"):
            query_tips = (
                f"Generate 3 practical daily nutrition tips for a {age}-year-old {sex} with {condition}, "
                f"aiming for {goal}. Focus on hydration, food diversity, and meal timing."
            )
            tips = get_nutrition_response(query_tips)
            st.markdown("### Daily Nutrition Tips")
            st.markdown(tips.replace("\n", "  \n"))

    # ---------------------------- TAB 3: Hydration & Meal Tracker ----------------------------
    with tab3:
        st.subheader("Hydration & Meal Tracker")
        today = str(datetime.date.today())

        if "hydration" not in st.session_state:
            st.session_state["hydration"] = {}
        if "meals_logged" not in st.session_state:
            st.session_state["meals_logged"] = {}

        water_intake = st.number_input("Water intake (cups) today:", min_value=0, max_value=30, step=1)
        if st.button("Log Hydration", key="nt_hydration_btn"):
            st.session_state["hydration"][today] = water_intake
            st.success(f"Hydration logged for {today}: {water_intake} cups")

        st.divider()
        meal = st.text_input("Describe your recent meal")
        if st.button("Log Meal", key="nt_meal_btn"):
            meals = st.session_state["meals_logged"].get(today, [])
            meals.append(meal)
            st.session_state["meals_logged"][today] = meals
            st.success("Meal logged successfully.")

        if st.checkbox("Show Today’s Logs", key="nt_show_logs"):
            st.markdown("### Today's Logs")
            st.markdown(f"**Hydration:** {st.session_state['hydration'].get(today, 'Not logged')} cups")
            st.markdown(f"**Meals:** {', '.join(st.session_state['meals_logged'].get(today, [])) if st.session_state['meals_logged'].get(today) else 'No meals logged'}")

    # ---------------------------- TAB 4: Nutrition Insights ----------------------------
    with tab4:
        st.subheader("AI-Driven Nutrition Insights")
        insights_query = st.text_area(
            "Ask a question about nutrition (e.g., 'What are good sources of protein for heart health?')",
            height=100
        )
        if st.button("Get Insight", key="nt_insight_btn"):
            if insights_query.strip():
                response = get_nutrition_response(insights_query)
                st.markdown("### AI Nutrition Insight")
                st.markdown(response.replace("\n", "  \n"))
            else:
                st.warning("Please enter a question to get insights.")
