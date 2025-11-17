# tools.py
from langchain.tools import BaseTool
import requests
from bs4 import BeautifulSoup

def retrieve_pubmed_abstracts(query: str, max_results: int = 3) -> str:
    """
    Fetches up to `max_results` PubMed abstracts for a given query.
    """
    try:
        # Step 1: Search for PubMed IDs
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }
        search_response = requests.get(search_url, params=search_params)
        search_response.raise_for_status()
        ids = search_response.json().get("esearchresult", {}).get("idlist", [])

        if not ids:
            return "No relevant PubMed articles found."

        # Step 2: Fetch abstracts
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "xml"
        }
        fetch_response = requests.get(fetch_url, params=fetch_params)
        fetch_response.raise_for_status()

        soup = BeautifulSoup(fetch_response.text, "lxml-xml")
        abstracts = [ab.text.strip() for ab in soup.find_all("AbstractText")][:max_results]

        if not abstracts:
            return "No abstracts found in the retrieved articles."

        return "\n\n".join([f"{i+1}. {a}" for i, a in enumerate(abstracts)])

    except Exception as e:
        return f"Error retrieving data from PubMed: {e}"


# ----------------------------
# Define a LangChain Tool
# ----------------------------
class MedicalInfoTool(BaseTool):
    name: str = "PubMedRetriever"
    description: str = "Search PubMed for abstracts (up to 3 results) and return plain text."

    def _run(self, query: str) -> str:
        """Synchronous run"""
        return retrieve_pubmed_abstracts(query)

    async def _arun(self, query: str) -> str:
        """Async run (not implemented)"""
        raise NotImplementedError("Async not implemented.")


# Instantiate the tool for use in agents
medical_info_tool = MedicalInfoTool()
