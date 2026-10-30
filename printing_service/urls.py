from flask_xmlrpcre.xmlrpcre import XMLRPCHandler

import views


def register_urls(app):
    app.add_url_rule("/", view_func=views.index)

    app.add_url_rule("/exams", view_func=views.list_exams)
    app.add_url_rule("/exams/<int:exam_id>/pdf", view_func=views.download_exam_pdf)

    handler = XMLRPCHandler("api")
    handler.connect(app, "/api")
    handler.register(views.print_exam)
