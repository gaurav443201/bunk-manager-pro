def get_curriculum(division, batch):
    """
    Returns (subjects_list, daily_schedule) for the given SE division (A or B) and batch (A/B/C/D).
    NOTE: MIL is called 'Modern Indian Languages' in the user's corrected data.
    Practicals are added TWICE to daily_schedule for 2-hour duration weighting.
    """
    division = division.upper().strip()
    batch = batch.upper().strip()

    daily_schedule = {
        "Monday": [], "Tuesday": [], "Wednesday": [],
        "Thursday": [], "Friday": [], "Saturday": []
    }
    subjects_dict = {}

    def lec(day, name):
        daily_schedule[day].append({"subject_name": name, "subject_type": "Lecture"})
        subjects_dict[(name, "Lecture", "")] = {
            "subject_name": name, "subject_type": "Lecture",
            "batch": "", "exclude_attendance": False
        }

    def prac(day, name):
        daily_schedule[day].append({"subject_name": name, "subject_type": "Practical"})
        subjects_dict[(name, "Practical", batch)] = {
            "subject_name": name, "subject_type": "Practical",
            "batch": batch, "exclude_attendance": False
        }

    if division == 'A':
        # ── MONDAY ──────────────────────────────────────────────
        for l in ["Database Management System", "Discrete Mathematics", "Open Elective"]:
            lec("Monday", l)
        if batch == 'A':   prac("Monday", "Web Development Lab")
        elif batch == 'B': prac("Monday", "Database Management System Lab")
        elif batch == 'C': prac("Monday", "Database Management System Lab")
        elif batch == 'D': prac("Monday", "Microprocessor Lab")

        # ── TUESDAY ─────────────────────────────────────────────
        for l in ["Internet of Things", "Computer Organization", "Modern Indian Languages"]:
            lec("Tuesday", l)
        if batch == 'A':
            prac("Tuesday", "Database Management System Lab")
            prac("Tuesday", "Web Development Lab")
        elif batch == 'B':
            prac("Tuesday", "Web Development Lab")
            prac("Tuesday", "Microprocessor Lab")
        elif batch == 'C': prac("Tuesday", "Microprocessor Lab")
        # batch D: no practical

        # ── WEDNESDAY ───────────────────────────────────────────
        for l in ["Open Elective", "Environmental Studies", "Discrete Mathematics"]:
            lec("Wednesday", l)
        if batch == 'A':   prac("Wednesday", "Engineering Project Development Lab")
        elif batch == 'B': prac("Wednesday", "Microprocessor Lab")
        elif batch == 'C': prac("Wednesday", "Web Development Lab")
        elif batch == 'D': prac("Wednesday", "Database Management System Lab")

        # ── THURSDAY ────────────────────────────────────────────
        for l in ["Internet of Things", "Discrete Mathematics", "Database Management System"]:
            lec("Thursday", l)
        if batch == 'A':
            prac("Thursday", "Microprocessor Lab")
            prac("Thursday", "Modern Indian Languages")
        elif batch == 'B': prac("Thursday", "Web Development Lab")
        elif batch == 'C': prac("Thursday", "Database Management System Lab")
        elif batch == 'D': prac("Thursday", "Engineering Project Development Lab")

        # ── FRIDAY ──────────────────────────────────────────────
        for l in ["Computer Organization", "Environmental Studies", "Engineering Project Development"]:
            lec("Friday", l)
        if batch == 'A':   prac("Friday", "Engineering Project Development Lab")
        elif batch == 'B': prac("Friday", "Modern Indian Languages")
        elif batch == 'C': prac("Friday", "Modern Indian Languages")
        elif batch == 'D': prac("Friday", "Web Development Lab")

    elif division == 'B':
        # ── MONDAY ──────────────────────────────────────────────
        for l in ["Database Management System", "Open Elective", "Discrete Mathematics"]:
            lec("Monday", l)
        if batch == 'A':
            prac("Monday", "Database Management System Lab")
            prac("Monday", "Engineering Project Development Lab")
        elif batch == 'B': prac("Monday", "Modern Indian Languages")
        elif batch == 'C':
            prac("Monday", "Web Development Lab")
            prac("Monday", "Modern Indian Languages")
        # batch D: no practical

        # ── TUESDAY ─────────────────────────────────────────────
        for l in ["Computer Organization", "Internet of Things", "Database Management System"]:
            lec("Tuesday", l)
        if batch == 'A': prac("Tuesday", "Web Development Lab")
        elif batch == 'B': prac("Tuesday", "Database Management System Lab")
        elif batch == 'C':
            prac("Tuesday", "Microprocessor Lab")
            prac("Tuesday", "Web Development Lab")
        # batch D: no practical

        # ── WEDNESDAY ───────────────────────────────────────────
        for l in ["Open Elective", "Modern Indian Languages", "Discrete Mathematics"]:
            lec("Wednesday", l)
        if batch == 'A': prac("Wednesday", "Web Development Lab")
        elif batch == 'B': prac("Wednesday", "Microprocessor Lab")
        # batch C: no practical
        elif batch == 'D': prac("Wednesday", "Database Management System Lab")

        # ── THURSDAY ────────────────────────────────────────────
        for l in ["Internet of Things", "Discrete Mathematics", "Database Management System"]:
            lec("Thursday", l)
        if batch == 'A':
            prac("Thursday", "Microprocessor Lab")
            prac("Thursday", "Modern Indian Languages")
        elif batch == 'B': prac("Thursday", "Web Development Lab")
        elif batch == 'C': prac("Thursday", "Database Management System Lab")
        elif batch == 'D': prac("Thursday", "Engineering Project Development Lab")

        # ── FRIDAY ──────────────────────────────────────────────
        for l in ["Engineering Project Development", "Environmental Studies", "Computer Organization"]:
            lec("Friday", l)
        # batches A, B, C: no practical
        if batch == 'D': prac("Friday", "Modern Indian Languages")


    return list(subjects_dict.values()), daily_schedule
