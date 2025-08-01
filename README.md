# PubMed Paper Fetcher

A command-line tool to fetch research papers from PubMed and filter by pharmaceutical/biotech company affiliations.

## Overview

This tool searches PubMed for research papers based on user-specified queries and identifies papers where at least one author is affiliated with pharmaceutical or biotech companies. The results are exported to a CSV file with detailed information about the papers and their authors.

## Features

- **PubMed API Integration**: Full support for PubMed's query syntax
- **Company Affiliation Detection**: Intelligent filtering for pharmaceutical/biotech companies
- **CSV Export**: Structured output with all required fields
- **Command-line Interface**: Easy-to-use CLI with various options
- **Debug Mode**: Detailed logging for troubleshooting
- **Error Handling**: Robust error handling for API failures and invalid data

## Installation

### Prerequisites

- Python 3.8 or higher
- Poetry (for dependency management)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd pubmed-paper-fetcher
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. The tool is now ready to use with the command `get-papers-list`

## Usage

### Basic Usage

```bash
# Search for papers about cancer treatment
get-papers-list "cancer treatment"

# Search with PubMed syntax
get-papers-list "diabetes[Title] AND 2023[Date - Publication]"

# Save results to CSV file
get-papers-list "cancer treatment" --file results.csv
```

### Command-line Options

- `QUERY`: PubMed search query (required)
- `-f, --file`: Output filename for CSV results
- `-d, --debug`: Enable debug logging
- `--max-results`: Maximum number of results to fetch (default: 100)
- `--api-key`: NCBI API key for higher rate limits
- `-h, --help`: Show help message

### Examples

```bash
# Search for papers by specific author
get-papers-list "Smith J[Author]"

# Search for recent papers
get-papers-list "cancer[Title] AND 2023:2024[Date - Publication]"

# Debug mode with custom output
get-papers-list "diabetes research" --debug --file diabetes_papers.csv

# Limit results
get-papers-list "cancer treatment" --max-results 50
```

## Output Format

The tool generates a CSV file with the following columns:

- **PubmedID**: Unique identifier for the paper
- **Title**: Paper title
- **Publication Date**: Publication date
- **Non-academic Author(s)**: Names of authors affiliated with non-academic institutions
- **Company Affiliation(s)**: Names of pharmaceutical/biotech companies
- **Corresponding Author Email**: Email address of the corresponding author

## Code Organization

The project follows a modular architecture with clear separation of concerns:

### Core Components

1. **`pubmed_client.py`**: Handles all PubMed API interactions
   - Search for papers using PubMed queries
   - Fetch detailed paper information
   - Parse XML responses from PubMed API

2. **`paper_analyzer.py`**: Analyzes papers for company affiliations
   - Identifies non-academic authors
   - Detects pharmaceutical/biotech company affiliations
   - Uses heuristics to classify author institutions

3. **`csv_exporter.py`**: Handles output generation
   - Export results to CSV format
   - Console output formatting
   - Data validation and cleaning

4. **`cli.py`**: Command-line interface
   - Parses command-line arguments
   - Coordinates between components
   - Provides user-friendly output

### Project Structure

```
src/pubmed_fetcher/
├── __init__.py          # Package initialization
├── pubmed_client.py     # PubMed API client
├── paper_analyzer.py    # Paper analysis logic
├── csv_exporter.py      # CSV export functionality
└── cli.py              # Command-line interface
```

## Company Affiliation Detection

The tool uses several heuristics to identify pharmaceutical/biotech companies:

### Company Keywords
- Generic terms: pharmaceutical, pharma, biotech, biotechnology
- Business suffixes: inc, corp, corporation, ltd, limited, company
- Major companies: Novartis, Pfizer, Roche, Merck, Johnson & Johnson, etc.

### Academic Institution Filtering
- Excludes institutions with keywords: university, college, institute, laboratory
- Recognizes major academic institutions: Harvard, Stanford, MIT, etc.

### Pattern Matching
- Regular expressions for company name patterns
- Email domain analysis
- Affiliation text analysis

## Error Handling

The tool includes comprehensive error handling for:

- Invalid PubMed queries
- API failures and timeouts
- Missing or malformed data
- Network connectivity issues
- File I/O errors

## Performance Considerations

- Rate limiting to comply with PubMed API guidelines
- Efficient XML parsing
- Memory management for large result sets
- Optional API key for higher rate limits

## Development

### Tools Used

- **Poetry**: Dependency management and packaging
- **Click**: Command-line interface framework
- **Requests**: HTTP client for API calls
- **Pandas**: Data manipulation and CSV handling
- **LXML**: XML parsing for PubMed responses

### External Resources

- **PubMed API**: NCBI's E-utilities for accessing PubMed data
- **PubMed Query Syntax**: Full support for PubMed's advanced search syntax

### Testing

```bash
# Run tests
poetry run pytest

# Code formatting
poetry run black src/

# Type checking
poetry run mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository.
