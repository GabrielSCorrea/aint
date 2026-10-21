from io import BytesIO
from xmlrpc.client import Fault

from flask import abort, redirect, render_template, send_file

import models
import utils


def index():
    return redirect("/exams")


def listExams():
    return render_template("listExams.html", exams=models.ResolutionSheet.exams())


def downloadExamPdf(examId):
    sheets = models.ResolutionSheet.forExam(examId)
    if not sheets:
        abort(404)
    pdf = utils.mergePdfs([sheet.pdf for sheet in sheets])
    return send_file(
        BytesIO(pdf),
        mimetype="application/pdf",
        download_name="exam-%d.pdf" % examId,
    )


def printExam(examId, date, course, sheetsNum):
    error = models.ResolutionSheet.validate(examId, date, course, sheetsNum)
    if error is None and models.ResolutionSheet.isPrinted(examId):
        error = "exam %d already has resolution sheets" % examId
    if error:
        raise Fault(1, error)
    return models.ResolutionSheet.bulkCreate(examId, date, course, sheetsNum)
