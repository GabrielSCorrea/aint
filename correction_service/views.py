from io import BytesIO

from flask import abort, redirect, render_template, request, send_file

import models
import utils
from settings import MAX_GRADE, QUESTIONS


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


def index():
    return redirect("/corrections")


# AD_4 - list professor assignments
def listAssignments():
    return render_template(
        "listAssignments.html", assignments=models.ProfessorAssignment.all()
    )


# AD_4 - assign a professor to the correction of an exam question
def assignProfessor():
    if request.method == "GET":
        return render_template("assignProfessor.html", questions=QUESTIONS)
    else:
        examId = parseInt(request.form["examId"])
        questionNumber = parseInt(request.form["questionNumber"])
        professorId = parseInt(request.form["professorId"])
        error = models.ProfessorAssignment.validate(examId, questionNumber, professorId)
        if error:
            return render_template(
                "assignProfessor.html",
                questions=QUESTIONS,
                error=error,
                examId=request.form["examId"],
                questionNumber=questionNumber,
                professorId=request.form["professorId"],
            )
        models.ProfessorAssignment.assign(examId, questionNumber, professorId)
        return redirect("/assignments")


# AD_5 - list uploaded scans
def listScans():
    return render_template("listScans.html", scans=models.ExamCorrectionPdf.all())


# AD_5 - upload the scan of an exam's resolutions
def uploadScan():
    if request.method == "GET":
        return render_template("uploadScan.html")
    else:
        examIdText = request.form["examId"]
        examId = parseInt(examIdText)
        file = request.files.get("pdf")
        error = models.ExamCorrectionPdf.validate(examId)
        if error is None and (not file or not file.filename):
            error = "no PDF file given"
        if error is None:
            pdf = file.read()
            try:
                pages = utils.splitScan(pdf)
            except ValueError as err:
                error = str(err)
        if error is None:
            uploaded = models.QuestionCorrection.uploadedSheets(
                {sheetId for sheetId, _, _ in pages}
            )
            if uploaded:
                error = "sheet(s) already uploaded: %s" % ", ".join(map(str, uploaded))
        if error:
            return render_template("uploadScan.html", error=error, examId=examIdText)
        models.ExamCorrectionPdf.create(examId, pdf, pages)
        return redirect("/scans")


def downloadScan(examPdfId):
    examPdf = models.ExamCorrectionPdf.get(examPdfId)
    if examPdf is None:
        abort(404)
    return send_file(
        BytesIO(examPdf.pdf),
        mimetype="application/pdf",
        download_name="scan-%d.pdf" % examPdf.id,
    )


# PR_1 - list resolutions waiting for correction (of every professor in part 1)
def listPending():
    return render_template(
        "listCorrections.html",
        title="Answers to Correct",
        corrections=models.QuestionCorrection.listWithProfessor(False),
    )


# PR_3 - list corrected answers
def listCorrected():
    return render_template(
        "listCorrections.html",
        title="Corrected Answers",
        corrections=models.QuestionCorrection.listWithProfessor(True),
    )


# PR_2 - correct an answer
def correctAnswer(correctionId):
    correction = models.QuestionCorrection.get(correctionId)
    if correction is None:
        abort(404)
    if request.method == "GET":
        return render_template(
            "correctAnswer.html", correction=correction, maxGrade=MAX_GRADE
        )
    else:
        gradeText = request.form["grade"]
        grade = parseGrade(gradeText)
        error = models.QuestionCorrection.validateGrade(grade)
        if error:
            return render_template(
                "correctAnswer.html",
                correction=correction,
                maxGrade=MAX_GRADE,
                error=error,
                gradeText=gradeText,
            )
        correction.correct(grade)
        return redirect("/corrections")


def correctionImage(correctionId):
    correction = models.QuestionCorrection.get(correctionId)
    if correction is None:
        abort(404)
    return send_file(BytesIO(correction.image), mimetype="image/png")


# ST_3 - list resolution sheets and their grades
def listResolutions():
    return render_template(
        "listResolutions.html",
        sheets=models.QuestionCorrection.sheets(),
        questions=QUESTIONS,
    )


# ST_3 - see a resolution's scans and corrections
def showResolution(sheetId):
    corrections = models.QuestionCorrection.forSheet(sheetId)
    if not corrections:
        abort(404)
    total = None
    if all(c.evaluated for c in corrections):
        total = sum(c.grade for c in corrections)
    return render_template(
        "showResolution.html", sheetId=sheetId, corrections=corrections, total=total
    )
