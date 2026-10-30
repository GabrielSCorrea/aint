from io import BytesIO

from flask import abort, redirect, render_template, request, send_file

import models
import utils
from settings import MAX_GRADE, QUESTIONS


def index():
    return redirect("/corrections")


def listAssignments():
    return render_template(
        "listAssignments.html", assignments=models.ProfessorAssignment.all()
    )


def assignProfessor():
    if request.method == "GET":
        return render_template("assignProfessor.html", questions=QUESTIONS)
    else:
        examId = utils.parseInt(request.form["examId"])
        questionNumber = utils.parseInt(request.form["questionNumber"])
        professorId = utils.parseInt(request.form["professorId"])

        error = models.ProfessorAssignment.validate(examId, questionNumber, professorId)
        if error is None:
            assignment = models.ProfessorAssignment.get(examId, questionNumber)
            if assignment is not None:
                error = f"question {questionNumber} of exam {examId} is already assigned to professor {assignment.professorId}"
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


def listScans():
    return render_template("listScans.html", scans=models.ExamCorrectionPdf.all())


def uploadScan():
    if request.method == "GET":
        return render_template("uploadScan.html")
    else:
        examIdText = request.form["examId"]
        examId = utils.parseInt(examIdText)
        file = request.files.get("pdf")

        error = models.ExamCorrectionPdf.validate(examId)
        if error is None and not file:
            error = "no PDF file given"

        if error is None:
            pdf = file.read()
            try:
                pages = utils.splitScan(pdf)
            except ValueError as err:
                error = str(err)

        if error is None:
            sheetIds = []
            for sheetId, _, _ in pages:
                sheetIds.append(sheetId)

            uploaded = models.QuestionCorrection.uploadedSheets(sheetIds)
            if uploaded:
                error = f"sheet(s) already uploaded: {', '.join(map(str, uploaded))}"

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
        download_name=f"scan-{examPdf.id}.pdf",
    )


def listPending():
    return render_template(
        "listCorrections.html",
        title="Answers to Correct",
        corrections=models.QuestionCorrection.listWithProfessor(False),
    )


def listCorrected():
    return render_template(
        "listCorrections.html",
        title="Corrected Answers",
        corrections=models.QuestionCorrection.listWithProfessor(True),
    )


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
        grade = utils.parseGrade(gradeText)

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


def listResolutions():
    return render_template(
        "listResolutions.html",
        sheets=models.QuestionCorrection.sheets(),
        questions=QUESTIONS,
    )


def showResolution(sheetId):
    corrections = models.QuestionCorrection.forSheet(sheetId)
    if not corrections:
        abort(404)

    total = 0
    for correction in corrections:
        if not correction.evaluated:
            total = None
            break

        total += correction.grade

    return render_template(
        "showResolution.html", sheetId=sheetId, corrections=corrections, total=total
    )
