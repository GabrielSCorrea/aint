import cv2
import numpy as np
import pymupdf

from settings import QUESTIONS


def readPage(page):
    # returns the QR values found on the page and a PNG of it with the QRs covered
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
        # same square as the lab's cover_qr_codes_with_gray_squares, but painted
        # on the rendered image, so the QR code is gone from the stored page
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
    # returns (sheetId, questionNumber, png) per page, ValueError for a bad scan
    try:
        document = pymupdf.open(stream=pdf, filetype="pdf")
    except pymupdf.FileDataError:
        raise ValueError("the file is not a valid PDF") from None
    if document.page_count == 0 or document.page_count % QUESTIONS != 0:
        raise ValueError(
            "the scan has %d pages, expected a multiple of %d"
            % (document.page_count, QUESTIONS)
        )
    pages = []
    seen = set()
    for first in range(0, document.page_count, QUESTIONS):
        pageRange = "pages %d-%d" % (first + 1, first + QUESTIONS)
        values = []
        images = []
        for page in document.pages(first, first + QUESTIONS):
            pageValues, image = readPage(page)
            values += pageValues
            images.append(image)
        # every page of a sheet carries the same QR code: the sheet id
        sheetIds = {int(v) for v in values if v.isdigit()}
        if len(sheetIds) != 1:
            raise ValueError("%s: could not read the sheet's QR code" % pageRange)
        sheetId = sheetIds.pop()
        if sheetId in seen:
            raise ValueError("%s: sheet %d appears twice" % (pageRange, sheetId))
        seen.add(sheetId)
        # the page position within the sheet is the question number
        for questionNumber, image in enumerate(images, start=1):
            pages.append((sheetId, questionNumber, image))
    return pages
