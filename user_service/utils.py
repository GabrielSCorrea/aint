import models


def parseUsersText(text):
    users = []
    errors = []
    for lineNumber, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue

        fields = []
        for field in line.split(","):
            fields.append(field.strip())

        if len(fields) != 3:
            errors.append(f"line {lineNumber}: expected name,password,role")
            continue

        name, password, role = fields
        role = role.lower()

        error = models.User.validate(name, password, role)

        if error:
            errors.append(f"line {lineNumber}: {error}")
        else:
            users.append((name, password, role))

    return users, errors
