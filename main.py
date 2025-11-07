from dotenv import load_dotenv
import os
import logging
from langchain_ibm import WatsonxLLM
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
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
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

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
# Initialize main agent
# ----------------------------
tools_list = [medical_info_tool]
if physical_activity_tool:
    tools_list.append(physical_activity_tool)

agent = initialize_agent(
    tools=tools_list,
    llm=llm,
    agent_type="zero-shot-react-description",
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)

logging.basicConfig(level=logging.INFO)


def is_general_health_query(query: str) -> bool:
    general_keywords = [
        "lifestyle", "sleep", "hydration", "stress", "mental health", "wellness"
    ]
    return any(keyword.lower() in query.lower() for keyword in general_keywords)

# ----------------------------
# Improved Helper: Extract physical activity keywords
# ----------------------------
def extract_physical_keywords(query: str) -> str:
    # Expanded keyword list
    physical_keywords = [
        "exercise", "physical activity", "fitness", "workout", "aerobic",
        "strength", "endurance", "cardio", "movement", "sports", "training",
        "walking", "running", "yoga", "stretching", "cycling", "swimming", "resistance"
    ]
    # Return all keywords found in query
    keywords_found = [kw for kw in physical_keywords if kw.lower() in query.lower()]
    return " ".join(keywords_found)

# ----------------------------
# Check if query is related to physical activity
# ----------------------------
def is_physical_activity_query(query: str) -> bool:
    return bool(extract_physical_keywords(query))

# ----------------------------
# Main response function with chunk-aware RAG
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

        full_prompt = f"{system_prompt}\n{lang_instruction}\nUser: {user_input}\n"

        # ----------------------------
        # Step 1: Physical Activity RAG (keyword-based)
        # ----------------------------
        rag_context = ""
        if physical_activity_tool and is_physical_activity_query(user_input):
            logging.info("Fetching Physical Activity info from RAG...")
            keywords_for_rag = extract_physical_keywords(user_input)
            if keywords_for_rag:
                rag_response = physical_activity_tool.run(keywords_for_rag)
                if rag_response.strip():
                    # Optional: Include chunk ID or source info
                    rag_context = (
                        f"Physical Activity Reference (keywords: {keywords_for_rag}):\n"
                        f"{rag_response}\n"
                        "Reference each piece of info from the retrieved document.\n"
                    )

        # ----------------------------
        # Step 2: PubMed context
        # ----------------------------
        pubmed_context = ""
        logging.info("Fetching PubMed info...")
        pubmed_response = medical_info_tool.run(user_input)
        if pubmed_response.strip():
            pubmed_context = f"PubMed Reference:\n{pubmed_response}\n"

        # ----------------------------
        # Step 3: Combine context and instruct LLM
        # ----------------------------
        if rag_context or pubmed_context:
            context_text = "Use the following evidence to support your response if relevant:\n"
            context_text += rag_context + pubmed_context
            context_text += (
                "\nIMPORTANT: Answer using only the provided context. "
                "Do NOT provide information outside of the retrieved references unless necessary. "
                "Clearly indicate if you are using fallback knowledge.\n"
            )
            full_prompt += context_text
        else:
            full_prompt += (
                "Note: No relevant document found in RAG or PubMed. "
                "You may answer using your general knowledge, but clearly state this.\n"
            )

        # ----------------------------
        # Step 4: Generate answer with IBM Granite LLM
        # ----------------------------
        logging.info("Generating response with IBM Granite LLM...")
        result = llm.generate([full_prompt])
        answer = result.generations[0][0].text

        # Safety fallback if empty
        if not answer.strip():
            logging.warning("LLM returned empty response, generating fallback answer...")
            fallback_prompt = f"{system_prompt}\n{lang_instruction}\nUser: {user_input}"
            result = llm.generate([fallback_prompt])
            answer = result.generations[0][0].text

        return f"Assistant: {answer}"

    except Exception as e:
        logging.error(f"Error during AI response: {e}")
        return "Assistant: Sorry, something went wrong. Please try again later."
