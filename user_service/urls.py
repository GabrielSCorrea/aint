import views


def register_urls(app):
    app.add_url_rule("/", view_func=views.index)

    app.add_url_rule("/users", view_func=views.list_users)
    app.add_url_rule("/users/create", view_func=views.add_user, methods=["GET", "POST"])
    app.add_url_rule(
        "/users/bulk", view_func=views.bulk_add_users, methods=["GET", "POST"]
    )
