from io import BytesIO

from flask import abort, redirect, render_template, request, send_file

import models
import utils
from settings import MAX_GRADE, QUESTIONS


def index():
    return redirect("/corrections")


def list_assignments():
    return render_template(
        "list_assignments.html", assignments=models.ProfessorAssignment.all()
    )


def assign_professor():
    if request.method == "GET":
        return render_template("assign_professor.html", questions=QUESTIONS)
    else:
        exam_id = utils.parse_int(request.form["exam_id"])
        question_number = utils.parse_int(request.form["question_number"])
        professor_id = utils.parse_int(request.form["professor_id"])

        error = models.ProfessorAssignment.validate(
            exam_id, question_number, professor_id
        )
        if error is None:
            assignment = models.ProfessorAssignment.get(exam_id, question_number)
            if assignment is not None:
                error = f"question {question_number} of exam {exam_id} is already assigned to professor {assignment.professor_id}"
        if error:
            return render_template(
                "assign_professor.html",
                questions=QUESTIONS,
                error=error,
                exam_id=request.form["exam_id"],
                question_number=question_number,
                professor_id=request.form["professor_id"],
            )

        models.ProfessorAssignment.assign(exam_id, question_number, professor_id)

        return redirect("/assignments")


def list_scans():
    return render_template("list_scans.html", scans=models.ExamCorrectionPdf.all())


def upload_scan():
    if request.method == "GET":
        return render_template("upload_scan.html")
    else:
        exam_id_text = request.form["exam_id"]
        exam_id = utils.parse_int(exam_id_text)
        file = request.files.get("pdf")

        error = models.ExamCorrectionPdf.validate(exam_id)
        if error is None and not file:
            error = "no PDF file given"

        if error is None:
            pdf = file.read()
            try:
                pages = utils.split_scan(pdf)
            except ValueError as err:
                error = str(err)

        if error is None:
            sheet_ids = []
            for sheet_id, _, _ in pages:
                sheet_ids.append(sheet_id)

            uploaded = models.QuestionCorrection.uploaded_sheets(sheet_ids)
            if uploaded:
                error = f"sheet(s) already uploaded: {', '.join(map(str, uploaded))}"

        if error:
            return render_template(
                "upload_scan.html", error=error, exam_id=exam_id_text
            )

        models.ExamCorrectionPdf.create(exam_id, pdf, pages)

        return redirect("/scans")


def download_scan(exam_pdf_id):
    exam_pdf = models.ExamCorrectionPdf.get(exam_pdf_id)

    if exam_pdf is None:
        abort(404)

    return send_file(
        BytesIO(exam_pdf.pdf),
        mimetype="application/pdf",
        download_name=f"scan-{exam_pdf.id}.pdf",
    )


def list_pending():
    return render_template(
        "list_corrections.html",
        title="Answers to Correct",
        corrections=models.QuestionCorrection.list_with_professor(False),
    )


def list_corrected():
    return render_template(
        "list_corrections.html",
        title="Corrected Answers",
        corrections=models.QuestionCorrection.list_with_professor(True),
    )


def correct_answer(correction_id):
    correction = models.QuestionCorrection.get(correction_id)
    if correction is None:
        abort(404)

    if request.method == "GET":
        return render_template(
            "correct_answer.html", correction=correction, max_grade=MAX_GRADE
        )
    else:
        grade_text = request.form["grade"]
        grade = utils.parse_grade(grade_text)

        error = models.QuestionCorrection.validate_grade(grade)

        if error:
            return render_template(
                "correct_answer.html",
                correction=correction,
                max_grade=MAX_GRADE,
                error=error,
                grade_text=grade_text,
            )

        correction.correct(grade)

        return redirect("/corrections")


def correction_image(correction_id):
    correction = models.QuestionCorrection.get(correction_id)
    if correction is None:
        abort(404)

    return send_file(BytesIO(correction.image), mimetype="image/png")


def list_resolutions():
    return render_template(
        "list_resolutions.html",
        sheets=models.QuestionCorrection.sheets(),
        questions=QUESTIONS,
    )


def show_resolution(sheet_id):
    corrections = models.QuestionCorrection.for_sheet(sheet_id)
    if not corrections:
        abort(404)

    total = 0
    for correction in corrections:
        if not correction.evaluated:
            total = None
            break

        total += correction.grade

    return render_template(
        "show_resolution.html", sheet_id=sheet_id, corrections=corrections, total=total
    )
