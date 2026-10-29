from io import BytesIO
from os import path

import pymupdf
import qrcode

TEMPLATE_FILE = path.join(path.dirname(path.abspath(__file__)), "Exam-template.pdf")


def add_page_titles(document, title: str) -> pymupdf.Document:
    for page in document:
        margin = min(36, page.rect.width * 0.08)
        title_box = pymupdf.Rect(
            margin,
            18,
            page.rect.width - margin,
            48,
        )
        remaining_space = page.insert_textbox(
            title_box,
            title,
            fontsize=16,
            fontname="helv",
            align=pymupdf.TEXT_ALIGN_CENTER,
        )
        if remaining_space < 0:
            raise ValueError(f"Title does not fit on page {page.number + 1}.")
    return document


def add_qr_code_to_pages(document, value) -> None:
    if not value:
        raise ValueError("QR code content must not be empty.")

    qr_image = qrcode.make(value)
    image_data = BytesIO()
    qr_image.save(image_data, format="PNG")
    image_bytes = image_data.getvalue()

    for page in document:
        margin = 18
        size = min(72, page.rect.width - 2 * margin, page.rect.height - 2 * margin)
        if size <= 0:
            raise ValueError(f"Page {page.number + 1} is too small for a QR code.")
        corner_positions = (
            (margin, margin),
            (page.rect.width - margin - size, margin),
            (margin, page.rect.height - margin - size),
            (page.rect.width - margin - size, page.rect.height - margin - size),
        )
        for x, y in corner_positions:
            qr_rect = pymupdf.Rect(x, y, x + size, y + size)
            page.insert_image(qr_rect, stream=image_bytes)


def makeSheetPdf(sheetId, title):
    document = pymupdf.open(TEMPLATE_FILE)
    document.delete_page(0)

    add_page_titles(document, title)
    add_qr_code_to_pages(document, str(sheetId))

    return document.tobytes()


def mergePdfs(pdfs):
    document = pymupdf.open()
    for pdf in pdfs:
        document.insert_pdf(pymupdf.open(stream=pdf, filetype="pdf"))

    return document.tobytes()
