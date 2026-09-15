import fitz  # PyMuPDF
import os

pdf_filename = "mihpt_reference_log.pdf"

if not os.path.exists(pdf_filename):
    print(f"Error: '{pdf_filename}' not found in the project directory.")
else:
    doc = fitz.open(pdf_filename)
    print(f"Total pages found: {len(doc)}")

    for i, page in enumerate(doc):
        # 300 DPI ensures crisp text and clear graph sensor lines
        pix = page.get_pixmap(dpi=300)
        output_filename = f"mihpt_log_{i+1}.png"
        pix.save(output_filename)
        print(f"Generated high-resolution image: {output_filename}")

    print("\nPDF conversion complete!")