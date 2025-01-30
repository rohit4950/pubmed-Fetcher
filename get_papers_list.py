import csv
import logging
import requests
import json
import re
from xml.etree import ElementTree
from requests.adapters import HTTPAdapter, Retry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up requests session with retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def get_papers_list(query, max_results=100, debug=False):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Step 1: Search for papers
    search_url = f"{BASE_URL}esearch.fcgi"
    params = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json"}
    
    try:
        response = session.get(search_url, params=params)
        response.raise_for_status()
        search_data = response.json()
        pmids = search_data.get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        logging.error(f"Error during search request: {e}")
        return []
    
    if not pmids:
        logging.info("No papers found for the given query.")
        return []
    
    # Step 2: Fetch paper details
    fetch_url = f"{BASE_URL}efetch.fcgi"
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}
    
    try:
        response = session.get(fetch_url, params=params)
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)
    except Exception as e:
        logging.error(f"Error fetching or parsing XML: {e}")
        return []
    
    papers = []
    company_keywords = {"pharma", "biotech", "pharmaceutical", "biotechnology", "drug", "medical"}
    
    for article in root.findall(".//PubmedArticle"):
        title = article.find(".//ArticleTitle")
        pubmed_id = article.find(".//PMID")
        pub_date = article.find(".//PubDate")
        
        title = title.text if title is not None else "N/A"
        pubmed_id = pubmed_id.text if pubmed_id is not None else "N/A"
        
        year = pub_date.find("Year").text if pub_date is not None and pub_date.find("Year") is not None else "N/A"
        month = pub_date.find("Month").text if pub_date is not None and pub_date.find("Month") is not None else "N/A"
        day = pub_date.find("Day").text if pub_date is not None and pub_date.find("Day") is not None else "N/A"
        publication_date = f"{year}-{month}-{day}" if year != "N/A" else "N/A"
        
        authors = article.findall(".//Author")
        non_academic_authors = []
        company_affiliations = []
        corresponding_author_email = "N/A"
        
        for author in authors:
            fore_name = author.find(".//ForeName")
            last_name = author.find(".//LastName")
            
            name = " ".join(filter(None, [fore_name.text if fore_name is not None else "", last_name.text if last_name is not None else ""])).strip()
            affiliation = author.find(".//AffiliationInfo/Affiliation")
            
            if affiliation is not None:
                aff_text = affiliation.text.lower()
                if any(keyword in aff_text for keyword in company_keywords):
                    non_academic_authors.append(name)
                    company_affiliations.append(affiliation.text)
            
            # Extract email using regex
            if corresponding_author_email == "N/A" and affiliation is not None:
                email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", affiliation.text)
                if email_match:
                    corresponding_author_email = email_match.group(0)
        
        if company_affiliations:
            papers.append({
                "PubmedID": pubmed_id,
                "Title": title,
                "Publication Date": publication_date,
                "Non-academic Author(s)": "; ".join(non_academic_authors),
                "Company Affiliation(s)": "; ".join(company_affiliations),
                "Corresponding Author Email": corresponding_author_email,
            })
    
    return papers

def save_to_csv(papers, filename):
    if not papers:
        logging.info(f"No papers to save in {filename}.")
        return
    
    keys = papers[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(papers)
    
    logging.info(f"Results saved to {filename}")
