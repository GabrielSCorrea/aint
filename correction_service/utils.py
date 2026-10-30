import cv2
import numpy as np
import pymupdf

from settings import QUESTIONS


def parse_int(text):
    try:
        return int(text)
    except ValueError:
        return None


def parse_grade(text):
    try:
        return float(text)
    except ValueError:
        return None


def split_pdf_into_pages(
    document: pymupdf.Document,
) -> list[pymupdf.Document]:
    page_documents = []

    for page_number in range(document.page_count):
        page_document = pymupdf.open()
        page_document.insert_pdf(document, from_page=page_number, to_page=page_number)
        page_documents.append(page_document)

    return page_documents


def read_qr_code_values(page_documents: list[pymupdf.Document]) -> list[list[str]]:
    detector = cv2.QRCodeDetector()
    page_values = []

    for page_document in page_documents:
        page = page_document[0]

        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(2, 2),
            colorspace=pymupdf.csRGB,
            alpha=False,
        )
        image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
            pixmap.height,
            pixmap.width,
            3,
        )
        grayscale = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        found, values, _, _ = detector.detectAndDecodeMulti(grayscale)

        values_found = []
        if found:
            for value in values:
                if value:
                    values_found.append(value)
        page_values.append(values_found)

    return page_values


def cover_qr_codes_with_gray_squares(
    page_documents: list[pymupdf.Document],
) -> None:
    detector = cv2.QRCodeDetector()
    gray = (0.5, 0.5, 0.5)

    for page_document in page_documents:
        page = page_document[0]
        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(2, 2),
            colorspace=pymupdf.csRGB,
            alpha=False,
        )
        image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
            pixmap.height,
            pixmap.width,
            3,
        )
        grayscale = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        _, _, points, _ = detector.detectAndDecodeMulti(grayscale)
        if points is None:
            continue

        scale_x = pixmap.width / page.rect.width
        scale_y = pixmap.height / page.rect.height
        for qr_points in points:
            qr_points = qr_points.reshape(-1, 2)
            left, right = qr_points[:, 0].min(), qr_points[:, 0].max()
            top, bottom = qr_points[:, 1].min(), qr_points[:, 1].max()
            side = max(right - left, bottom - top) * 1.1
            center_x = (left + right) / 2
            center_y = (top + bottom) / 2
            page.draw_rect(
                pymupdf.Rect(
                    page.rect.x0 + (center_x - side / 2) / scale_x,
                    page.rect.y0 + (center_y - side / 2) / scale_y,
                    page.rect.x0 + (center_x + side / 2) / scale_x,
                    page.rect.y0 + (center_y + side / 2) / scale_y,
                ),
                color=None,
                fill=gray,
                overlay=True,
            )


def split_scan(pdf):
    try:
        document = pymupdf.open(stream=pdf, filetype="pdf")
    except pymupdf.FileDataError:
        raise ValueError("the file is not a valid PDF") from None
    if document.page_count == 0 or document.page_count % QUESTIONS != 0:
        raise ValueError(
            f"the scan has {document.page_count} pages, expected a multiple of {QUESTIONS}"
        )

    page_documents = split_pdf_into_pages(document)
    qr_values = read_qr_code_values(page_documents)
    cover_qr_codes_with_gray_squares(page_documents)

    pages = []
    seen = []
    for first_sheet_page in range(0, len(page_documents), QUESTIONS):
        sheet_ids = []
        for values in qr_values[first_sheet_page : first_sheet_page + QUESTIONS]:
            for value in values:
                if value.isdigit() and int(value) not in sheet_ids:
                    sheet_ids.append(int(value))

        if len(sheet_ids) != 1:
            raise ValueError(
                f"pages {first_sheet_page + 1} - {first_sheet_page + QUESTIONS} could not read the sheet's QR code"
            )

        sheet_id = sheet_ids.pop()
        if sheet_id in seen:
            raise ValueError(
                f"pages {first_sheet_page + 1} - {first_sheet_page + QUESTIONS} sheet {sheet_id} appears twice"
            )

        seen.append(sheet_id)

        sheet_pages = page_documents[first_sheet_page : first_sheet_page + QUESTIONS]
        for question_number, page_document in enumerate(sheet_pages, start=1):
            pixmap = page_document[0].get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                colorspace=pymupdf.csRGB,
                alpha=False,
            )
            pages.append((sheet_id, question_number, pixmap.tobytes("png")))

    return pages
