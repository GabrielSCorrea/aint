import csv

from flask import redirect, render_template, request

import models


def parseUsersText(text):
    users = []
    errors = []
    for lineNumber, fields in enumerate(csv.reader(text.splitlines()), start=1):
        if all(f.strip() == "" for f in fields):
            continue
        if len(fields) != 3:
            errors.append("line %d: expected name,password,role" % lineNumber)
            continue
        name, password, role = [f.strip() for f in fields]
        role = role.lower()
        error = models.User.validate(name, password, role)
        if error:
            errors.append("line %d: %s" % (lineNumber, error))
        else:
            users.append((name, password, role))
    return users, errors


def index():
    return redirect("/users")


# SU_1 - list users
def listUsers():
    return render_template("listUsers.html", users=models.User.all())


# SU_2 - add user
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


# SU_3 - bulk add users
def bulkAddUsers():
    if request.method == "GET":
        return render_template("bulkAddUsers.html", roles=models.ROLES)
    else:
        text = request.form["usersText"]
        users, errors = parseUsersText(text)
        if not users and not errors:
            errors = ["no users given"]
        if errors:
            return render_template(
                "bulkAddUsers.html", roles=models.ROLES, usersText=text, errors=errors
            )
        models.User.bulkCreate(users)
        return redirect("/users")
