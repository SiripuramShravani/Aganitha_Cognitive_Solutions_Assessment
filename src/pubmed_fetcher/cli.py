"""
Command Line Interface

Main CLI interface for the PubMed paper fetcher application.
"""

import logging
import sys
from typing import Optional
import click

from .pubmed_client import PubMedClient
from .paper_analyzer import PaperAnalyzer
from .csv_exporter import CSVExporter


def setup_logging(debug: bool = False) -> None:
    """
    Setup logging configuration.
    
    Args:
        debug: Enable debug logging if True
    """
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


@click.command()
@click.argument('query', required=True)
@click.option('-f', '--file', 'output_file', help='Output filename for CSV results')
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging')
@click.option('--max-results', default=100, help='Maximum number of results to fetch')
@click.option('--api-key', help='NCBI API key for higher rate limits')
def main(query: str, output_file: Optional[str], debug: bool, max_results: int, api_key: Optional[str]) -> None:
    """
    Fetch research papers from PubMed and filter by pharmaceutical/biotech company affiliations.
    
    QUERY: PubMed search query (supports full PubMed syntax)
    
    Examples:
        get-papers-list "cancer treatment"
        get-papers-list "diabetes[Title] AND 2023[Date - Publication]" --file results.csv
        get-papers-list "Smith J[Author]" --debug
    """
    # Setup logging
    setup_logging(debug)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Starting PubMed paper search with query: {query}")
        
        # Initialize components
        client = PubMedClient(api_key=api_key)
        analyzer = PaperAnalyzer()
        exporter = CSVExporter()
        
        # Search for papers
        logger.info("Searching PubMed for papers...")
        pmid_list = client.search_papers(query, max_results=max_results)
        
        if not pmid_list:
            logger.warning("No papers found for the given query")
            print("No papers found matching your query.")
            return
            
        logger.info(f"Found {len(pmid_list)} papers, fetching details...")
        
        # Fetch paper details
        papers_data = []
        for i, pmid in enumerate(pmid_list, 1):
            logger.debug(f"Processing paper {i}/{len(pmid_list)}: PMID {pmid}")
            
            paper_details = client.fetch_paper_details(pmid)
            if paper_details:
                # Analyze paper for company affiliations
                analyzed_paper = analyzer.analyze_paper(paper_details)
                
                # Only include papers with company affiliations
                if analyzed_paper.get('company_affiliations'):
                    papers_data.append(analyzed_paper)
                    logger.debug(f"Found company affiliation in PMID {pmid}")
                    
        logger.info(f"Found {len(papers_data)} papers with company affiliations")
        
        # Validate and clean data
        cleaned_data = exporter.validate_data(papers_data)
        
        if not cleaned_data:
            logger.warning("No papers with company affiliations found")
            print("No papers with pharmaceutical/biotech company affiliations found.")
            return
            
        # Export results
        if output_file:
            success = exporter.export_to_csv(cleaned_data, output_file)
            if success:
                print(f"Results exported to {output_file}")
            else:
                logger.error("Failed to export results to CSV")
                sys.exit(1)
        else:
            exporter.export_to_console(cleaned_data)
            
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 