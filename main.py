from dotenv import load_dotenv
import os
import logging
from langchain_ibm import WatsonxLLM
from langchain.agents import create_agent
# from langchain.memory.buffer import ConversationBufferMemory
from tools.pubmed_retriever import medical_info_tool
from tools.physical_activity_rag import build_physical_activity_rag

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
# Build the Physical Activity tool
# ----------------------------
physical_activity_tool = build_physical_activity_rag()
if physical_activity_tool is None:
    logging.warning("Physical Activity tool failed to initialize. It will fallback to LLM.")

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
# Initialize main agent using create_agent
# ----------------------------
tools_list = [medical_info_tool]
if physical_activity_tool:
    tools_list.append(physical_activity_tool)

agent = create_agent(
    llm,              # Your Watsonx Granite LLM
    tools=tools_list,
    system_prompt=system_prompt,
    verbose=True
)

logging.basicConfig(level=logging.INFO)

# ----------------------------
# Helper functions
# ----------------------------
def is_general_health_query(query: str) -> bool:
    general_keywords = [
        "lifestyle", "sleep", "hydration", "stress", "mental health", "wellness"
    ]
    return any(keyword.lower() in query.lower() for keyword in general_keywords)

def extract_physical_keywords(query: str) -> str:
    physical_keywords = [
        "exercise", "physical activity", "fitness", "workout", "aerobic",
        "strength", "endurance", "cardio", "movement", "sports", "training",
        "walking", "running", "yoga", "stretching", "cycling", "swimming", "resistance"
    ]
    return " ".join(kw for kw in physical_keywords if kw.lower() in query.lower())

def is_physical_activity_query(query: str) -> bool:
    return bool(extract_physical_keywords(query))

# ----------------------------
# Main response function with RAG
# ----------------------------
def get_response(user_input: str, language="English") -> str:
    try:
        language_prompts = {
            "English": "Respond in English.",
            "Spanish": "Responde en español.",
            "French": "Veuillez répondre en français.",
            "Deutsch": "Bitte antworte auf Deutsch."
        }
        lang_instruction = language_prompts.get(language, "Please respond in English.")

        # Step 1: Physical Activity RAG
        rag_context = ""
        if physical_activity_tool and is_physical_activity_query(user_input):
            logging.info("Fetching Physical Activity info from RAG...")
            keywords = extract_physical_keywords(user_input)
            if keywords:
                rag_response = physical_activity_tool.run(keywords)
                if rag_response.strip():
                    rag_context = f"Physical Activity Reference (keywords: {keywords}):\n{rag_response}\n"

        # Step 2: PubMed context
        pubmed_context = ""
        logging.info("Fetching PubMed info...")
        pubmed_response = medical_info_tool.run(user_input)
        if pubmed_response.strip():
            pubmed_context = f"PubMed Reference:\n{pubmed_response}\n"

        # Step 3: Combine context
        context_text = ""
        if rag_context or pubmed_context:
            context_text = "Use the following evidence to support your response if relevant:\n"
            context_text += rag_context + pubmed_context
            context_text += (
                "\nIMPORTANT: Answer using only the provided context. "
                "Do NOT provide information outside of the retrieved references unless necessary. "
                "Clearly indicate if you are using fallback knowledge.\n"
            )

        final_input = f"{lang_instruction}\nUser: {user_input}\n{context_text}"

        # Step 4: Generate answer
        result = agent.invoke({"input": final_input})
        return f"Assistant: {result['output']}"

    except Exception as e:
        logging.error(f"Error during AI response: {e}")
        return "Assistant: Sorry, something went wrong. Please try again later."
