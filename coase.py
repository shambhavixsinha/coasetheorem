import os
import re
import pdfplumber
import fitz  # PyMuPDF

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

# Function to search for author information
def extract_author_info(pages):
    author_info = None

    # Pattern to match multiline footnotes starting with '*'
    footnote_pattern = r'\*.*?(?=\n|\Z)'
    keywords_pattern = r'(Professor|University|Law|J\.D\.|A\.B\.)'

    for page_text in pages:
        # Search for footnotes with asterisk
        footnote_match = re.search(footnote_pattern, page_text, re.IGNORECASE | re.DOTALL)
        if footnote_match:
            # Extract the full footnote text
            full_footnote = footnote_match.group(0)

            # Check if the footnote contains any of the keywords
            if re.search(keywords_pattern, full_footnote, re.IGNORECASE):
                author_info = full_footnote
                break

    if not author_info:
        # If no footnote match, search generally for keywords
        general_pattern = r'(Professor [A-Z][a-zA-Z]*|[A-Z][a-zA-Z]* University|School of Law)'
        for page_text in pages:
            general_match = re.search(general_pattern, page_text, re.IGNORECASE)
            if general_match:
                author_info = general_match.group(0).strip()
                break

    return author_info or "Author information not found."

# Function to search for "Coase" references in the text
def search_coase_references(pages):
    pattern = r'\bCoase\b|\bCoase\'s result\b|\bCoase theorem\b'
    results = []

    for i, page_text in enumerate(pages):
        sentences = re.split(r'(?<=[.!?])\s+', page_text)
        page_references = []

        for sentence in sentences:
            if re.search(pattern, sentence, re.IGNORECASE):
                page_references.append(sentence.strip())

        if page_references:
            results.append({
                "page": i + 1,
                "sentences": page_references
            })

    return results

# Function to extract page images and highlight terms
def highlight_term_in_pdf(pdf_path, references):
    try:
        doc = fitz.open(pdf_path)
        output_path = os.path.splitext(pdf_path)[0] + '_highlighted.pdf'

        for ref in references:
            page_num = ref['page'] - 1
            page = doc[page_num]

            for sentence in ref['sentences']:
                text_instances = page.search_for(sentence)
                for inst in text_instances:
                    # Highlight each instance of the term
                    page.add_highlight_annot(inst)

        # Save the PDF with highlights
        doc.save(output_path, deflate=True)
        print(f"Highlighted PDF saved to: {output_path}")
    except Exception as e:
        print(f"Error highlighting terms in {pdf_path}: {e}")

# Function to save the extracted references and author info to a text file
def save_to_text_file(pdf_path, author_info, references):
    text_file_path = os.path.splitext(pdf_path)[0] + '_coase_references.txt'

    with open(text_file_path, 'w') as f:
        f.write(f"Author Information:\n{author_info}\n")
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

# Loop through all PDFs in the directory
for pdf_filename in os.listdir(pdf_dir):
    if pdf_filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        print(f"Processing file: {pdf_filename}")
        
        # Extract text from PDF
        pages = extract_text(pdf_path)
        
        if pages:
            # Extract author information from the first page
            author_info = extract_author_info(pages)
            
            # Search for Coase references
            references = search_coase_references(pages)
            
            # Save references and author info to a text file
            if references or author_info:
                save_to_text_file(pdf_path, author_info, references)
                # Highlight terms in the PDF and save a visual version
                highlight_term_in_pdf(pdf_path, references)
            else:
                print(f"No Coase references found in {pdf_filename}")
        else:
            print(f"Skipping {pdf_filename} due to extraction failure.")
