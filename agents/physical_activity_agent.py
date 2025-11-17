# agents/physical_activity_agent.py
import logging
from helper import llm, system_prompt
from tools.physical_activity_rag import build_physical_activity_rag

# Initialize RAG tool
physical_activity_tool = build_physical_activity_rag()

# ----------------------------
# Helpers specific to physical activity
# ----------------------------
def extract_physical_keywords(query: str) -> str:
    physical_keywords = [
        "exercise", "physical activity", "fitness", "workout", "aerobic",
        "strength", "endurance", "cardio", "movement", "sports", "training",
        "walking", "running", "yoga", "stretching", "cycling", "swimming", "resistance"
    ]
    keywords_found = [kw for kw in physical_keywords if kw.lower() in query.lower()]
    return " ".join(keywords_found)

def is_physical_activity_query(query: str) -> bool:
    return bool(extract_physical_keywords(query))

# ----------------------------
# Main Physical Activity response function (RAG-only)
# ----------------------------
def get_physical_activity_response(user_input: str, language="English") -> str:
    try:
        language_prompts = {
            "English": "Respond in English.",
            "Spanish": "Responde en español.",
            "French": "Veuillez répondre en français.",
            "Deutsch": "Bitte antworte auf Deutsch."
        }
        lang_instruction = language_prompts.get(language, "Please respond in English.")

        full_prompt = f"{system_prompt}\n{lang_instruction}\nUser: {user_input}\n"

        # Physical Activity RAG (keyword-based)
        rag_context = ""
        if physical_activity_tool and is_physical_activity_query(user_input):
            logging.info("Fetching Physical Activity info from RAG...")
            keywords_for_rag = extract_physical_keywords(user_input)
            if keywords_for_rag:
                rag_response = physical_activity_tool.run(keywords_for_rag)
                if rag_response.strip():
                    rag_context = (
                        f"Physical Activity Reference (keywords: {keywords_for_rag}):\n"
                        f"{rag_response}\n"
                        "Reference each piece of info from the retrieved document.\n"
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
                "You may answer using your general knowledge, but clearly state this.\n"
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
        logging.error(f"Error during Physical Activity response: {e}")
        return "Assistant: Sorry, something went wrong. Please try again later."
