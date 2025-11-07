# tools/vector_builder.py
import os
from langchain_ibm import WatsonxEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def create_vector_store(file_path, collection_name, embeddings):
    """
    Create a Chroma vector store from a text file using provided embeddings.
    """
    if embeddings is None:
        raise ValueError("Embeddings must be provided to create vector store.")

    # Read text file
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_text(raw_text)
    docs = [Document(page_content=t) for t in texts]

    # Persist path
    persist_directory = os.path.join("data", "chroma_store", collection_name)
    os.makedirs(persist_directory, exist_ok=True)

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory
    )

    vectorstore.persist()
    return vectorstore
