import os
import pdfplumber
from openpyxl import Workbook
from transformers import AutoTokenizer, AutoModel
import torch

# Initialize FinBERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = AutoModel.from_pretrained("yiyanghkust/finbert-tone")


def encode_text(text):
    """Encodes text into embeddings using FinBERT."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)  # Mean pooling of token embeddings


def calculate_similarity(query_embedding, text_embedding):
    """Calculates cosine similarity between query and text embeddings."""
    query_norm = query_embedding / query_embedding.norm(dim=1, keepdim=True)
    text_norm = text_embedding / text_embedding.norm(dim=1, keepdim=True)
    return torch.mm(query_norm, text_norm.T).squeeze().item()


def extract_financial_statements_from_pdf(pdf_path, output_dir, keywords, similarity_threshold=0.7):
    """
    Extracts tables related to specific financial statement keywords from a PDF using FinBERT for context-based filtering.

    Args:
        pdf_path (str): Path to the PDF file.
        output_dir (str): Directory where extracted Excel files will be saved.
        keywords (list): List of keywords to search for in the PDF.
        similarity_threshold (float): Threshold for similarity to consider content relevant.

    Returns:
        None
    """
    try:
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Encode keywords as a single query embedding for semantic similarity
        query = (
            "Financial statements include: Assets, Liabilities, Equity, Revenue, Expenses, "
            "Net Income, Cash Flows, Operating Expenses, Gross Profit, Depreciation, and Amortization. "
            "Typical rows include 'Current Assets', 'Total Liabilities', 'Shareholder Equity', "
            "'Net Profit', and 'Cash Flow'. Columns often represent time periods such as 'Q1 2023', 'FY2023', or 'Year Ended'."
        )
        query_embedding = encode_text(query)

        # Open the PDF file
        with pdfplumber.open(pdf_path) as pdf:
            pdf_title = os.path.basename(pdf_path).replace(".pdf", "")

            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if not page_text:
                    continue  # Skip pages with no text

                # **Step 1: Fast Filtering with Keyword Matching**
                if any(keyword.lower() in page_text.lower() for keyword in keywords):
                    # Extract context around the keywords
                    context_lines = [
                        line for line in page_text.split("\n") if any(keyword.lower() in line.lower() for keyword in keywords)
                    ]
                    context_text = " ".join(context_lines)

                    # **Step 2: Refine with FinBERT-Based Similarity**
                    context_embedding = encode_text(context_text)
                    similarity = calculate_similarity(query_embedding, context_embedding)

                    if similarity >= similarity_threshold:
                        # Check for tables on the page
                        tables = page.extract_tables()
                        if tables:
                            # Create an Excel workbook
                            workbook = Workbook()
                            sheet = workbook.active
                            sheet.title = "Financial Statement"

                            # Write tables to the Excel sheet
                            for table in tables:
                                for row in table:
                                    sheet.append(row)

                            # Save the Excel file
                            excel_filename = f"{pdf_title} - Financial Statement Page {page_num + 1}.xlsx"
                            excel_filepath = os.path.join(output_dir, excel_filename)
                            workbook.save(excel_filepath)
                            print(f"Extracted: {excel_filepath}")
                        else:
                            print(f"No tables found for relevant content on page {page_num + 1}")
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")


if __name__ == "__main__":
    # Example usage
    pdf_directory = "pdfs"  # Directory containing filtered PDFs
    output_directory = "extracted_statements"  # Directory to save extracted Excel files
    keywords_to_search = ["balance sheet", "income statement", "cash flow statement", "financial statement",
                          "financial summary", "auditors report", "profit and loss account", "financial statements",
                          "CONSOLIDATED BALANCE SHEETS", "CONSOLIDATED INCOME STATEMENTS",
                          "CONSOLIDATED CASH FLOW STATEMENTS", 
                          "CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME",]

    # Process each PDF in the directory
    for pdf_file in os.listdir(pdf_directory):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, pdf_file)
            extract_financial_statements_from_pdf(pdf_path, output_directory, keywords_to_search)
