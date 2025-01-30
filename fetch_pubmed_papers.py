import csv
import argparse
import logging
import urllib.request
import urllib.parse
import json
import ssl
from xml.etree import ElementTree

#We can use requests module instead of urllib as well but urllib gives more accurate results.
# Create an unverified SSL context
ssl_context = ssl._create_unverified_context()

def fetch_pubmed_papers(query, max_results=100, debug=False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    # Step 1: Search for papers matching the query
    search_url = f"{base_url}esearch.fcgi"
    search_params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
    })
    try:
        with urllib.request.urlopen(f"{search_url}?{search_params}", context=ssl_context) as response:
            search_data = json.loads(response.read().decode())
        if debug:
            logging.debug(f"Search response: {search_data}")
    except Exception as e:
        print(f"Error during search request: {e}")
        return []

    # Get the list of PubMed IDs (PMIDs)
    pmids = search_data.get("esearchresult", {}).get("idlist", [])

    if not pmids:
        print("No papers found for the given query.")
        return []

    # Step 2: Fetch paper details using the PMIDs
    fetch_url = f"{base_url}efetch.fcgi"
    fetch_params = urllib.parse.urlencode({
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
    })
    try:
        with urllib.request.urlopen(f"{fetch_url}?{fetch_params}", context=ssl_context) as response:
            fetch_data = response.read().decode()
    except Exception as e:
        print(f"Error during fetch request: {e}")
        return []

    try:
        root = ElementTree.fromstring(fetch_data)
    except ElementTree.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []

    papers = []

    for article in root.findall(".//PubmedArticle"):
        title = article.find(".//ArticleTitle").text if article.find(".//ArticleTitle") is not None else "N/A"
        pubmed_id = article.find(".//PMID").text if article.find(".//PMID") is not None else "N/A"
        
        # Exctracting the date if Publication 
        pub_date = article.find(".//PubDate")
        if pub_date is not None:
            year = pub_date.find("Year").text if pub_date.find("Year") is not None else "N/A"
            month = pub_date.find("Month").text if pub_date.find("Month") is not None else "N/A"
            day = pub_date.find("Day").text if pub_date.find("Day") is not None else "N/A"
            publication_date = f"{year}-{month}-{day}" if year != "N/A" else "N/A"
        else:
            publication_date = "N/A"
        
        authors = article.findall(".//Author")
        non_academic_authors = []
        company_affiliations = []
        corresponding_author_email = "N/A"

        for author in authors:
            affiliation = author.find(".//AffiliationInfo/Affiliation")
            if affiliation is not None:
                affiliation_text = affiliation.text.lower()
                if any(keyword in affiliation_text for keyword in ["pharma", "biotech", "pharmaceutical", "biotechnology", "drug", "medical"]):
                    non_academic_authors.append(
                        f"{author.find('.//ForeName').text if author.find('.//ForeName') is not None else ''} {author.find('.//LastName').text if author.find('.//LastName') is not None else ''}".strip()
                    )
                    company_affiliations.append(affiliation.text)

            # Extraction for email
            email = author.find(".//Identifier[@Source='Email']")
            if email is not None and corresponding_author_email == "N/A":
                corresponding_author_email = email.text.strip()

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
        print(f"No papers to save in {filename}.")
        return

    keys = papers[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(papers)

    print(f"Results saved to {filename}")
    
    #Main function to implement it using command lines. We use argpasser for that 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and filter PubMed papers based on industry affiliations.")
    parser.add_argument("query", help="Search query for PubMed")
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug information during execution")
    parser.add_argument("-f", "--file", type=str, help="Specify the filename to save results. If not provided, prints to console")
    parser.add_argument("--max_results", type=int, default=100, help="Maximum number of results to fetch")
    
    args = parser.parse_args()

    print("Fetching papers...")
    papers = fetch_pubmed_papers(args.query, max_results=args.max_results, debug=args.debug)

    if papers:
        print(f"Found {len(papers)} papers with relevant affiliations.")
        if args.file:
            save_to_csv(papers, args.file)
        else:
            for paper in papers:
                print(paper)
    else:
        print("No papers found with authors affiliated with pharmaceutical or biotech companies.")
