"""
CSV Exporter

Handles CSV output generation and formatting of paper analysis results.
"""

import csv
import logging
from typing import List, Dict, Any, Optional
import pandas as pd


class CSVExporter:
    """Handles CSV export functionality."""
    
    def __init__(self):
        """Initialize the CSV exporter."""
        self.logger = logging.getLogger(__name__)
        
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str) -> bool:
        """
        Export data to CSV file.
        
        Args:
            data: List of dictionaries containing paper data
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        if not data:
            self.logger.warning("No data to export")
            return False
            
        try:
            # Define column headers
            fieldnames = [
                'PubmedID',
                'Title', 
                'Publication Date',
                'Non-academic Author(s)',
                'Company Affiliation(s)',
                'Corresponding Author Email'
            ]
            
            # Write CSV file
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in data:
                    # Map internal field names to CSV column names
                    csv_row = {
                        'PubmedID': row.get('pmid', ''),
                        'Title': row.get('title', ''),
                        'Publication Date': row.get('publication_date', ''),
                        'Non-academic Author(s)': row.get('non_academic_authors', ''),
                        'Company Affiliation(s)': row.get('company_affiliations', ''),
                        'Corresponding Author Email': row.get('corresponding_author_email', '')
                    }
                    writer.writerow(csv_row)
                    
            self.logger.info(f"Successfully exported {len(data)} papers to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            return False
            
    def export_to_console(self, data: List[Dict[str, Any]]) -> None:
        """
        Print data to console in a formatted table.
        
        Args:
            data: List of dictionaries containing paper data
        """
        if not data:
            print("No papers found matching the criteria.")
            return
            
        # Create DataFrame for nice formatting
        df_data = []
        for row in data:
            df_data.append({
                'PubmedID': row.get('pmid', ''),
                'Title': row.get('title', '')[:50] + '...' if len(row.get('title', '')) > 50 else row.get('title', ''),
                'Publication Date': row.get('publication_date', ''),
                'Non-academic Author(s)': row.get('non_academic_authors', '')[:30] + '...' if len(row.get('non_academic_authors', '')) > 30 else row.get('non_academic_authors', ''),
                'Company Affiliation(s)': row.get('company_affiliations', '')[:30] + '...' if len(row.get('company_affiliations', '')) > 30 else row.get('company_affiliations', ''),
                'Corresponding Author Email': row.get('corresponding_author_email', '')
            })
            
        df = pd.DataFrame(df_data)
        
        print(f"\nFound {len(data)} papers with pharmaceutical/biotech company affiliations:")
        print("=" * 80)
        print(df.to_string(index=False))
        print("=" * 80)
        
    def validate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and clean data before export.
        
        Args:
            data: List of dictionaries containing paper data
            
        Returns:
            Cleaned data list
        """
        cleaned_data = []
        
        for row in data:
            # Ensure all required fields exist
            cleaned_row = {
                'pmid': str(row.get('pmid', '')),
                'title': str(row.get('title', '')),
                'publication_date': str(row.get('publication_date', '')),
                'non_academic_authors': str(row.get('non_academic_authors', '')),
                'company_affiliations': str(row.get('company_affiliations', '')),
                'corresponding_author_email': str(row.get('corresponding_author_email', ''))
            }
            
            # Remove any papers without basic information
            if cleaned_row['pmid'] and cleaned_row['title']:
                cleaned_data.append(cleaned_row)
                
        return cleaned_data 