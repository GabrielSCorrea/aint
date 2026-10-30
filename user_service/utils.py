import models


def parse_users_text(text):
    users = []
    errors = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue

        fields = []
        for field in line.split(","):
            fields.append(field.strip())

        if len(fields) != 3:
            errors.append(f"line {line_number}: expected name,password,role")
            continue

        name, password, role = fields
        role = role.lower()

        error = models.User.validate(name, password, role)

        if error:
            errors.append(f"line {line_number}: {error}")
        else:
            users.append((name, password, role))

    return users, errors
