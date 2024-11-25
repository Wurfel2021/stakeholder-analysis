import pandas as pd
from fpdf import FPDF

def sanitize_text(text):
    """
    Replace or remove unsupported Unicode characters from text.
    """
    import unicodedata
    return unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('ascii')

def export_speeches_from_excel_to_pdf(excel_file, pdf_file):
    """
    Reads speeches from an Excel file and exports them to a PDF file.

    Parameters:
        excel_file (str): Path to the input Excel file containing speeches.
        pdf_file (str): Path to the output PDF file.
    """
    # Read the Excel file
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Check if required columns exist
    required_columns = ['Date', 'Speaker', 'Speech']
    for col in required_columns:
        if col not in df.columns:
            print(f"Column '{col}' not found in Excel file.")
            return

    # Initialize PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Iterate over the DataFrame rows
    for index, row in df.iterrows():
        date = sanitize_text(row.get('Date', 'Unknown Date'))
        #speaker = sanitize_text(row.get('Speaker', 'Unknown Speaker'))
        speech = sanitize_text(row.get('Speech', ''))
        
        if not speech.strip():
            continue  # Skip empty speeches

        # Add a new page
        pdf.add_page()

        # Add date to PDF
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Date: {date}", ln=1)
        pdf.ln(5)

        # Add speaker name
        pdf.set_font("Arial", "B", 11)
        #pdf.cell(0, 10, f"Speaker: {speaker}", ln=1)
        pdf.ln(5)

        # Add speech content
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, speech)
        pdf.ln(5)

    # Save the PDF
    try:
        pdf.output(pdf_file)
        print(f"PDF saved as {pdf_file}")
    except Exception as e:
        print(f"Error saving PDF: {e}")

# Example usage:
if __name__ == "__main__":
    excel_file = "hansard_speeches.xlsx"  # Replace with your Excel file path
    pdf_file = "hansard_speeches.pdf"     # Desired output PDF file path
    export_speeches_from_excel_to_pdf(excel_file, pdf_file)
