from io import BytesIO
from xmlrpc.client import Fault

from flask import abort, redirect, render_template, send_file

import models
import utils
from settings import ALREADY_PRINTED_FAULT, INVALID_DATA_FAULT


def index():
    return redirect("/exams")


def list_exams():
    return render_template("list_exams.html", exams=models.ResolutionSheet.exams())


def download_exam_pdf(exam_id):
    sheets = models.ResolutionSheet.for_exam(exam_id)
    if not sheets:
        abort(404)

    pdfs = []
    for sheet in sheets:
        pdfs.append(sheet.pdf)
    pdf = utils.merge_pdfs(pdfs)

    return send_file(
        BytesIO(pdf),
        mimetype="application/pdf",
        download_name=f"exam-{exam_id}.pdf",
    )


def print_exam(exam_id, date, course, sheets_num):
    error = models.ResolutionSheet.validate(exam_id, date, course, sheets_num)

    if error:
        raise Fault(INVALID_DATA_FAULT, error)

    if models.ResolutionSheet.is_printed(exam_id):
        error = f"exam {exam_id} already has resolution sheets"
        raise Fault(ALREADY_PRINTED_FAULT, error)

    return models.ResolutionSheet.bulk_create(exam_id, date, course, sheets_num)
