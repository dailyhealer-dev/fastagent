import os
import logging
from langchain.tools import Tool
from langchain_ibm import WatsonxEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def build_nutrition_rag(embeddings=None):
    """
    Build a Nutrition Retrieval Tool using a Chroma vector store.
    Loads the Dietary Guidelines for Americans 2020–2025 PDF and returns a LangChain Tool.
    """
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(this_dir, "..", "data", "Dietary_Guidelines_for_Americans_2020-2025.pdf")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Nutrition PDF not found: {file_path}")

        # Initialize embeddings if not passed
        if embeddings is None:
            embeddings = WatsonxEmbeddings(
                model_id="ibm/granite-embedding-107m-multilingual",
                url=os.getenv("WATSONX_URL"),
                project_id=os.getenv("WATSONX_PROJECT_ID"),
                apikey=os.getenv("WATSONX_APIKEY")
            )

        # Directory to persist Chroma DB
        persist_directory = os.path.join(this_dir, "..", "data", "chroma_store", "nutrition_guidelines")
        os.makedirs(persist_directory, exist_ok=True)

        # If Chroma DB already exists, load it
        if os.path.exists(os.path.join(persist_directory, "chroma.sqlite3")):
            logging.info(f"Loading existing Chroma vector store from: {persist_directory}")
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        else:
            logging.info(f"Creating new Chroma vector store from PDF: {file_path}")

            # Load and split PDF
            loader = PyPDFLoader(file_path)
            pages = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=400,
                chunk_overlap=80,
                separators=["\n\n", "\n", ".", " "]
            )
            split_docs = text_splitter.split_documents(pages)

            # Create new Chroma vector store
            vectorstore = Chroma.from_documents(
                documents=split_docs,
                embedding=embeddings,
                collection_name="nutrition_guidelines",
                persist_directory=persist_directory
            )
            vectorstore.persist()

        # Create retriever
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

        # Retrieval function
        def retrieve_nutrition_info(query: str) -> str:
            docs = retriever.invoke(query)
            if not docs:
                return "No relevant information found in the Dietary Guidelines for Americans (2020–2025)."
            return "\n\n".join([d.page_content for d in docs])

        # Return LangChain Tool
        return Tool(
            name="Nutrition Information Retriever",
            func=retrieve_nutrition_info,
            description="Use this tool to answer questions about nutrition and dietary guidelines."
        )

    except Exception as e:
        logging.error(f"Failed to build Nutrition RAG tool: {e}")
        return None
