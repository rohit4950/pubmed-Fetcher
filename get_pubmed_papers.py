 #Main function to implement it using command lines. We use argpasser for that 
import logging 
import argparse
from get_papers_list import get_papers_list,save_to_csv
 

def main():
    parser = argparse.ArgumentParser(description="Fetch and filter PubMed papers based on industry affiliations.")
    parser.add_argument("query", help="Search query for PubMed")
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug information during execution")
    parser.add_argument("-f", "--file", type=str, help="Specify the filename to save results. If not provided, prints to console")
    parser.add_argument("--max_results", type=int, default=100, help="Maximum number of results to fetch")
    
    args = parser.parse_args()

    print("Fetching papers...")
    papers = get_papers_list(args.query, max_results=args.max_results, debug=args.debug)

    if papers:
        print(f"Found {len(papers)} papers with relevant affiliations.")
        if args.file:
            save_to_csv(papers, args.file)
        else:
            for paper in papers:
                print(paper)
    else:
        print("No papers found with authors affiliated with pharmaceutical or biotech companies.")

if __name__ == "__main__":
    main()