from flask_xmlrpcre.xmlrpcre import XMLRPCHandler

import views


def registerUrls(app):
    app.add_url_rule("/", view_func=views.index)
    app.add_url_rule("/exams", view_func=views.listExams)
    app.add_url_rule("/exams/<int:examId>/pdf", view_func=views.downloadExamPdf)

    handler = XMLRPCHandler("api")
    handler.connect(app, "/api")
    handler.register(views.printExam)
