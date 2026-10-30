def parse_student_ids(text):
    student_ids = []
    errors = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue

        try:
            student_id = int(line)
        except ValueError:
            student_id = -1

        if student_id < 1:
            error = f"'{line}' is not a valid student id"
            errors.append(f"line {line_number}: {error}")
        else:
            student_ids.append(student_id)

    return student_ids, errors
