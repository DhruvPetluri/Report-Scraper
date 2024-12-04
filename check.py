import os
from tabula import read_pdf
from openpyxl import Workbook

def extract_tables_from_pdf(pdf_path, output_dir):
    """
    Extracts all tables from a PDF using Tabula and saves them to Excel files.

    Args:
        pdf_path (str): Path to the PDF file.
        output_dir (str): Directory to save the extracted tables.

    Returns:
        None
    """
    try:
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Read tables from the PDF
        tables = read_pdf(pdf_path, pages="all", multiple_tables=True, pandas_options={"header": None})

        for idx, table in enumerate(tables):
            # Create an Excel workbook for each table
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = f"Table_{idx + 1}"

            # Write table data to the sheet
            for row in table.values.tolist():
                sheet.append(row)

            # Save the workbook
            excel_path = os.path.join(output_dir, f"{os.path.basename(pdf_path)}_Table_{idx + 1}.xlsx")
            workbook.save(excel_path)
            print(f"Table {idx + 1} extracted to {excel_path}")

    except Exception as e:
        print(f"Error extracting tables from {pdf_path}: {e}")

# Example usage
extract_tables_from_pdf("pdfs", "extracted_statements")
