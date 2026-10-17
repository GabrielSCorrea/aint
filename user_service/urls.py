import views


def registerUrls(app):
    app.add_url_rule("/", view_func=views.index)
    app.add_url_rule("/users", view_func=views.listUsers)
    app.add_url_rule("/users/create", view_func=views.addUser, methods=["GET", "POST"])
    app.add_url_rule(
        "/users/bulk", view_func=views.bulkAddUsers, methods=["GET", "POST"]
    )
