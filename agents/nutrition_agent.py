import logging
from helper import llm, system_prompt
from tools.nutrition_rag import build_nutrition_rag

# Initialize RAG tool
nutrition_tool = build_nutrition_rag()

# ----------------------------
# Helpers specific to nutrition
# ----------------------------
NUTRITION_KEYWORDS = [
    "nutrition", "diet", "food", "nutrient", "protein", "carbohydrate", "fat",
    "vitamin", "mineral", "fiber", "hydration", "balanced diet", "healthy eating",
    "meal plan", "micronutrients", "macronutrients", "sodium", "cholesterol",
    "sugar", "vegetables", "fruits", "whole grains", "dietary guideline"
]

def extract_nutrition_keywords(query: str) -> str:
    return " ".join([kw for kw in NUTRITION_KEYWORDS if kw.lower() in query.lower()])

def is_nutrition_query(query: str) -> bool:
    return bool(extract_nutrition_keywords(query))

# ----------------------------
# Main Nutrition response function (RAG + LLM)
# ----------------------------
def get_nutrition_response(user_input: str, language="English") -> str:
    try:
        # Language instruction
        language_prompts = {
            "English": "Respond in English.",
            "Spanish": "Responde en español.",
            "French": "Veuillez répondre en français.",
            "Deutsch": "Bitte antworte auf Deutsch."
        }
        lang_instruction = language_prompts.get(language, "Respond in English.")
        
        full_prompt = f"{system_prompt}\n{lang_instruction}\nUser: {user_input}\n"

        # ----------------------------
        # Nutrition RAG context
        # ----------------------------
        rag_context = ""
        if nutrition_tool and is_nutrition_query(user_input):
            logging.info("Routing query to Nutrition RAG...")
            keywords = extract_nutrition_keywords(user_input)
            rag_response = nutrition_tool.run(keywords)
            if rag_response.strip():
                rag_context = (
                    f"Nutrition Reference (keywords: {keywords}):\n{rag_response}\n"
                    "Use only this context for your answer.\n"
                )

        # ----------------------------
        # Add context to prompt
        # ----------------------------
        if rag_context:
            full_prompt += (
                "Use the following evidence to support your response:\n"
                f"{rag_context}"
                "\nIMPORTANT: Answer using only the provided context. "
                "Do NOT provide information outside of the retrieved references unless necessary.\n"
            )
        else:
            full_prompt += (
                "Note: No relevant document found in RAG. "
                "You may answer using general knowledge, but clearly state this.\n"
            )

        # ----------------------------
        # Generate answer with IBM Granite LLM
        # ----------------------------
        logging.info("Generating response with IBM Granite LLM...")
        result = llm.generate([full_prompt])
        answer = result.generations[0][0].text.strip()

        # Fallback if empty
        if not answer:
            logging.warning("LLM returned empty response. Using fallback prompt...")
            fallback_prompt = f"{system_prompt}\n{lang_instruction}\nUser: {user_input}"
            result = llm.generate([fallback_prompt])
            answer = result.generations[0][0].text.strip()

        return f"Assistant: {answer}"

    except Exception as e:
        logging.error(f"Error during Nutrition response: {e}")
        return "Assistant: Sorry, something went wrong. Please try again later."
