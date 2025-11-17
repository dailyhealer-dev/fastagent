# tools/physical_activity_rag.py
import os
import logging
from langchain.tools import BaseTool
from langchain_ibm import WatsonxEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def build_physical_activity_rag(embeddings=None):
    """
    Build a Physical Activity Retrieval Tool using a Chroma vector store.
    Loads Physical Activity Guidelines PDF and returns a LangChain Tool.
    """
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(this_dir, "..", "data", "Physical_Activity_Guidelines_2nd_edition.pdf")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Physical Activity PDF not found: {file_path}")

        if embeddings is None:
            embeddings = WatsonxEmbeddings(
                model_id="ibm/granite-embedding-278m-multilingual",
                url=os.getenv("WATSONX_URL"),
                project_id=os.getenv("WATSONX_PROJECT_ID"),
                apikey=os.getenv("WATSONX_APIKEY"),
            )

        persist_directory = os.path.join(this_dir, "..", "data", "chroma_store", "physical_activity_guidelines")
        os.makedirs(persist_directory, exist_ok=True)
        chroma_db_path = os.path.join(persist_directory, "chroma.sqlite3")

        # Load existing vectorstore
        if os.path.exists(chroma_db_path):
            logging.info(f"Loading existing Chroma vector store from: {persist_directory}")
            vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings  # use embedding_function only when loading
            )
        else:
            logging.info("Creating new Chroma vector store from PDF...")
            loader = PyPDFLoader(file_path)
            pages = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
            split_docs = text_splitter.split_documents(pages)

            # Use `embedding=` only when creating from documents
            vectorstore = Chroma.from_documents(
                documents=split_docs,
                embedding=embeddings,  # CORRECTED here
                collection_name="physical_activity_guidelines",
                persist_directory=persist_directory,
            )
            vectorstore.persist()

        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

        class PhysicalActivityTool(BaseTool):
            name: str = "physical_activity_information_retriever"
            description: str = "Use this tool to answer questions about physical activity and exercise guidelines."

            def _run(self, query: str) -> str:
                try:
                    docs = retriever.get_relevant_documents(query)
                except AttributeError:
                    try:
                        docs = retriever.retrieve(query)
                    except Exception:
                        return "Retriever is not available."

                if not docs:
                    return "No relevant information found in the Physical Activity Guidelines."
                return "\n\n".join([getattr(d, "page_content", str(d)) for d in docs])

            async def _arun(self, query: str) -> str:
                raise NotImplementedError("Async not implemented.")

        return PhysicalActivityTool()

    except Exception as e:
        logging.error(f"Failed to build Physical Activity RAG tool: {e}")
        return None
