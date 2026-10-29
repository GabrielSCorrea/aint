def parseStudentIds(text):
    studentIds = []
    errors = []
    for lineNumber, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue

        try:
            studentId = int(line)
        except ValueError:
            studentId = -1

        if studentId < 1:
            error = f"'{line}' is not a valid student id"
            errors.append(f"line {lineNumber}: {error}")
        else:
            studentIds.append(studentId)

    return studentIds, errors
