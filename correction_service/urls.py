import views


def registerUrls(app):
    app.add_url_rule("/", view_func=views.index)
    app.add_url_rule("/assignments", view_func=views.listAssignments)
    app.add_url_rule(
        "/assignments/create", view_func=views.assignProfessor, methods=["GET", "POST"]
    )
    app.add_url_rule("/scans", view_func=views.listScans)
    app.add_url_rule(
        "/scans/upload", view_func=views.uploadScan, methods=["GET", "POST"]
    )
    app.add_url_rule("/scans/<int:examPdfId>/pdf", view_func=views.downloadScan)
    app.add_url_rule("/corrections", view_func=views.listPending)
    app.add_url_rule("/corrections/done", view_func=views.listCorrected)
    app.add_url_rule(
        "/corrections/<int:correctionId>",
        view_func=views.correctAnswer,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/corrections/<int:correctionId>/image", view_func=views.correctionImage
    )
    app.add_url_rule("/resolutions", view_func=views.listResolutions)
    app.add_url_rule("/resolutions/<int:sheetId>", view_func=views.showResolution)
