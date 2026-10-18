from flask import abort, redirect, render_template, request

import models


def parseStudentIds(text):
    studentIds = []
    errors = []
    for lineNumber, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            studentId = int(line)
        except ValueError:
            studentId = 0
        if studentId < 1:
            error = "'%s' is not a valid student id" % line
            errors.append("line %d: %s" % (lineNumber, error))
        else:
            studentIds.append(studentId)
    return studentIds, errors


def index():
    return redirect("/exams")


# AD_1 - list scheduled exams
def listExams():
    return render_template("listExams.html", exams=models.Exam.all())


# AD_1 - schedule an exam
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


# AD_2 - bulk enroll students in an exam
def enrollExam(examId):
    exam = models.Exam.get(examId)
    if exam is None:
        abort(404)
    if request.method == "GET":
        return render_template("enrollExam.html", exam=exam)
    else:
        text = request.form["studentIds"]
        studentIds, errors = parseStudentIds(text)
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


# ST_1 - list student enrollments in exams
def listEnrollments():
    return render_template("listEnrollments.html", enrollments=models.Enrollment.all())
