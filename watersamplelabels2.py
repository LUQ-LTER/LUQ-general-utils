import os
from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import datetime

from docx.shared import Pt
import io

# Load the original document from the correct path
doc_path = './labels_30_per_pagev3.docx'
doc = Document(doc_path)

# Define new label size in points (1 inch = 72 points)
label_width_pt, label_height_pt = 2.625 * 72, 1 * 72

# Update each label to fit the new size
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            # Set each cell's width and height
            cell.width = Pt(label_width_pt)
            cell.height = Pt(label_height_pt)

# Save the updated document
updated_doc_path = './updated_water_sample_labels.docx'
doc.save(updated_doc_path)

# Convert to PDF if needed
# convert_to_pdf = True  # Set to False if Word document is preferred
#  pdf_path = './updated_water_sample_labels.pdf'


