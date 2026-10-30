from xmlrpc import client

from flask import abort, redirect, render_template, request

import models
import utils
from settings import ALREADY_PRINTED_FAULT, PRINTING_API, PRINTING_SERVICE


def index():
    return redirect("/exams")


def list_exams():
    return render_template("list_exams.html", exams=models.Exam.all())


def schedule_exam():
    if request.method == "GET":
        return render_template("schedule_exam.html")
    else:
        date = request.form["date"]
        course = request.form["course"].strip()

        error = models.Exam.validate(date, course)

        if error:
            return render_template(
                "schedule_exam.html", error=error, date=date, course=course
            )

        models.Exam.create(date, course)

        return redirect("/exams")


def enroll_exam(exam_id):
    exam = models.Exam.get(exam_id)

    if exam is None:
        abort(404)

    if request.method == "GET":
        return render_template("enroll_exam.html", exam=exam)
    else:
        text = request.form["student_ids"]
        student_ids, errors = utils.parse_student_ids(text)

        if not student_ids and not errors:
            errors = ["no student ids given"]

        if errors:
            return render_template(
                "enroll_exam.html", exam=exam, student_ids_text=text, errors=errors
            )

        new_ids = models.Enrollment.bulk_create(exam.id, student_ids)

        unique_ids = []
        for student_id in student_ids:
            if student_id not in unique_ids:
                unique_ids.append(student_id)

        return render_template(
            "enroll_exam.html",
            exam=exam,
            new_ids=new_ids,
            skipped=len(unique_ids) - len(new_ids),
        )


def order_printing(exam_id):
    exam = models.Exam.get(exam_id)
    if exam is None:
        abort(404)

    if request.method == "GET":
        return render_template("order_printing.html", exam=exam)

    if not exam.enrollments:
        return render_template(
            "order_printing.html", exam=exam, error="no students enrolled"
        )

    pdf_url = f"{PRINTING_SERVICE}/exams/{exam.id}/pdf"
    proxy = client.ServerProxy(PRINTING_API)
    try:
        sheet_ids = proxy.print_exam(
            exam.id, exam.date.isoformat(), exam.course, len(exam.enrollments)
        )
    except client.Fault as err:
        if err.faultCode == ALREADY_PRINTED_FAULT:
            return render_template(
                "order_printing.html", exam=exam, error=err.faultString, pdf_url=pdf_url
            )

        error = err.faultString
    except (client.ProtocolError, OSError):
        error = "printing service unavailable"
    else:
        return render_template(
            "order_printing.html", exam=exam, sheet_ids=sheet_ids, pdf_url=pdf_url
        )

    return render_template("order_printing.html", exam=exam, error=error)


def list_enrollments():
    return render_template("list_enrollments.html", enrollments=models.Enrollment.all())
