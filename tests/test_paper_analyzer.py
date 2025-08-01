"""
Tests for the paper analyzer module.
"""

import pytest
from pubmed_fetcher.paper_analyzer import PaperAnalyzer


class TestPaperAnalyzer:
    """Test cases for PaperAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = PaperAnalyzer()
        
    def test_is_non_academic_author_pharma_company(self):
        """Test detection of pharmaceutical company affiliations."""
        affiliation = "Novartis Pharmaceuticals, Basel, Switzerland"
        assert self.analyzer._is_non_academic_author(affiliation) is True
        
    def test_is_non_academic_author_biotech_company(self):
        """Test detection of biotech company affiliations."""
        affiliation = "Amgen Inc., Thousand Oaks, CA"
        assert self.analyzer._is_non_academic_author(affiliation) is True
        
    def test_is_non_academic_author_university(self):
        """Test that university affiliations are not flagged as non-academic."""
        affiliation = "Harvard Medical School, Boston, MA"
        assert self.analyzer._is_non_academic_author(affiliation) is False
        
    def test_is_non_academic_author_institute(self):
        """Test that research institutes are not flagged as non-academic."""
        affiliation = "National Institutes of Health, Bethesda, MD"
        assert self.analyzer._is_non_academic_author(affiliation) is False
        
    def test_extract_company_affiliations(self):
        """Test extraction of company names from affiliations."""
        affiliation = "Pfizer Inc., New York, NY"
        companies = self.analyzer._extract_company_affiliations(affiliation)
        assert "Pfizer" in companies or "Pfizer Inc" in companies
        
    def test_analyze_paper_with_company_affiliation(self):
        """Test analysis of paper with company affiliation."""
        paper_data = {
            'pmid': '12345',
            'title': 'Test Paper',
            'publication_date': '2023',
            'authors': [
                {
                    'name': 'John Smith',
                    'affiliation': 'Novartis Pharmaceuticals',
                    'email': 'john.smith@novartis.com'
                }
            ]
        }
        
        result = self.analyzer.analyze_paper(paper_data)
        
        assert result['pmid'] == '12345'
        assert result['title'] == 'Test Paper'
        assert 'John Smith' in result['non_academic_authors']
        assert 'novartis' in result['company_affiliations'].lower()
        
    def test_analyze_paper_without_company_affiliation(self):
        """Test analysis of paper without company affiliation."""
        paper_data = {
            'pmid': '12346',
            'title': 'Test Paper 2',
            'publication_date': '2023',
            'authors': [
                {
                    'name': 'Jane Doe',
                    'affiliation': 'Harvard University',
                    'email': 'jane.doe@harvard.edu'
                }
            ]
        }
        
        result = self.analyzer.analyze_paper(paper_data)
        
        assert result['pmid'] == '12346'
        assert result['title'] == 'Test Paper 2'
        assert result['non_academic_authors'] == ''
        assert result['company_affiliations'] == '' 