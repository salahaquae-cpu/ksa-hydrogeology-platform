import urllib.request
import os

# 1. Download official Dakota Technologies MiHPT Reference Log PDF
pdf_url = "https://www.dakotatechnologies.com/docs/default-source/technical-documents/reference-log---mihptf6d9.pdf"
pdf_filename = "mihpt_reference_log.pdf"

print("Downloading official MiHPT test log PDF...")
urllib.request.urlretrieve(pdf_url, pdf_filename)
print(f"Downloaded: {pdf_filename}")

# Note: If you want to convert PDF pages directly to PNG inside Python,
# you can use 'pdf2image' or simply take a high-res screenshot of the PDF
# and save it as 'mihpt_log_1.png' inside your project directory.