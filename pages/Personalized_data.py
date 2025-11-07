import streamlit as st

# --- App Title ---
st.title("Diabetic Prevention Data Collection Form")

# --- Personal & Sociodemographic Information ---
@st.fragment
def personal_info_form():
    st.subheader("Personal & Sociodemographic Information")
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    region = st.text_input("Region / City")
    education = st.selectbox(
        "Education Level",
        ["No formal education", "Primary", "Secondary", "College/University", "Postgraduate"]
    )
    occupation = st.text_input("Occupation")
    marital_status = st.selectbox("Marital Status", ["Single", "Married", "Divorced", "Widowed"])

    return {
        "name": name,
        "age": age,
        "gender": gender,
        "region": region,
        "education": education,
        "occupation": occupation,
        "marital_status": marital_status,
    }

# --- Health-Related Information ---
@st.fragment
def health_info_form():
    st.subheader("Health-Related Information")
    weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, step=0.1)
    height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, step=0.1)
    physical_activity = st.selectbox(
        "How often do you engage in physical activity?",
        ["Never", "1–2 times/week", "3–4 times/week", "Daily"]
    )
    diet = st.selectbox(
        "Dietary Habits",
        ["Unhealthy", "Moderately Healthy", "Healthy"]
    )
    smoking = st.selectbox("Do you smoke?", ["No", "Yes"])
    alcohol = st.selectbox("Do you drink alcohol?", ["No", "Occasionally", "Regularly"])
    sleep_hours = st.number_input("Average Sleep Hours per Night", min_value=0, max_value=24, step=1)

    return {
        "weight": weight,
        "height": height,
        "physical_activity": physical_activity,
        "diet": diet,
        "smoking": smoking,
        "alcohol": alcohol,
        "sleep_hours": sleep_hours,
    }

# --- Diabetes-Related Information ---
@st.fragment
def diabetes_info_form():
    st.subheader("Diabetes-Related Information")
    family_history = st.selectbox("Family History of Diabetes?", ["No", "Yes"])
    glucose_level = st.number_input("Fasting Blood Glucose Level (mg/dL)", min_value=0.0, step=0.1)
    blood_pressure = st.number_input("Average Blood Pressure (mmHg)", min_value=0.0, step=0.1)
    cholesterol = st.number_input("Cholesterol Level (mg/dL)", min_value=0.0, step=0.1)
    bmi = st.number_input("BMI (if known)", min_value=0.0, step=0.1)
    previous_diagnosis = st.selectbox("Previously Diagnosed with Diabetes?", ["No", "Yes"])
    medication = st.text_input("Current Medication (if any)")

    return {
        "family_history": family_history,
        "glucose_level": glucose_level,
        "blood_pressure": blood_pressure,
        "cholesterol": cholesterol,
        "bmi": bmi,
        "previous_diagnosis": previous_diagnosis,
        "medication": medication,
    }

# --- Main Form Context Manager ---
with st.form("diabetes_prevention_form"):
    st.write("Please fill in your information below. Your data will help our AI agent assess diabetic risk factors and provide prevention insights.")

    personal_data = personal_info_form()
    health_data = health_info_form()
    diabetic_data = diabetes_info_form()

    submitted = st.form_submit_button("Submit")

    if submitted:
        st.success("Your information has been submitted successfully!")
        st.write("### Summary of Collected Data:")
        all_data = {
            "personal_info": personal_data,
            "health_info": health_data,
            "diabetic_info": diabetic_data
        }
        st.json(all_data)
