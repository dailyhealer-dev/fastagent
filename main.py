# main.py
from dotenv import load_dotenv
import os
import logging
from langchain_ibm import WatsonxLLM
from langchain.agents import create_agent
from langchain.tools import BaseTool
from tools.pubmed_retriever import medical_info_tool
from tools.physical_activity_rag import build_physical_activity_rag
from tools.nutrition_rag import build_nutrition_rag

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
api_key = os.getenv("WATSONX_APIKEY")
url = os.getenv("WATSONX_URL")
project_id = os.getenv("WATSONX_PROJECT_ID")

# ----------------------------
# Initialize Watsonx Granite LLM
# ----------------------------
llm = WatsonxLLM(
    model_id="ibm/granite-3-8b-instruct",
    url=url,
    project_id=project_id,
    apikey=api_key,
    params={
        "decoding_method": "greedy",
        "temperature": 0.7,
        "min_new_tokens": 5,
        "max_new_tokens": 400,
        "repetition_penalty": 1.2
    }
)

# ----------------------------
# Build RAG Tools
# ----------------------------
physical_activity_tool = build_physical_activity_rag()
if physical_activity_tool is None:
    logging.warning("Physical Activity tool failed to initialize. Will fallback to LLM.")

nutrition_tool = build_nutrition_rag()
if nutrition_tool is None:
    logging.warning("Nutrition tool failed to initialize. Will fallback to LLM.")

# ----------------------------
# Logging setup
# ----------------------------
logging.basicConfig(level=logging.INFO)

# ----------------------------
# Helper functions for routing
# ----------------------------
PHYSICAL_KEYWORDS = [
    "exercise", "physical activity", "fitness", "workout", "aerobic",
    "strength", "endurance", "cardio", "movement", "sports", "training",
    "walking", "running", "yoga", "stretching", "cycling", "swimming", "resistance"
]

NUTRITION_KEYWORDS = [
    "nutrition", "diet", "food", "nutrient", "protein", "carbohydrate", "fat",
    "vitamin", "mineral", "fiber", "hydration", "balanced diet", "healthy eating",
    "meal plan", "micronutrients", "macronutrients", "sodium", "cholesterol",
    "sugar", "vegetables", "fruits", "whole grains", "dietary guideline"
]

GENERAL_HEALTH_KEYWORDS = [
    "lifestyle", "sleep", "hydration", "stress", "mental health", "wellness"
]

def is_physical_activity_query(query: str) -> bool:
    return any(kw.lower() in query.lower() for kw in PHYSICAL_KEYWORDS)

def is_nutrition_query(query: str) -> bool:
    return any(kw.lower() in query.lower() for kw in NUTRITION_KEYWORDS)

def is_general_health_query(query: str) -> bool:
    return any(kw.lower() in query.lower() for kw in GENERAL_HEALTH_KEYWORDS)

# ----------------------------
# Multi-Agent Tools
# ----------------------------
tools_list = []

# Physical Activity Agent
if physical_activity_tool:
    class PhysicalActivityAgent(BaseTool):
        name: str = "PhysicalActivityAgent"
        description: str = "Answers questions specifically about physical activity and exercise."

        def _run(self, query: str) -> str:
            try:
                return physical_activity_tool.run(query)
            except Exception as e:
                logging.error(f"Physical Activity sub-agent failed: {e}")
                return "Physical Activity info not available."

        async def _arun(self, query: str) -> str:
            raise NotImplementedError("Async not implemented.")

    physical_activity_agent = PhysicalActivityAgent()
    tools_list.append(physical_activity_agent)

# Nutrition Agent
if nutrition_tool:
    class NutritionAgent(BaseTool):
        name: str = "NutritionAgent"
        description: str = "Answers questions specifically about nutrition and dietary guidelines."

        def _run(self, query: str) -> str:
            try:
                return nutrition_tool.run(query)
            except Exception as e:
                logging.error(f"Nutrition sub-agent failed: {e}")
                return "Nutrition info not available."

        async def _arun(self, query: str) -> str:
            raise NotImplementedError("Async not implemented.")

    nutrition_agent = NutritionAgent()
    tools_list.append(nutrition_agent)

# PubMed Agent
class PubMedAgent(BaseTool):
    name: str = "PubMedAgent"
    description: str = "Searches PubMed for abstracts and returns plain text summaries."

    def _run(self, query: str) -> str:
        try:
            return medical_info_tool.run(query)
        except Exception as e:
            logging.error(f"PubMed sub-agent failed: {e}")
            return "PubMed info not available."

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("Async not implemented.")

pubmed_agent = PubMedAgent()
tools_list.append(pubmed_agent)

# ----------------------------
# System Prompt
# ----------------------------
system_prompt = """
You are a Personal Health Advisor AI.
Answer only health-related questions.
Use IBM foundation model as fallback if other tools haven't relevant information.
Always provide citations (PubMed or reliable sources) when possible.

FORMAT INSTRUCTIONS:
- Use **Markdown formatting** for clarity.
- Use bullet points (- or •) for listing items.
- Use **bold** for key health terms or warnings.
- Use *italics* for subtle emphasis.
- Use block quotes (>) for expert advice or disclaimers.
- Use numbered lists when giving step-by-step guidance.
- Provide URLs or citations as [text](link) when possible.
- Do not use HTML tags.

BEHAVIOR INSTRUCTIONS:
If the user asks something unrelated to health, respond politely:
> I am a personal health advisor. Please ask questions related to health, wellness, or lifestyle.

Do NOT provide medical diagnoses; always encourage consulting a professional if needed.
Always provide evidence-based responses supported by reliable citations.
Focus on prevention, lifestyle improvement, and educational guidance only.
"""

# ----------------------------
# Initialize Main Agent (Multi-Agent)
# ----------------------------
multi_agent = None
try:
    multi_agent = create_agent(
        llm,
        tools=tools_list,
        system_prompt=system_prompt
    )
    logging.info("Multi-agent initialized successfully.")
except Exception as e:
    logging.error(f"Multi-agent initialization failed: {e}")
    multi_agent = None

# ----------------------------
# Main Response Function
# ----------------------------
def get_response(user_input: str, language="English") -> str:
    try:
        language_prompts = {
            "English": "Respond in English.",
            "Spanish": "Responde en español.",
            "French": "Veuillez répondre en français.",
            "Deutsch": "Bitte antworte auf Deutsch."
        }
        lang_instruction = language_prompts.get(language, "Respond in English.")

        # Routing
        if is_physical_activity_query(user_input) and physical_activity_tool:
            logging.info("Routing to Physical Activity Agent")
            return f"Assistant: {physical_activity_agent._run(user_input)}"

        if is_nutrition_query(user_input) and nutrition_tool:
            logging.info("Routing to Nutrition Agent")
            return f"Assistant: {nutrition_agent._run(user_input)}"

        if is_general_health_query(user_input):
            logging.info("Routing to PubMed Agent")
            return f"Assistant: {pubmed_agent._run(user_input)}"

        # Otherwise, use multi-agent
        if multi_agent:
            final_input = f"{lang_instruction}\nUser: {user_input}"
            try:
                result = multi_agent.invoke({"input": final_input})
                return f"Assistant: {result.get('output') if isinstance(result, dict) else str(result)}"
            except Exception as ae:
                logging.error(f"Multi-agent invocation failed: {ae}")

        # Fallback to LLM
        final_input = f"{lang_instruction}\nUser: {user_input}"
        try:
            logging.info("Falling back to LLM.generate()")
            llm_result = llm.generate([final_input])
            answer = llm_result.generations[0][0].text
            return f"Assistant: {answer}"
        except Exception as e:
            logging.error(f"LLM fallback failed: {e}")
            return "Assistant: Sorry, something went wrong. Please try again later."

    except Exception as e:
        logging.error(f"Unexpected error in get_response: {e}")
        return "Assistant: Sorry, something went wrong. Please try again later."
