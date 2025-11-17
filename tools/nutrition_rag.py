# tools/nutrition_rag.py
import os
import logging
from langchain.tools import BaseTool
from langchain_ibm import WatsonxEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

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

        if embeddings is None:
            embeddings = WatsonxEmbeddings(
                model_id="ibm/granite-embedding-278m-multilingual",
                url=os.getenv("WATSONX_URL"),
                project_id=os.getenv("WATSONX_PROJECT_ID"),
                apikey=os.getenv("WATSONX_APIKEY"),
            )

        persist_directory = os.path.join(this_dir, "..", "data", "chroma_store", "nutrition_guidelines")
        os.makedirs(persist_directory, exist_ok=True)
        chroma_db_path = os.path.join(persist_directory, "chroma.sqlite3")

        # Load existing vectorstore
        if os.path.exists(chroma_db_path):
            logging.info(f"Loading existing Chroma vector store from: {persist_directory}")
            vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
        else:
            logging.info(f"Creating new Chroma vector store from: {file_path}")
            loader = PyPDFLoader(file_path)
            pages = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=400,
                chunk_overlap=80,
                separators=["\n\n", "\n", ".", " "]
            )

            split_docs = text_splitter.split_documents(pages)

            vectorstore = Chroma.from_documents(
                documents=split_docs,
                embedding=embeddings,  # use embedding= when creating
                collection_name="nutrition_guidelines",
                persist_directory=persist_directory,
            )
            vectorstore.persist()

        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        class NutritionTool(BaseTool):
            name: str = "nutrition_information_retriever"
            description: str = (
                "Use this tool to answer questions about nutrition "
                "and the Dietary Guidelines for Americans (2020–2025)."
            )

            def _run(self, query: str) -> str:
                try:
                    docs = retriever.get_relevant_documents(query)
                except AttributeError:
                    try:
                        docs = retriever.retrieve(query)
                    except Exception:
                        return "Retriever is not available."

                if not docs:
                    return "No relevant information found in the Dietary Guidelines for Americans."
                return "\n\n".join([getattr(d, "page_content", str(d)) for d in docs])

            async def _arun(self, query: str) -> str:
                raise NotImplementedError("Async not implemented.")

        return NutritionTool()

    except Exception as e:
        logging.error(f"Failed to build Nutrition RAG tool: {e}")
        return None
