import subprocess

def compress_pdf(input_path, output_path, quality="screen"):
    """
    quality options:
        screen  (low resolution, small size)
        ebook   (medium)
        printer (high)
        prepress (very high)
    """
    command = [
        "gs",
        "-sDEVICE=pdfwrite",
        f"-dPDFSETTINGS=/{quality}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path,
    ]

    subprocess.run(command, check=True)

# compress_pdf("input.pdf", "compressed.pdf", quality="ebook")
# compress_pdf("Exam 2 notes copy.pdf", "Exam 2 notes copy_compressed.pdf", quality="ebook")
