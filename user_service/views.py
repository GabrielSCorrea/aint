from flask import redirect, render_template, request

import models
import utils


def index():
    return redirect("/users")


def list_users():
    return render_template("list_users.html", users=models.User.all())


def add_user():
    if request.method == "GET":
        return render_template("add_user.html", roles=models.ROLES)
    else:
        name = request.form["name"].strip()
        password = request.form["password"]
        role = request.form["role"]

        error = models.User.validate(name, password, role)

        if error:
            return render_template(
                "add_user.html", roles=models.ROLES, error=error, name=name, role=role
            )

        models.User.create(name, password, role)

        return redirect("/users")


def bulk_add_users():
    if request.method == "GET":
        return render_template("bulk_add_users.html", roles=models.ROLES)
    else:
        text = request.form["users_text"]
        users, errors = utils.parse_users_text(text)

        if not users and not errors:
            errors = ["no users given"]

        if errors:
            return render_template(
                "bulk_add_users.html",
                roles=models.ROLES,
                users_text=text,
                errors=errors,
            )

        models.User.bulk_create(users)

        return redirect("/users")
