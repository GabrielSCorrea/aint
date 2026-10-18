import views


def registerUrls(app):
    app.add_url_rule("/", view_func=views.index)
    app.add_url_rule("/exams", view_func=views.listExams)
    app.add_url_rule(
        "/exams/create", view_func=views.scheduleExam, methods=["GET", "POST"]
    )
    app.add_url_rule(
        "/exams/<int:examId>/enroll",
        view_func=views.enrollExam,
        methods=["GET", "POST"],
    )
    app.add_url_rule("/enrollments", view_func=views.listEnrollments)
