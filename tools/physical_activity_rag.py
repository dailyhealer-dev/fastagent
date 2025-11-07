import os
import logging
from langchain.tools import Tool
from langchain_ibm import WatsonxEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def build_physical_activity_rag(embeddings=None):
    """
    Build a Physical Activity Retrieval Tool using a Chroma vector store.
    Loads Physical Activity Guidelines (2nd Edition) PDF and returns a LangChain Tool.
    """
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(this_dir, "..", "data", "Physical_Activity_Guidelines_2nd_edition.pdf")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Physical Activity PDF not found: {file_path}")

        # Initialize embeddings if not passed
        if embeddings is None:
            embeddings = WatsonxEmbeddings(
                model_id="ibm/granite-embedding-107m-multilingual",
                url=os.getenv("WATSONX_URL"),
                project_id=os.getenv("WATSONX_PROJECT_ID"),
                apikey=os.getenv("WATSONX_APIKEY")
            )

        # Directory to persist Chroma DB
        persist_directory = os.path.join(this_dir, "..", "data", "chroma_store", "physical_activity_guidelines")
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

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
            split_docs = text_splitter.split_documents(pages)

            # Create new Chroma vector store
            vectorstore = Chroma.from_documents(
                documents=split_docs,
                embedding=embeddings,
                collection_name="physical_activity_guidelines",
                persist_directory=persist_directory
            )
            vectorstore.persist()

        # Create retriever with Top K = 3
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

        # Retrieval function
        def retrieve_physical_activity_info(query: str) -> str:
            docs = retriever.invoke(query)
            if not docs:
                return "No relevant information found in the Physical Activity Guidelines."
            return "\n\n".join([d.page_content for d in docs])

        # Return as LangChain Tool
        return Tool(
            name="Physical Activity Information Retriever",
            func=retrieve_physical_activity_info,
            description="Use this tool to answer questions about physical activity and exercise guidelines."
        )

    except Exception as e:
        logging.error(f"Failed to build Physical Activity RAG tool: {e}")
        return None
