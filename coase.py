import os
import re
import pdfplumber

# Function to extract text from PDF using pdfplumber
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

# Function to search for "Coase" references in the text
def search_coase_references(text):
    # Regex pattern to match "Coase", "Coase's result", etc.
    pattern = r'Coase|Coase\'s result|Coase theorem'
    results = []
    
    # Get surrounding text for context (e.g., 2000 characters around each match)
    for match in re.finditer(pattern, text, re.IGNORECASE):
        start = max(0, match.start() - 1000)
        end = min(len(text), match.end() + 1000)
        context = text[start:end]
        results.append(context)
        results.append('-' * 50)  # Separator between matches
    
    return results

# Function to save the extracted references to a text file
def save_to_text_file(pdf_path, references):
    # Create a text file with the same name as the PDF
    text_file_path = os.path.splitext(pdf_path)[0] + '.txt'
    
    with open(text_file_path, 'w') as f:
        for ref in references:
            f.write(ref + '\n\n')
    
    print(f"Extracted references saved to: {text_file_path}")

# Directory where the PDFs are stored
pdf_dir = 'LawPDFExport'

# Loop through all PDFs in the directory
for pdf_filename in os.listdir(pdf_dir):
    if pdf_filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        print(f"Processing file: {pdf_filename}")
        
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        
        # If text extraction was successful, search for Coase references
        if text:
            references = search_coase_references(text)
            
            # Save the references to a text file with the same name as the PDF
            if references:
                save_to_text_file(pdf_path, references)
            else:
                print(f"No Coase references found in {pdf_filename}")
        else:
            print(f"Skipping {pdf_filename} due to extraction failure.")
