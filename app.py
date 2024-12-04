from flask import Flask, render_template, request
import os
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor, defer
from crochet import setup, wait_for
import pdfplumber
from rank_bm25 import BM25Okapi

# Initialize crochet for asynchronous support
setup()

app = Flask(__name__)

class AnnualReportsSpider(scrapy.Spider):
    name = 'annual_reports'
    max_pages = 10  # Limit the spider to parse the first 10 pages of search results
    custom_settings = {
    "RETRY_ENABLED": True,
    "RETRY_TIMES": 3,
    "DOWNLOAD_TIMEOUT": 15,
    "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7"
}

    def __init__(self, company_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_name = company_name.lower()
        self.keywords = [self.company_name]
        self.current_page = 1  # Track the current page number
        self.downloaded_pdfs = 0

    def start_requests(self):
        query = f"{self.company_name} annual report filetype:pdf"
        search_url = f"https://www.google.com/search?q={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        request = scrapy.Request(search_url, headers=headers, callback=self.parse_search_results)
        request.meta['dont_redirect'] = True
        yield request

    def parse_search_results(self, response):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Extract all PDF links in the search results
        for link in response.css('a::attr(href)').getall():
            if link and (link.startswith('http://') or link.startswith('https://')):
                request = scrapy.Request(link, headers=headers, callback=self.check_if_pdf)
                request.meta['dont_redirect'] = True
                yield request

        # Go to the next page if max_pages limit is not reached
        next_page = response.css('a#pnnext::attr(href)').get()
        if next_page and self.current_page < self.max_pages:
            next_page_url = response.urljoin(next_page)
            self.current_page += 1
            request = scrapy.Request(next_page_url, headers=headers, callback=self.parse_search_results)
            request.meta['dont_redirect'] = True
            yield request

    def check_if_pdf(self, response):
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        if 'application/pdf' in content_type and self.downloaded_pdfs < 30:
            os.makedirs("pdfs", exist_ok=True)
            pdf_name = response.url.split("/")[-1]
            pdf_path = os.path.join("pdfs", pdf_name)
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(response.body)
            self.downloaded_pdfs += 1
            # Check PDF relevance
            if not self.is_pdf_relevant(pdf_path):
                os.remove(pdf_path)  # Delete irrelevant PDF

    def is_pdf_relevant(self, pdf_path):
        text = extract_text_from_pdf(pdf_path, max_pages=1)
        if not text:
            return False

        # Tokenize the text and keywords
        documents = [text.lower().split()]
        bm25 = BM25Okapi(documents)
        query = ' '.join(self.keywords).split()
        score = bm25.get_scores(query)[0]

        # Set a relevance threshold, adjust as needed
        relevance_threshold = 0.3
        return score > relevance_threshold

# Run Scrapy spider asynchronously
@wait_for(60)  # Set a timeout to allow more time for multiple pages
def run_spider(company_name):
    configure_logging()
    runner = CrawlerRunner()
    d = runner.crawl(AnnualReportsSpider, company_name=company_name)
    return d

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        company_name = request.form['company_name']

        # Run spider and wait for completion
        run_spider(company_name)

        # Process PDFs and generate summaries
        summaries = []
        pdf_dir = "pdfs"
        for pdf_file in os.listdir(pdf_dir):
            if pdf_file.endswith(".pdf"):
                pdf_path = os.path.join(pdf_dir, pdf_file)
                # Extract and summarize as needed
                # pdf_text = extract_text_from_pdf(pdf_path, max_pages=3)
                # summary = summarize_text(pdf_text)
                # summaries.append((pdf_file, summary))
                
        return render_template('index.html', summaries=summaries)
    
    return render_template('index.html')

# Function to extract text from a limited number of pages in a PDF
def extract_text_from_pdf(pdf_path, max_pages=1):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            if i >= max_pages:  # Limit to the specified number of pages
                break
            text += page.extract_text() or ""  # Handle None case
    return text

if __name__ == '__main__':
    app.run(debug=True, port=5000)