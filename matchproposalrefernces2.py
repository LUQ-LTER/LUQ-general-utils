from docx import Document
import re

# Load the documents
doc_noref_path = './LUQ VII draft renewal proposal ver. 1.docx'
doc_ref_path = './LUQ VI Complete references March 1.docx'

doc_noref = Document(doc_noref_path)
doc_ref = Document(doc_ref_path)

# Function to extract text and page numbers from a document
def extract_text_and_page_numbers(doc):
    text_with_pages = []
    for i, paragraph in enumerate(doc.paragraphs):
        # Assuming a simple structure where page breaks can be identified
        if 'PAGE BREAK' in paragraph.text or i == 0: # Placeholder for actual page break detection
            page_number = len(text_with_pages) + 1  # Increment page number
            text_with_pages.append("")  # Start a new page
        text_with_pages[-1] += paragraph.text + "\n"  # Add text to the current page
    return text_with_pages

# Extract references and their text from the references document
def extract_full_references(doc):
    full_references = []
    for paragraph in doc.paragraphs:
        full_references.append(paragraph.text)
    return full_references

# Extract text with identified page numbers
text_with_pages_noref = extract_text_and_page_numbers(doc_noref)
full_references_list = extract_full_references(doc_ref)

# Check the first few entries to verify
text_with_pages_noref[:2], full_references_list[:2]


import pandas as pd

# Function to find partial references in the document
def find_partial_references(text_with_pages):
    partial_references = []
    # Regex pattern to match references like (Author et al. Year)
    pattern = re.compile(r'\([A-Za-z]+ et al\. \d{4}\)')
    for page_number, text in enumerate(text_with_pages, start=1):
        matches = pattern.findall(text)
        for match in matches:
            partial_references.append((match, page_number))
    return partial_references

# Function to match partial references to full references
def match_references(partial_refs, full_refs):
    matched_refs = []
    for partial_ref, page_number in partial_refs:
        # Extract year for more accurate matching
        year = re.search(r'\d{4}', partial_ref).group()
        for full_ref in full_refs:
            if year in full_ref and re.search(re.escape(partial_ref.split(" et al.")[0]), full_ref):
                matched_refs.append((partial_ref, full_ref, page_number))
                break
    return matched_refs

# Find partial references in the no-reference document
partial_references = find_partial_references(text_with_pages_noref)

# Match partial references to full references
matched_references = match_references(partial_references, full_references_list)

# Create a DataFrame for the matched references
df_matched_refs = pd.DataFrame(matched_references, columns=['Partial Reference', 'Full Reference', 'Page Number'])

# Save the DataFrame to a CSV file
output_csv_path = './matched_references7.csv'
df_matched_refs.to_csv(output_csv_path, index=False)

output_csv_path, df_matched_refs.head()

# Updated function to find partial references, considering multiple publications listed consecutively
def find_partial_references_updated(text_with_pages):
    partial_references_updated = []
    # Updated regex pattern to match references like (Author et al. Year) and consecutive listings
    pattern = re.compile(r'\((?:[A-Za-z]+ et al\. \d{4}(?:, )?)+\)')
    for page_number, text in enumerate(text_with_pages, start=1):
        matches = pattern.findall(text)
        for match in matches:
            # Extract individual references from the matched string
            individual_refs = re.findall(r'([A-Za-z]+ et al\. \d{4})', match)
            for ind_ref in individual_refs:
                partial_references_updated.append((ind_ref, page_number))
    return partial_references_updated

# Function to match partial references (updated to handle multiple references) to full references
def match_references_updated(partial_refs, full_refs):
    matched_refs_updated = []
    for partial_ref, page_number in partial_refs:
        # Extract year for more accurate matching
        year = re.search(r'\d{4}', partial_ref).group()
        # Search for a match in the full references
        for full_ref in full_refs:
            if year in full_ref and re.search(re.escape(partial_ref.split(" et al.")[0]), full_ref):
                matched_refs_updated.append((partial_ref, full_ref, page_number))
                break  # Break after the first match to avoid duplicate entries for the same partial ref
    return matched_refs_updated

# Find updated partial references in the no-reference document
partial_references_updated = find_partial_references_updated(text_with_pages_noref)

# Match updated partial references to full references
matched_references_updated = match_references_updated(partial_references_updated, full_references_list)

# Create a DataFrame for the updated matched references
df_matched_refs_updated = pd.DataFrame(matched_references_updated, columns=['Partial Reference', 'Full Reference', 'Page Number'])

# Save the updated DataFrame to a CSV file
output_csv_path_updated = './matched_references_updated7.csv'
df_matched_refs_updated.to_csv(output_csv_path_updated, index=False)

output_csv_path_updated, df_matched_refs_updated.head()
