"""
PubMed API Client

Handles all interactions with the PubMed API including searching for papers
and fetching detailed information about papers and authors.
"""

import logging
import time
from typing import Dict, List, Optional, Any
import requests
from xml.etree import ElementTree as ET


class PubMedClient:
    """Client for interacting with PubMed API."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    SEARCH_URL = f"{BASE_URL}/esearch.fcgi"
    FETCH_URL = f"{BASE_URL}/efetch.fcgi"
    
    def __init__(self, api_key: Optional[str] = None, delay: float = 0.1):
        """
        Initialize PubMed client.
        
        Args:
            api_key: NCBI API key for higher rate limits
            delay: Delay between API calls in seconds
        """
        self.api_key = api_key
        self.delay = delay
        self.logger = logging.getLogger(__name__)
        
    def search_papers(self, query: str, max_results: int = 100) -> List[str]:
        """
        Search for papers using PubMed query.
        
        Args:
            query: PubMed search query
            max_results: Maximum number of results to return
            
        Returns:
            List of PubMed IDs
        """
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'sort': 'relevance'
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
            
        try:
            self.logger.debug(f"Searching PubMed with query: {query}")
            response = requests.get(self.SEARCH_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            id_list = data.get('esearchresult', {}).get('idlist', [])
            
            self.logger.info(f"Found {len(id_list)} papers for query: {query}")
            time.sleep(self.delay)
            
            return id_list
            
        except requests.RequestException as e:
            self.logger.error(f"Error searching PubMed: {e}")
            raise
            
    def fetch_paper_details(self, pmid: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information about a paper.
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Dictionary containing paper details or None if error
        """
        params = {
            'db': 'pubmed',
            'id': pmid,
            'retmode': 'xml',
            'rettype': 'abstract'
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
            
        try:
            self.logger.debug(f"Fetching details for PMID: {pmid}")
            response = requests.get(self.FETCH_URL, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Extract paper information
            paper_info = self._parse_paper_xml(root)
            
            time.sleep(self.delay)
            return paper_info
            
        except (requests.RequestException, ET.ParseError) as e:
            self.logger.error(f"Error fetching paper details for PMID {pmid}: {e}")
            return None
            
    def _parse_paper_xml(self, root: ET.Element) -> Dict[str, Any]:
        """
        Parse PubMed XML response to extract paper details.
        
        Args:
            root: XML root element
            
        Returns:
            Dictionary with paper details
        """
        paper_info = {
            'pmid': '',
            'title': '',
            'publication_date': '',
            'authors': [],
            'corresponding_author_email': '',
            'abstract': ''
        }
        
        # Find the PubmedArticle element
        pubmed_article = root.find('.//PubmedArticle')
        if pubmed_article is None:
            return paper_info
            
        # Extract PMID
        pmid_elem = pubmed_article.find('.//PMID')
        if pmid_elem is not None:
            paper_info['pmid'] = pmid_elem.text
            
        # Extract title
        title_elem = pubmed_article.find('.//ArticleTitle')
        if title_elem is not None:
            paper_info['title'] = title_elem.text or ''
            
        # Extract publication date
        pub_date = pubmed_article.find('.//PubDate')
        if pub_date is not None:
            year_elem = pub_date.find('Year')
            month_elem = pub_date.find('Month')
            if year_elem is not None:
                date_parts = [year_elem.text]
                if month_elem is not None:
                    date_parts.insert(0, month_elem.text)
                paper_info['publication_date'] = '-'.join(date_parts)
                
        # Extract authors
        author_list = pubmed_article.find('.//AuthorList')
        if author_list is not None:
            for author in author_list.findall('Author'):
                author_info = self._parse_author(author)
                if author_info:
                    paper_info['authors'].append(author_info)
                    
        # Extract abstract
        abstract_elem = pubmed_article.find('.//AbstractText')
        if abstract_elem is not None:
            paper_info['abstract'] = abstract_elem.text or ''
            
        return paper_info
        
    def _parse_author(self, author_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """
        Parse author information from XML.
        
        Args:
            author_elem: Author XML element
            
        Returns:
            Dictionary with author details
        """
        author_info = {
            'name': '',
            'affiliation': '',
            'email': ''
        }
        
        # Extract name
        last_name_elem = author_elem.find('LastName')
        first_name_elem = author_elem.find('ForeName')
        
        if last_name_elem is not None and first_name_elem is not None:
            author_info['name'] = f"{first_name_elem.text} {last_name_elem.text}"
        elif last_name_elem is not None:
            author_info['name'] = last_name_elem.text
        elif first_name_elem is not None:
            author_info['name'] = first_name_elem.text
            
        # Extract affiliation
        affiliation_elem = author_elem.find('AffiliationInfo/Affiliation')
        if affiliation_elem is not None:
            author_info['affiliation'] = affiliation_elem.text or ''
            
        # Extract email (if available)
        email_elem = author_elem.find('AffiliationInfo/Affiliation')
        if email_elem is not None and '@' in (email_elem.text or ''):
            author_info['email'] = email_elem.text
            
        return author_info if author_info['name'] else None 