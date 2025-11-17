# tools/vector_builder.py
import os
import logging
from langchain_ibm import WatsonxEmbeddings
from langchain_chroma import Chroma
from langchain_textsplitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def create_vector_store(file_path: str, collection_name: str, embeddings=None):
    """
    Create a Chroma vector store from a text file using provided embeddings.
    """
    try:
        if embeddings is None:
            embeddings = WatsonxEmbeddings(
                model_id="ibm/granite-embedding-278m-multilingual",
                url=os.getenv("WATSONX_URL"),
                project_id=os.getenv("WATSONX_PROJECT_ID"),
                apikey=os.getenv("WATSONX_APIKEY"),
            )

        # Read text file
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(raw_text)
        docs = [Document(page_content=c) for c in chunks]

        # Persist directory
        persist_directory = os.path.join("data", "chroma_store", collection_name)
        os.makedirs(persist_directory, exist_ok=True)

        # Create or load Chroma vectorstore
        chroma_db_path = os.path.join(persist_directory, "chroma.sqlite3")
        if os.path.exists(chroma_db_path):
            logging.info(f"Loading existing vector store: {persist_directory}")
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        else:
            logging.info(f"Creating new vector store for {collection_name}...")
            vectorstore = Chroma.from_documents(
                documents=docs,
                embedding_function=embeddings,
                collection_name=collection_name,
                persist_directory=persist_directory
            )
            vectorstore.persist()

        return vectorstore

    except Exception as e:
        logging.error(f"Failed to create vector store: {e}")
        return None
