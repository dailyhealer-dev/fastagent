import logging
from helper import llm, memory, system_prompt
from tools.nutrition_rag import build_nutrition_rag

# Initialize RAG tool
nutrition_tool = build_nutrition_rag()

# ----------------------------
# Helpers specific to nutrition
# ----------------------------
def extract_nutrition_keywords(query: str) -> str:
    nutrition_keywords = [
        "nutrition", "diet", "food", "nutrient", "protein", "carbohydrate", "fat", 
        "vitamin", "mineral", "fiber", "hydration", "balanced diet", "healthy eating",
        "meal plan", "micronutrients", "macronutrients", "sodium", "cholesterol",
        "sugar", "vegetables", "fruits", "whole grains", "dietary guideline"
    ]
    keywords_found = [kw for kw in nutrition_keywords if kw.lower() in query.lower()]
    return " ".join(keywords_found)

def is_nutrition_query(query: str) -> bool:
    return bool(extract_nutrition_keywords(query))

# ----------------------------
# Main Nutrition response function (RAG-only)
# ----------------------------
def get_nutrition_response(user_input: str, language="English") -> str:
    try:
        language_prompts = {
            "English": "Respond in English.",
            "Spanish": "Responde en español.",
            "French": "Veuillez répondre en français.",
            "Deutsch": "Bitte antworte auf Deutsch."
        }
        lang_instruction = language_prompts.get(language, "Please respond in English.")

        full_prompt = f"{system_prompt}\n{lang_instruction}\nUser: {user_input}\n"

        # Nutrition RAG
        rag_context = ""
        if nutrition_tool and is_nutrition_query(user_input):
            logging.info("Fetching Nutrition info from RAG...")
            keywords_for_rag = extract_nutrition_keywords(user_input)
            if keywords_for_rag:
                rag_response = nutrition_tool.run(keywords_for_rag)
                if rag_response.strip():
                    rag_context = (
                        f"Nutrition Reference (keywords: {keywords_for_rag}):\n"
                        f"{rag_response}\n"
                        "Use only this context for your answer.\n"
                    )

        # Combine context
        if rag_context:
            context_text = "Use the following evidence to support your response:\n"
            context_text += rag_context
            context_text += (
                "\nIMPORTANT: Answer using only the provided context. "
                "Do NOT provide information outside of the retrieved references unless necessary.\n"
            )
            full_prompt += context_text
        else:
            full_prompt += (
                "Note: No relevant document found in RAG. "
                "You may answer using general knowledge, but clearly state this.\n"
            )

        # Generate answer with IBM Granite LLM
        logging.info("Generating response with IBM Granite LLM...")
        result = llm.generate([full_prompt])
        answer = result.generations[0][0].text

        # Fallback safety
        if not answer.strip():
            logging.warning("LLM returned empty response, generating fallback answer...")
            fallback_prompt = f"{system_prompt}\n{lang_instruction}\nUser: {user_input}"
            result = llm.generate([fallback_prompt])
            answer = result.generations[0][0].text

        return f"Assistant: {answer}"

    except Exception as e:
        logging.error(f"Error during Nutrition response: {e}")
        return "Assistant: Sorry, something went wrong. Please try again later."
