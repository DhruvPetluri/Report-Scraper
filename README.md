# Financial Report Scraping and Analysis Project

This project is a solution for automating the extraction and analysis of financial statements from company annual reports available online. Built with a combination of Python frameworks and libraries, the project encompasses web scraping, natural language processing, and a user-friendly web interface.
The financial extraction is not yet very robust, but it works for PDFs with easily recognisable table structures.

## Features

1. **Scrapy Spider for Web Scraping**
   - A custom-built Scrapy spider to scrape annual report PDFs from Bing search results using a company name as input.
   - Ensures efficient and targeted scraping with relevance filtering to minimize irrelevant downloads.

2. **Flask Web Application**
   - A Flask-based web app serves as the frontend.
   - Accepts company names from users, triggering the Scrapy spider in the backend to fetch relevant PDFs.

3. **Relevance Filtering with BM25**
   - Utilizes the BM25 algorithm to evaluate and rank PDFs based on their relevance to financial report queries.
   - Only the most pertinent files are processed further.

4. **Financial Statement Extraction Using FinBERT**
   - Employs FinBERT, a domain-specific NLP model, to process and extract financial statements from the filtered PDFs.
   - Focused extraction of Balance Sheets, Income Statements, and Cash Flow Statements.

## Tech Stack

- **Backend**: Python (Flask, Scrapy)
- **Frontend**: HTML, CSS, Flask Templates
- **PDF Processing**: pdfplumber
- **NLP**: Hugging Face Transformers (FinBERT), BM25 Algorithm

## Project Structure

```
project-root/
|-- extracted_statements/# Folder to store filtered Excel tables
|-- pdfs/
|-- static/
|   |-- styles.css              # CSS file for frontend styling
|-- templates/
|   |-- index.html              # HTML file for the web interface
|-- app.py                      # Main Flask app for handling frontend/backend
|-- financial_statement.py      # Backend script to process and extract data


## How It Works

1. **User Input**: The Flask app takes a company name as input from the user.
2. **Web Scraping**: The Scrapy spider searches for and downloads relevant PDFs based on predefined filters.
3. **Relevance Filtering**: PDFs are ranked and filtered using BM25 to identify potential financial reports.
4. **Financial Statement Extraction**: FinBERT is used to locate and extract key financial data from the reports.
5. **Output**: Extracted financial statements are saved as structured Excel files.

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/DhruvPetluri/Report-Scraper
   cd Report-Scraper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Flask app:
   ```bash
   python app.py
   ```

4. Access the application at `http://localhost:5000`.

## Usage

- Enter the company name in the web interface.
- The application scrapes and downloads relevant PDFs.
- financial_statement.py extracts financial statements.
- Extracted financial statements are stored in the `extracted_statements/` directory.

## Future Enhancements

-Change the Extraction to OCR based for tables, as this isn;t robust at extracting financial data.

- Integrating real-time scraping for more dynamic sources.
- Expanding the NLP model to support multilingual financial reports.
- Adding a database to store and query extracted financial data.



---

Feel free to contribute and make this project even better! For any issues or suggestions, please open an issue on GitHub.
