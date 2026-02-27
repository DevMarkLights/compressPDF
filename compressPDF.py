from pypdf import PdfReader, PdfWriter

def compress_pdf(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Enable stream compression
    writer.remove_images = False  # keep images
    writer.add_metadata({})       # clear metadata

    with open(output_path, "wb") as f:
        writer.write(f)

# compress_pdf("module 7: Information Retrieval.pdf", "module 7: Information Retrieval_compressed.pdf")
compress_pdf("module 7: Information Retrieval_compressed.pdf", "module 7: Information Retrieval_compressed.pdf")
