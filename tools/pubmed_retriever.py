# tools.py
from langchain.tools import BaseTool
import requests
from bs4 import BeautifulSoup

def retrieve_pubmed_abstracts_single(query: str) -> str:
    max_results = 3
    try:
        # Step 1: search PubMed IDs
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

        # Step 2: fetch abstracts
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


# Subclass BaseTool and implement _run
class MedicalInfoTool(BaseTool):
    name: str = "PubMedRetriever"
    description: str = "Search PubMed for abstracts (max 3 results) and return them as plain text."

    def _run(self, query: str) -> str:
        return retrieve_pubmed_abstracts_single(query)

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("Async not implemented.")

medical_info_tool = MedicalInfoTool()