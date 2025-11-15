import streamlit as st
import sqlite3
from datetime import date

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("health_advisor.db")
    c = conn.cursor()

    # User Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY
        )
    """)

    # General health data
    c.execute("""
        CREATE TABLE IF NOT EXISTS personal_info (
            username TEXT,
            full_name TEXT,
            age INTEGER,
            gender TEXT,
            region TEXT,
            education TEXT,
            occupation TEXT,
            marital_status TEXT,
            weight REAL,
            height REAL,
            physical_activity TEXT,
            diet TEXT,
            smoking TEXT,
            alcohol TEXT,
            sleep_hours INTEGER,
            family_history TEXT,
            glucose_level REAL,
            blood_pressure REAL,
            cholesterol REAL,
            bmi REAL,
            previous_diagnosis TEXT,
            medication TEXT,
            goal TEXT,
            condition TEXT,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    # Nutrition Tracker
    c.execute("""
        CREATE TABLE IF NOT EXISTS nutrition_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            date TEXT,
            meal_type TEXT,
            food_items TEXT,
            calories REAL,
            carbs REAL,
            protein REAL,
            fat REAL,
            notes TEXT,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    # Exercise Tracker
    c.execute("""
        CREATE TABLE IF NOT EXISTS exercise_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            date TEXT,
            exercise_type TEXT,
            duration REAL,
            intensity TEXT,
            notes TEXT,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    conn.commit()
    conn.close()


# --- SAVE FUNCTIONS ---
def add_user(username):
    conn = sqlite3.connect("health_advisor.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()

def save_personal_info(username, data):
    conn = sqlite3.connect("health_advisor.db")
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO personal_info (
            username, full_name, age, gender, region, education, occupation, marital_status,
            weight, height, physical_activity, diet, smoking, alcohol, sleep_hours,
            family_history, glucose_level, blood_pressure, cholesterol, bmi,
            previous_diagnosis, medication
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        username,
        data.get("full_name"), data.get("age"), data.get("gender"), data.get("region"),
        data.get("education"), data.get("occupation"), data.get("marital_status"),
        data.get("weight"), data.get("height"), data.get("physical_activity"), data.get("diet"),
        data.get("smoking"), data.get("alcohol"), data.get("sleep_hours"),
        data.get("family_history"), data.get("glucose_level"), data.get("blood_pressure"),
        data.get("cholesterol"), data.get("bmi"), data.get("previous_diagnosis"), data.get("medication")
    ))
    conn.commit()
    conn.close()

def log_nutrition(username, meal_type, food_items, calories, notes):
    conn = sqlite3.connect("health_advisor.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO nutrition_tracker (username, date, meal_type, food_items, calories, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, str(date.today()), meal_type, food_items, calories, notes))
    conn.commit()
    conn.close()

def log_exercise(username, exercise_type, duration, intensity, notes):
    conn = sqlite3.connect("health_advisor.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO exercise_tracker (username, date, exercise_type, duration, intensity, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, str(date.today()), exercise_type, duration, intensity, notes))
    conn.commit()
    conn.close()

# --- MAIN APP ---
init_db()
st.title("Personal Health Advisor")

# --- View recent logs ---
def view_logs(username, table_name):
    conn = sqlite3.connect("health_advisor.db")
    c = conn.cursor()
    c.execute(f"SELECT date, * FROM {table_name} WHERE username=? ORDER BY date DESC LIMIT 10", (username,))
    rows = c.fetchall()
    conn.close()
    return rows

# --- Summary statistics ---
def get_summary(username):
    conn = sqlite3.connect("health_advisor.db")
    c = conn.cursor()
    c.execute("SELECT AVG(calories) FROM nutrition_tracker WHERE username=?", (username,))
    avg_cal = c.fetchone()[0]
    c.execute("SELECT SUM(duration) FROM exercise_tracker WHERE username=?", (username,))
    total_exercise = c.fetchone()[0]
    conn.close()
    return avg_cal, total_exercise or 0

# --- Step 1: Enter Username ---
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.username:
    st.subheader("Enter your Username")
    username_input = st.text_input("Username")
    if st.button("Continue"):
        if username_input.strip():
            st.session_state.username = username_input.strip()
            add_user(st.session_state.username)
            st.rerun()
        else:
            st.warning("Please enter a valid username.")
else:
    st.success(f"Welcome, {st.session_state.username}!")

    # --- Check if the user already has personal info ---
    conn = sqlite3.connect("health_advisor.db")
    c = conn.cursor()
    c.execute("SELECT * FROM personal_info WHERE username=?", (st.session_state.username,))
    existing_data = c.fetchone()
    conn.close()

    # --- Helper function for BMI ---
    def calculate_bmi(weight, height_cm):
        if height_cm <= 0:
            return 0.0
        height_m = height_cm / 100
        return round(weight / (height_m ** 2), 2)

    # --- Conditional Tabs ---
    if existing_data:
        # Existing user → show Update + Tracker
        tab1, tab2 = st.tabs(["Update Info", "Track Nutrition & Exercise"])

        # --- TAB 1: Update Info ---
        with tab1:
            st.subheader("Update Existing Information")

            # Column names
            columns = [
                "username", "full_name", "age", "gender", "region", "education", "occupation",
                "marital_status", "weight", "height", "physical_activity", "diet", "smoking",
                "alcohol", "sleep_hours", "family_history", "glucose_level", "blood_pressure",
                "cholesterol", "bmi", "previous_diagnosis", "medication"
            ]
            user_dict = dict(zip(columns, existing_data))

            st.info("Your current data is loaded. You can update any fields below.")

            full_name = st.text_input("Full Name", user_dict["full_name"])
            age = st.number_input("Age", 0, 120, int(user_dict["age"]) if user_dict["age"] else 0)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                index=["Male", "Female", "Other"].index(user_dict["gender"]) if user_dict["gender"] in ["Male", "Female", "Other"] else 0)
            region = st.text_input("Region / City", user_dict["region"] or "")
            education = st.selectbox(
                "Education Level",
                ["No formal education", "Primary", "Secondary", "College/University", "Postgraduate"],
                index=["No formal education", "Primary", "Secondary", "College/University", "Postgraduate"].index(user_dict["education"]) if user_dict["education"] else 0
            )
            occupation = st.text_input("Occupation", user_dict["occupation"] or "")
            marital_status = st.selectbox(
                "Marital Status",
                ["Single", "Married", "Divorced", "Widowed"],
                index=["Single", "Married", "Divorced", "Widowed"].index(user_dict["marital_status"]) if user_dict["marital_status"] else 0
            )

            st.write("### Health Information")
            weight = st.number_input("Weight (kg)", 0.0, 300.0, float(user_dict["weight"] or 0))
            height = st.number_input("Height (cm)", 0.0, 250.0, float(user_dict["height"] or 0))
            physical_activity = st.selectbox(
                "Physical Activity",
                ["Never", "1–2 times/week", "3–4 times/week", "Daily"],
                index=["Never", "1–2 times/week", "3–4 times/week", "Daily"].index(user_dict["physical_activity"]) if user_dict["physical_activity"] else 0
            )
            diet = st.selectbox(
                "Diet",
                ["Unhealthy", "Moderately Healthy", "Healthy"],
                index=["Unhealthy", "Moderately Healthy", "Healthy"].index(user_dict["diet"]) if user_dict["diet"] else 0
            )
            smoking = st.selectbox("Smoking", ["No", "Yes"],
                index=["No", "Yes"].index(user_dict["smoking"]) if user_dict["smoking"] else 0)
            alcohol = st.selectbox("Alcohol", ["No", "Occasionally", "Regularly"],
                index=["No", "Occasionally", "Regularly"].index(user_dict["alcohol"]) if user_dict["alcohol"] else 0)
            sleep_hours = st.number_input("Sleep Hours", 0, 24, int(user_dict["sleep_hours"] or 0))

            st.write("### Diabetes & CVD Prevention")
            family_history = st.selectbox(
                "Family History of Diabetes?", ["No", "Yes"],
                index=["No", "Yes"].index(user_dict["family_history"]) if user_dict["family_history"] else 0
            )
            glucose_level = st.number_input("Fasting Glucose (mg/dL)", 0.0, 500.0, float(user_dict["glucose_level"] or 0))
            blood_pressure = st.number_input("Blood Pressure (mmHg)", 0.0, 300.0, float(user_dict["blood_pressure"] or 0))
            cholesterol = st.number_input("Cholesterol (mg/dL)", 0.0, 500.0, float(user_dict["cholesterol"] or 0))

            bmi_value = calculate_bmi(weight, height)
            st.markdown(f"**Calculated BMI:** {bmi_value}")

            previous_diagnosis = st.selectbox(
                "Previously Diagnosed with Diabetes?", ["No", "Yes"],
                index=["No", "Yes"].index(user_dict["previous_diagnosis"]) if user_dict["previous_diagnosis"] else 0
            )
            medication = st.text_input("Current Medication", user_dict["medication"] or "")

            if st.button("Save Updates"):
                data = {
                    "full_name": full_name, "age": age, "gender": gender, "region": region,
                    "education": education, "occupation": occupation, "marital_status": marital_status,
                    "weight": weight, "height": height, "physical_activity": physical_activity,
                    "diet": diet, "smoking": smoking, "alcohol": alcohol, "sleep_hours": sleep_hours,
                    "family_history": family_history, "glucose_level": glucose_level,
                    "blood_pressure": blood_pressure, "cholesterol": cholesterol, "bmi": bmi_value,
                    "previous_diagnosis": previous_diagnosis, "medication": medication
                }
                save_personal_info(st.session_state.username, data)
                st.success("Information updated successfully!")
                st.rerun()

        # --- TAB 2: Tracker ---
        with tab2:
            st.subheader("Nutrition & Exercise Tracker")
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
            food_items = st.text_area("Food Items", key="food_items")
            calories = st.number_input("Calories", 0.0, 2000.0)
            notes_meal = st.text_area("Notes", key="notes_meal")
            if st.button("Submit Meal Log", key="submit_meal"):
                log_nutrition(st.session_state.username, meal_type, food_items, calories, notes_meal)
                st.success("Nutrition data saved!")

            st.divider()
            st.subheader("Exercise Tracker")
            exercise_type = st.text_input("Exercise Type", key="exercise_type")
            duration = st.number_input("Duration (minutes)", 0.0, 300.0)
            intensity = st.selectbox("Intensity", ["Low", "Moderate", "High"], key="intensity")
            notes_exercise = st.text_area("Notes", key="notes_exercise")
            if st.button("Submit Exercise Log", key="submit_exercise"):
                log_exercise(st.session_state.username, exercise_type, duration, intensity, notes_exercise)
                st.success("Exercise data saved!")

    else:
        # New user → show New Info + Tracker
        tab1, tab2 = st.tabs(["New Personal Info", "Track Nutrition & Exercise"])

        # --- TAB 1: New Info ---
        with tab1:
            st.subheader("Enter Personal and Health Information")
            full_name = st.text_input("Full Name")
            age = st.number_input("Age", 0, 120)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            region = st.text_input("Region / City")
            education = st.selectbox("Education Level", ["No formal education", "Primary", "Secondary", "College/University", "Postgraduate"])
            occupation = st.text_input("Occupation")
            marital_status = st.selectbox("Marital Status", ["Single", "Married", "Divorced", "Widowed"])

            st.write("### Health Information")
            weight = st.number_input("Weight (kg)", 0.0, 300.0)
            height = st.number_input("Height (cm)", 0.0, 250.0)
            physical_activity = st.selectbox("Physical Activity", ["Never", "1–2 times/week", "3–4 times/week", "Daily"])
            diet = st.selectbox("Diet", ["Unhealthy", "Moderately Healthy", "Healthy"])
            smoking = st.selectbox("Smoking", ["No", "Yes"])
            alcohol = st.selectbox("Alcohol", ["No", "Occasionally", "Regularly"])
            sleep_hours = st.number_input("Sleep Hours", 0, 24)

            st.write("### Diabetes & CVD Prevention")
            family_history = st.selectbox("Family History of Diabetes?", ["No", "Yes"])
            glucose_level = st.number_input("Fasting Glucose (mg/dL)", 0.0, 500.0)
            blood_pressure = st.number_input("Blood Pressure (mmHg)", 0.0, 300.0)
            cholesterol = st.number_input("Cholesterol (mg/dL)", 0.0, 500.0)
            bmi_value = calculate_bmi(weight, height)
            st.markdown(f"**Calculated BMI:** {bmi_value}")
            previous_diagnosis = st.selectbox("Previously Diagnosed with Diabetes?", ["No", "Yes"])
            medication = st.text_input("Current Medication")

            if st.button("Submit New Info"):
                data = {
                    "full_name": full_name, "age": age, "gender": gender, "region": region,
                    "education": education, "occupation": occupation, "marital_status": marital_status,
                    "weight": weight, "height": height, "physical_activity": physical_activity,
                    "diet": diet, "smoking": smoking, "alcohol": alcohol, "sleep_hours": sleep_hours,
                    "family_history": family_history, "glucose_level": glucose_level,
                    "blood_pressure": blood_pressure, "cholesterol": cholesterol, "bmi": bmi_value,
                    "previous_diagnosis": previous_diagnosis, "medication": medication
                }
                save_personal_info(st.session_state.username, data)
                st.success("Personal information saved successfully!")
                st.rerun()

        # --- TAB 2: Tracker ---
        with tab2:
            st.subheader("Nutrition & Exercise Tracker")
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
            food_items = st.text_area("Food Items", key="food_items_new")
            calories = st.number_input("Calories", 0.0, 2000.0)
            notes_meal = st.text_area("Notes", key="notes_meal_new")
            if st.button("Submit Meal Log", key="submit_meal_new"):
                log_nutrition(st.session_state.username, meal_type, food_items, calories, notes_meal)
                st.success("Nutrition data saved!")

            st.divider()
            st.subheader("Exercise Tracker")
            exercise_type = st.text_input("Exercise Type", key="exercise_type_new")
            duration = st.number_input("Duration (minutes)", 0.0, 300.0)
            intensity = st.selectbox("Intensity", ["Low", "Moderate", "High"], key="intensity_new")
            notes_exercise = st.text_area("Notes", key="notes_exercise_new")

            # --- Show summary metrics ---
            avg_cal, total_ex = get_summary(st.session_state.username)
            st.metric("Average Daily Calories", f"{avg_cal:.1f}" if avg_cal else "No data")
            st.metric("Total Exercise (min)", f"{total_ex}")

            # --- Optional: show logs ---
            if st.checkbox("Show My Recent Logs"):
                st.write("### Nutrition Logs")
                st.dataframe(view_logs(st.session_state.username, "nutrition_tracker"))
                st.write("### Exercise Logs")
                st.dataframe(view_logs(st.session_state.username, "exercise_tracker"))
            if st.button("Submit Exercise Log", key="submit_exercise_new"):
                log_exercise(st.session_state.username, exercise_type, duration, intensity, notes_exercise)
                st.success("Exercise data saved!")
