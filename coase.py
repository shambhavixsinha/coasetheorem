import os
import re
import pdfplumber
import fitz  # PyMuPDF

# Function to extract text from PDF using pdfplumber
def extract_text_from_pdf(pdf_path):
    pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
        return pages
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

# Function to search for "Coase" references in the text
def search_coase_references(pages):
    pattern = r'\bCoase\b|\bCoase\'s result\b|\bCoase theorem\b'
    results = []

    for i, page_text in enumerate(pages):
        for match in re.finditer(pattern, page_text, re.IGNORECASE):
            paragraphs = page_text.split("\n")
            for para in paragraphs:
                if match.group(0) in para:
                    results.append({
                        "page": i + 1,
                        "paragraph": para.strip(),
                        "term": match.group(0)
                    })
                    break
    return results

# Function to extract page images and highlight terms
def highlight_term_in_pdf(pdf_path, references):
    try:
        doc = fitz.open(pdf_path)
        output_path = os.path.splitext(pdf_path)[0] + '_highlighted.pdf'

        for ref in references:
            page_num = ref['page'] - 1
            term = ref['term']

            page = doc[page_num]
            text_instances = page.search_for(term)

            for inst in text_instances:
                # Highlight each instance of the term
                page.add_highlight_annot(inst)

        # Save the PDF with highlights
        doc.save(output_path, deflate=True)
        print(f"Highlighted PDF saved to: {output_path}")
    except Exception as e:
        print(f"Error highlighting terms in {pdf_path}: {e}")

# Function to save the extracted references to a text file
def save_to_text_file(pdf_path, references):
    text_file_path = os.path.splitext(pdf_path)[0] + '_coase_references.txt'

    with open(text_file_path, 'w') as f:
        for ref in references:
            f.write(f"Page: {ref['page']}\n")
            f.write(f"Paragraph: {ref['paragraph']}\n")
            f.write('-' * 50 + '\n\n')
    
    print(f"Extracted references saved to: {text_file_path}")

# Directory where the PDFs are stored
pdf_dir = 'LawPDFExport'

# Loop through all PDFs in the directory
for pdf_filename in os.listdir(pdf_dir):
    if pdf_filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        print(f"Processing file: {pdf_filename}")
        
        # Extract text from PDF
        pages = extract_text_from_pdf(pdf_path)
        
        if pages:
            # Search for Coase references
            references = search_coase_references(pages)
            
            # Save references to a text file
            if references:
                save_to_text_file(pdf_path, references)
                # Highlight terms in the PDF and save a visual version
                highlight_term_in_pdf(pdf_path, references)
            else:
                print(f"No Coase references found in {pdf_filename}")
        else:
            print(f"Skipping {pdf_filename} due to extraction failure.")
