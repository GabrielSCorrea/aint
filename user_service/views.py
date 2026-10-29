from flask import redirect, render_template, request

import models
import utils


def index():
    return redirect("/users")


def listUsers():
    return render_template("listUsers.html", users=models.User.all())


def addUser():
    if request.method == "GET":
        return render_template("addUser.html", roles=models.ROLES)
    else:
        name = request.form["name"].strip()
        password = request.form["password"]
        role = request.form["role"]

        error = models.User.validate(name, password, role)

        if error:
            return render_template(
                "addUser.html", roles=models.ROLES, error=error, name=name, role=role
            )

        models.User.create(name, password, role)

        return redirect("/users")


def bulkAddUsers():
    if request.method == "GET":
        return render_template("bulkAddUsers.html", roles=models.ROLES)
    else:
        text = request.form["usersText"]
        users, errors = utils.parseUsersText(text)

        if not users and not errors:
            errors = ["no users given"]

        if errors:
            return render_template(
                "bulkAddUsers.html", roles=models.ROLES, usersText=text, errors=errors
            )

        models.User.bulkCreate(users)

        return redirect("/users")
