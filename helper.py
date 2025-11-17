# helper.py
from dotenv import load_dotenv
import os
import logging
from langchain_ibm import WatsonxLLM
# from langchain.memory import ConversationBufferMemory

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
# Conversation memory
# ----------------------------
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# ----------------------------
# System instruction / prompt
# ----------------------------
system_prompt = """
You are a Personal Health Advisor AI.
Answer only health-related questions.
Use IBM foundation model as fallback if other tools haven't relevant information.
Always provide citations (PubMed or reliable sources) when possible.
If the user asks something unrelated to health, respond politely:
"I am a personal health advisor. Please ask questions related to health, wellness, or lifestyle."
Do NOT provide medical diagnoses; always encourage consulting a professional if needed.
Use the conversation history to maintain context.
Always provide evidence-based responses supported by reliable citations.
Use the designated knowledge source whenever available to ensure factual accuracy.
Never provide a medical diagnosis or treatment plan.
Always recommend consulting a licensed physician for health concerns.
Focus on prevention, lifestyle improvement, and educational guidance only.
Clearly state limitations when responding to medical or uncertain questions.
Prioritize user safety and accuracy in all health-related content.
Maintain user privacy and handle all data securely.
Reference credible public health authorities such as WHO or CDC.
Communicate in a respectful, clear, and supportive manner.
"""

# ----------------------------
# Logging config
# ----------------------------
logging.basicConfig(level=logging.INFO)
