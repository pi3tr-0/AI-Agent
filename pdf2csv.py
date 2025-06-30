import pdfplumber
import csv
def pdf_table_to_csv(pdf_path, csv_path, page_number=0):
    """
    Extracts the first table from the specified page of a PDF and writes it to a CSV.

    Args:
        pdf_path (str): Path to the input PDF file.
        csv_path (str): Path to the output CSV file.
        page_number (int): Page number to extract the table from (0-indexed).
    """
    with pdfplumber.open(pdf_path) as pdf:
        if page_number >= len(pdf.pages):
            raise ValueError(f"Page number {page_number} is out of range. PDF has {len(pdf.pages)} pages.")
        
        page = pdf.pages[page_number]
        table = page.extract_table()

        if table is None:
            raise ValueError("No table found on the specified page.")

        with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in table:
                writer.writerow(row)

    print(f"Table from page {page_number+1} saved to {csv_path}")

# Example usage:
if __name__ == "__main__":
    pdf_file = "/Users/admin/Library/Mobile Documents/com~apple~CloudDocs/Downloads/Netflic FiRe.pdf"  # Replace with your PDF file
    csv_file = "/Users/admin/Desktop/output.csv"
    pdf_table_to_csv(pdf_file, csv_file, page_number=0)