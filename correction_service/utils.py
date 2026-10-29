import cv2
import numpy as np
import pymupdf

from settings import QUESTIONS


def parseInt(text):
    try:
        return int(text)
    except ValueError:
        return None


def parseGrade(text):
    try:
        return float(text)
    except ValueError:
        return None


def readPage(page):
    pixmap = page.get_pixmap(
        matrix=pymupdf.Matrix(2, 2), colorspace=pymupdf.csRGB, alpha=False
    )
    image = (
        np.frombuffer(pixmap.samples, dtype=np.uint8)
        .reshape(pixmap.height, pixmap.width, 3)
        .copy()
    )
    grayscale = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    found, values, points, _ = cv2.QRCodeDetector().detectAndDecodeMulti(grayscale)
    if points is not None:
        for qrPoints in points:
            qrPoints = qrPoints.reshape(-1, 2)
            left, right = qrPoints[:, 0].min(), qrPoints[:, 0].max()
            top, bottom = qrPoints[:, 1].min(), qrPoints[:, 1].max()
            half = max(right - left, bottom - top) * 1.1 / 2
            centerX, centerY = (left + right) / 2, (top + bottom) / 2
            cv2.rectangle(
                image,
                (int(centerX - half), int(centerY - half)),
                (int(centerX + half), int(centerY + half)),
                (128, 128, 128),
                thickness=-1,
            )
    _, png = cv2.imencode(".png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    return (list(values) if found else []), png.tobytes()


def splitScan(pdf):
    try:
        document = pymupdf.open(stream=pdf, filetype="pdf")
    except pymupdf.FileDataError:
        raise ValueError("the file is not a valid PDF") from None
    if document.page_count == 0 or document.page_count % QUESTIONS != 0:
        raise ValueError(
            f"the scan has {document.page_count} pages, expected a multiple of {QUESTIONS}"
        )
    pages = []
    seen = set()
    for first in range(0, document.page_count, QUESTIONS):
        pageRange = f"pages {first + 1}-{first + QUESTIONS}"
        values = []
        images = []
        for page in document.pages(first, first + QUESTIONS):
            pageValues, image = readPage(page)
            values += pageValues
            images.append(image)
        sheetIds = set()
        for value in values:
            if value.isdigit():
                sheetIds.add(int(value))
        if len(sheetIds) != 1:
            raise ValueError(f"{pageRange}: could not read the sheet's QR code")
        sheetId = sheetIds.pop()
        if sheetId in seen:
            raise ValueError(f"{pageRange}: sheet {sheetId} appears twice")
        seen.add(sheetId)
        for questionNumber, image in enumerate(images, start=1):
            pages.append((sheetId, questionNumber, image))
    return pages
