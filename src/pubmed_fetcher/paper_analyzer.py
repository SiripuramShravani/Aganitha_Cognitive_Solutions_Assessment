"""
Paper Analyzer

Analyzes papers to identify pharmaceutical/biotech company affiliations
and non-academic authors.
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional


class PaperAnalyzer:
    """Analyzes papers for company affiliations and non-academic authors."""
    
    def __init__(self):
        """Initialize the paper analyzer."""
        self.logger = logging.getLogger(__name__)
        
        # Keywords to identify pharmaceutical/biotech companies
        self.company_keywords = [
            'pharmaceutical', 'pharma', 'biotech', 'biotechnology',
            'inc', 'corp', 'corporation', 'ltd', 'limited', 'company',
            'novartis', 'pfizer', 'roche', 'merck', 'johnson & johnson',
            'astrazeneca', 'gilead', 'amgen', 'biogen', 'regeneron',
            'moderna', 'biontech', 'sanofi', 'glaxosmithkline', 'gsk',
            'eli lilly', 'abbvie', 'bristol-myers squibb', 'bms',
            'takeda', 'bayer', 'boehringer ingelheim', 'genentech',
            'celgene', 'gilead sciences', 'biogen idec', 'amgen inc',
            'regeneron pharmaceuticals', 'moderna therapeutics',
            'biontech se', 'sanofi-aventis', 'glaxosmithkline plc'
        ]
        
        # Keywords to identify academic institutions
        self.academic_keywords = [
            'university', 'college', 'institute', 'laboratory', 'lab',
            'medical school', 'school of medicine', 'department of',
            'faculty of', 'academic', 'academy', 'polytechnic',
            'university hospital', 'medical center', 'research center',
            'national institute', 'nih', 'nci', 'nhlbi', 'niddk',
            'harvard', 'stanford', 'mit', 'caltech', 'berkeley',
            'oxford', 'cambridge', 'imperial college', 'ucl',
            'johns hopkins', 'yale', 'princeton', 'columbia',
            'university of', 'state university', 'medical university'
        ]
        
    def analyze_paper(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a paper to identify company affiliations and non-academic authors.
        
        Args:
            paper_data: Dictionary containing paper information
            
        Returns:
            Dictionary with analysis results
        """
        if not paper_data or 'authors' not in paper_data:
            return self._create_empty_result()
            
        authors = paper_data.get('authors', [])
        non_academic_authors = []
        company_affiliations = []
        corresponding_author_email = ''
        
        for author in authors:
            author_name = author.get('name', '')
            affiliation = author.get('affiliation', '').lower()
            email = author.get('email', '')
            
            # Check if author is non-academic
            if self._is_non_academic_author(affiliation):
                non_academic_authors.append(author_name)
                
                # Check for company affiliations
                companies = self._extract_company_affiliations(affiliation)
                company_affiliations.extend(companies)
                
            # Extract corresponding author email
            if email and not corresponding_author_email:
                corresponding_author_email = email
                
        # Remove duplicates
        company_affiliations = list(set(company_affiliations))
        
        return {
            'pmid': paper_data.get('pmid', ''),
            'title': paper_data.get('title', ''),
            'publication_date': paper_data.get('publication_date', ''),
            'non_academic_authors': '; '.join(non_academic_authors),
            'company_affiliations': '; '.join(company_affiliations),
            'corresponding_author_email': corresponding_author_email
        }
        
    def _is_non_academic_author(self, affiliation: str) -> bool:
        """
        Determine if an author is non-academic based on affiliation.
        
        Args:
            affiliation: Author's affiliation text
            
        Returns:
            True if author is non-academic, False otherwise
        """
        if not affiliation:
            return False
            
        affiliation_lower = affiliation.lower()
        
        # Check for academic keywords
        for academic_keyword in self.academic_keywords:
            if academic_keyword in affiliation_lower:
                return False
                
        # Check for company keywords
        for company_keyword in self.company_keywords:
            if company_keyword in affiliation_lower:
                return True
                
        # Additional heuristics for non-academic institutions
        non_academic_patterns = [
            r'\b(inc|corp|ltd|llc|company|co\.)\b',
            r'\b(pharmaceutical|biotech|biotechnology)\b',
            r'\b(research|development|rd)\s+(center|institute|facility)\b',
            r'\b(clinical|medical)\s+(trial|research|development)\b'
        ]
        
        for pattern in non_academic_patterns:
            if re.search(pattern, affiliation_lower):
                return True
                
        return False
        
    def _extract_company_affiliations(self, affiliation: str) -> List[str]:
        """
        Extract company names from affiliation text.
        
        Args:
            affiliation: Affiliation text
            
        Returns:
            List of company names found
        """
        companies = []
        affiliation_lower = affiliation.lower()
        
        # Check for known company names
        for company_keyword in self.company_keywords:
            if company_keyword in affiliation_lower:
                # Try to extract the full company name
                company_name = self._extract_company_name(affiliation, company_keyword)
                if company_name:
                    companies.append(company_name)
                    
        # Look for patterns that suggest company names
        company_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(Inc|Corp|Ltd|LLC|Company|Co\.)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(Pharmaceuticals|Biotech|Biotechnology)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(Research|Development|R&D)\s+(Center|Institute|Facility)\b'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, affiliation, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    company_name = ' '.join(match)
                else:
                    company_name = match
                companies.append(company_name)
                
        return companies
        
    def _extract_company_name(self, affiliation: str, keyword: str) -> Optional[str]:
        """
        Extract full company name around a keyword.
        
        Args:
            affiliation: Affiliation text
            keyword: Company keyword found
            
        Returns:
            Full company name or None
        """
        # Simple extraction - look for words around the keyword
        words = affiliation.split()
        keyword_lower = keyword.lower()
        
        for i, word in enumerate(words):
            if keyword_lower in word.lower():
                # Try to get 2-3 words before and after the keyword
                start = max(0, i - 2)
                end = min(len(words), i + 3)
                company_name = ' '.join(words[start:end])
                return company_name
                
        return None
        
    def _create_empty_result(self) -> Dict[str, str]:
        """Create an empty result dictionary."""
        return {
            'pmid': '',
            'title': '',
            'publication_date': '',
            'non_academic_authors': '',
            'company_affiliations': '',
            'corresponding_author_email': ''
        } 