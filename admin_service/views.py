from xmlrpc import client

from flask import abort, redirect, render_template, request

import models
import utils
from settings import ALREADY_PRINTED_FAULT, PRINTING_API, PRINTING_SERVICE


def index():
    return redirect("/exams")


def listExams():
    return render_template("listExams.html", exams=models.Exam.all())


def scheduleExam():
    if request.method == "GET":
        return render_template("scheduleExam.html")
    else:
        date = request.form["date"]
        course = request.form["course"].strip()

        error = models.Exam.validate(date, course)

        if error:
            return render_template(
                "scheduleExam.html", error=error, date=date, course=course
            )

        models.Exam.create(date, course)

        return redirect("/exams")


def enrollExam(examId):
    exam = models.Exam.get(examId)

    if exam is None:
        abort(404)

    if request.method == "GET":
        return render_template("enrollExam.html", exam=exam)
    else:
        text = request.form["studentIds"]
        studentIds, errors = utils.parseStudentIds(text)

        if not studentIds and not errors:
            errors = ["no student ids given"]

        if errors:
            return render_template(
                "enrollExam.html", exam=exam, studentIdsText=text, errors=errors
            )

        newIds = models.Enrollment.bulkCreate(exam.id, studentIds)

        return render_template(
            "enrollExam.html",
            exam=exam,
            newIds=newIds,
            skipped=len(set(studentIds)) - len(newIds),
        )


def orderPrinting(examId):
    exam = models.Exam.get(examId)
    if exam is None:
        abort(404)

    if request.method == "GET":
        return render_template("orderPrinting.html", exam=exam)

    if not exam.enrollments:
        return render_template(
            "orderPrinting.html", exam=exam, error="no students enrolled"
        )

    pdfUrl = f"{PRINTING_SERVICE}/exams/{exam.id}/pdf"
    proxy = client.ServerProxy(PRINTING_API)
    try:
        sheetIds = proxy.printExam(
            exam.id, exam.date.isoformat(), exam.course, len(exam.enrollments)
        )
    except client.Fault as err:
        if err.faultCode == ALREADY_PRINTED_FAULT:
            return render_template(
                "orderPrinting.html", exam=exam, error=err.faultString, pdfUrl=pdfUrl
            )

        error = err.faultString
    except (client.ProtocolError, OSError):
        error = "printing service unavailable"
    else:
        return render_template(
            "orderPrinting.html", exam=exam, sheetIds=sheetIds, pdfUrl=pdfUrl
        )

    return render_template("orderPrinting.html", exam=exam, error=error)


def listEnrollments():
    return render_template("listEnrollments.html", enrollments=models.Enrollment.all())
