# tools.py
from langchain.tools import Tool
import requests
from bs4 import BeautifulSoup

def retrieve_pubmed_abstracts_single(query: str) -> str:
    """
    Single-input version: max_results fixed internally.
    """
    max_results = 3  # fix this inside the function
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


# Single-input tool for ZeroShotAgent
medical_info_tool = Tool(
    name="PubMedRetriever",
    func=retrieve_pubmed_abstracts_single,
    description="Search PubMed for abstracts (max 3 results) and return them as plain text."
)