import os
import re
import pdfplumber
import fitz  # PyMuPDF
import pandas as pd

# Load metadata from Excel file
metadata_path = 'CT-Law-1990s-Output-v1.1-Relative-Paths.xlsx'
metadata = pd.read_excel(metadata_path)
metadata['File Name'] = metadata['File Attachments'].apply(lambda x: os.path.basename(str(x)))

# Function to extract text from PDF using pdfplumber
def extract_text(pdf_path):
    pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
        return pages
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

# New improved function to search for author information (restricted to the first 10 pages)
def extract_author_info(pages):
    author_info = []

    # Patterns to identify author-related information
    patterns = [
        r'\bProfessor\s+[A-Z][a-zA-Z]+',                   # Professor title with name
        r'\b[A-Z][a-zA-Z]+\s+University\b',               # University names
        r'\bSchool of\b',                              # Law schools
        r'\bJ\.D\.|\bPh\.D\.|\bLL\.M\.|\bEsq\.',  # Degrees and titles
        r'\bA\.B\.|\bB\.A\.|\bB\.S\.|\bM\.A\.',  # Additional degrees
        r'\bDean\b|\bChair\b',                           # Administrative titles
        r'\b[A-Z][a-zA-Z]+,\s+\d{4}\b'                   # College degree with year
    ]

    combined_pattern = '|'.join(patterns)

    for i, page_text in enumerate(pages[:10]):  # Restrict search to the first 10 pages
        sentences = re.split(r'(?<=[.!?])\s+', page_text)
        for sentence in sentences:
            if re.search(combined_pattern, sentence, re.IGNORECASE):
                author_info.append(sentence.strip())

    # Remove duplicates and join information into a single string
    author_info = list(set(author_info))
    return author_info if author_info else ["Author information not found."]

# Function to search for "Coase" references in the text
def search_coase_references(pages):
    pattern = r'\bCoase\b|\bCoase\'s result\b|\bCoase theorem\b'
    results = []

    for i, page_text in enumerate(pages):
        sentences = re.split(r'(?<=[.!?])\s+', page_text)
        page_references = [sentence.strip() for sentence in sentences if re.search(pattern, sentence, re.IGNORECASE)]
        if page_references:
            results.append({"page": i + 1, "sentences": page_references})

    return results

# Function to extract page images and highlight terms
def highlight_term_in_pdf(pdf_path, references, author_info):
    try:
        doc = fitz.open(pdf_path)
        output_path = pdf_path

        # Highlight Coase references
        for ref in references:
            page_num = ref['page'] - 1
            page = doc[page_num]

            for sentence in ref['sentences']:
                text_instances = page.search_for(sentence)
                for inst in text_instances:
                    page.add_highlight_annot(inst)

        # Highlight author information (entire sentences)
        if author_info and author_info != ["Author information not found."]:
            for page_num in range(min(10, len(doc))):  # Restrict highlighting to the first 10 pages
                page = doc[page_num]
                for sentence in author_info:
                    text_instances = page.search_for(sentence)
                    if text_instances:
                        for inst in text_instances:
                            page.add_highlight_annot(inst)

        doc.saveIncr()
        print(f"Highlighted PDF saved to: {output_path}")
    except Exception as e:
        print(f"Error highlighting terms in {pdf_path}: {e}")

# Function to save the extracted references to a text file
def save_to_text_file(pdf_path, title, author, references):
    text_file_path = os.path.splitext(pdf_path)[0] + '_coase_references.txt'

    with open(text_file_path, 'w') as f:
        f.write(f"Title: {title}\n")
        f.write(f"Author: {author}\n")
        f.write('=' * 50 + '\n\n')
        
        for ref in references:
            f.write(f"Page: {ref['page']}\n")
            if len(ref['sentences']) > 1:
                f.write("Multiple references found on this page:\n")
            for sentence in ref['sentences']:
                f.write(f"- {sentence}\n")
            f.write('-' * 50 + '\n\n')
    
    print(f"Extracted references saved to: {text_file_path}")

# Directory where the PDFs are stored
pdf_dir = 'LawPDFExportNEW'

# Match PDF files with metadata and process them
for pdf_filename in os.listdir(pdf_dir):
    if pdf_filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        print(f"Processing file: {pdf_filename}")

        # Match metadata for the PDF
        match = metadata[metadata['File Name'] == pdf_filename]
        if not match.empty:
            title = match.iloc[0]['Title']
            author = match.iloc[0]['Author']
        else:
            title = "Unknown Title"
            author = "Unknown Author"

        # Extract text from PDF
        pages = extract_text(pdf_path)

        if pages:
            # Extract author information
            author_info = extract_author_info(pages)
            
            # Search for Coase references
            references = search_coase_references(pages)
            
            # Save references to a text file
            if references:
                save_to_text_file(pdf_path, title, author, references)
                # Highlight terms in the PDF and save a visual version
                highlight_term_in_pdf(pdf_path, references, author_info)
            else:
                print(f"No Coase references found in {pdf_filename}")
        else:
            print(f"Skipping {pdf_filename} due to extraction failure.")
