import views


def register_urls(app):
    app.add_url_rule("/", view_func=views.index)

    app.add_url_rule("/exams", view_func=views.list_exams)
    app.add_url_rule(
        "/exams/create", view_func=views.schedule_exam, methods=["GET", "POST"]
    )
    app.add_url_rule(
        "/exams/<int:exam_id>/enroll",
        view_func=views.enroll_exam,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/exams/<int:exam_id>/print",
        view_func=views.order_printing,
        methods=["GET", "POST"],
    )

    app.add_url_rule("/enrollments", view_func=views.list_enrollments)
