import views


def register_urls(app):
    app.add_url_rule("/", view_func=views.index)

    app.add_url_rule("/assignments", view_func=views.list_assignments)
    app.add_url_rule(
        "/assignments/create", view_func=views.assign_professor, methods=["GET", "POST"]
    )

    app.add_url_rule("/scans", view_func=views.list_scans)
    app.add_url_rule(
        "/scans/upload", view_func=views.upload_scan, methods=["GET", "POST"]
    )
    app.add_url_rule("/scans/<int:exam_pdf_id>/pdf", view_func=views.download_scan)

    app.add_url_rule("/corrections", view_func=views.list_pending)
    app.add_url_rule("/corrections/done", view_func=views.list_corrected)
    app.add_url_rule(
        "/corrections/<int:correction_id>",
        view_func=views.correct_answer,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/corrections/<int:correction_id>/image", view_func=views.correction_image
    )

    app.add_url_rule("/resolutions", view_func=views.list_resolutions)
    app.add_url_rule("/resolutions/<int:sheet_id>", view_func=views.show_resolution)
