from io import BytesIO
from xmlrpc.client import Fault

from flask import abort, redirect, render_template, send_file

import models
import utils
from settings import ALREADY_PRINTED_FAULT, INVALID_DATA_FAULT


def index():
    return redirect("/exams")


def listExams():
    return render_template("listExams.html", exams=models.ResolutionSheet.exams())


def downloadExamPdf(examId):
    sheets = models.ResolutionSheet.forExam(examId)
    if not sheets:
        abort(404)

    pdfs = []
    for sheet in sheets:
        pdfs.append(sheet.pdf)
    pdf = utils.mergePdfs(pdfs)

    return send_file(
        BytesIO(pdf),
        mimetype="application/pdf",
        download_name=f"exam-{examId}.pdf",
    )


def printExam(examId, date, course, sheetsNum):
    error = models.ResolutionSheet.validate(examId, date, course, sheetsNum)

    if error:
        raise Fault(INVALID_DATA_FAULT, error)

    if models.ResolutionSheet.isPrinted(examId):
        error = f"exam {examId} already has resolution sheets"
        raise Fault(ALREADY_PRINTED_FAULT, error)

    return models.ResolutionSheet.bulkCreate(examId, date, course, sheetsNum)
