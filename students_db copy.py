# Final program
#12-18-25
#Mark and Devin

import sqlite3

FIELDS = [
    "FirstName",
    "LastName",
    "Major",
    "GPA",
    "CreditsCompleted",
    "Email",
    "Standing",
    "IsFullTime",
    "GradYear"
]

def main():
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    add_students_table(cur)
    add_sample_students(cur)
    conn.commit()

    # Mainline menu: display + edit loop
    menu_loop(conn, cur)

    conn.close()
    print("\nDone. students.db saved successfully.")

def add_students_table(cur):
    """Create the Students table (drop first if it exists)."""
    cur.execute('DROP TABLE IF EXISTS Students')
    cur.execute('''
        CREATE TABLE Students (
            StudentID INTEGER PRIMARY KEY NOT NULL,
            FirstName TEXT,
            LastName TEXT,
            Major TEXT,
            GPA REAL,
            CreditsCompleted INTEGER,
            Email TEXT,
            Standing TEXT,
            IsFullTime INTEGER,
            GradYear INTEGER
        )
    ''')

def add_sample_students(cur):
    """Insert sample rows for testing."""
    students = [
        (1, 'Alex',    'Johnson',  'Computer Science', 3.6,  45, 'alex.johnson@example.edu',  'Sophomore', 1, 2027),
        (2, 'Maria',   'Lopez',    'Nursing',          3.9,  75, 'maria.lopez@example.edu',   'Junior',    1, 2026),
        (3, 'Jamal',   'Carter',   'Business',         2.8,  30, 'jamal.carter@example.edu',  'Freshman',  1, 2028),
        (4, 'Sofia',   'Nguyen',   'Psychology',       3.4,  90, 'sofia.nguyen@example.edu',  'Senior',    1, 2025),
        (5, 'Ethan',   'Kim',      'Engineering',      3.1,  60, 'ethan.kim@example.edu',     'Junior',    1, 2026),
        (6, 'Layla',   'Patel',    'Art',              3.7,  18, 'layla.patel@example.edu',   'Freshman',  0, 2029),
        (7, 'Noah',    'Williams', 'Cybersecurity',    2.9,  33, 'noah.williams@example.edu', 'Sophomore', 1, 2027),
        (8, 'Grace',   'Miller',   'Biology',          3.5, 105, 'grace.miller@example.edu',  'Senior',    1, 2025),
        (9, 'Omar',    'Ali',      'Data Science',     3.2,  48, 'omar.ali@example.edu',      'Sophomore', 1, 2027),
        (10,'Faith',   'Brown',    'Theology',         3.8,  72, 'faith.brown@example.edu',   'Junior',    1, 2026)
    ]

    for row in students:
        cur.execute('''
            INSERT INTO Students
            (StudentID, FirstName, LastName, Major, GPA,
             CreditsCompleted, Email, Standing, IsFullTime, GradYear)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', row)

def display_students(cur):
    """Print all students in a nice format."""
    print("\nContents of Students table:\n")
    cur.execute('SELECT StudentID, FirstName, LastName, Major, GPA, Standing, GradYear FROM Students')
    results = cur.fetchall()

    print(f"{'ID':<3} {'Name':25} {'Major':20} {'GPA':<5} {'Standing':10} {'GradYear'}")
    print("-" * 80)
    for row in results:
        student_id = row[0]
        full_name = f"{row[1]} {row[2]}"
        major = row[3]
        gpa = row[4]
        standing = row[5]
        grad_year = row[6]
        print(f"{student_id:<3} {full_name:25} {major:20} {gpa:<5.2f} {standing:10} {grad_year}")

def menu_loop(conn, cur):
    """Mainline loop that shows records and allows editing any record."""
    while True:
        print("\n--- Student Database Menu ---")
        print("1) Display all students")
        print("2) Edit a student record")
        print("3) Quit")
        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            display_students(cur)

        elif choice == "2":
            edit_student(conn, cur)

        elif choice == "3":
            break

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def edit_student(conn, cur):
    """Edit any field for one student by StudentID."""
    try:
        student_id = int(input("Enter the StudentID to edit: ").strip())
    except ValueError:
        print("StudentID must be a number.")
        return

    cur.execute("SELECT StudentID, FirstName, LastName, Major, GPA, CreditsCompleted, Email, Standing, IsFullTime, GradYear FROM Students WHERE StudentID = ?",
                (student_id,))
    row = cur.fetchone()

    if not row:
        print(f"No student found with ID {student_id}.")
        return

    print("\nCurrent record:")
    print_record(row)

    # Show editable fields
    print("\nWhich field do you want to edit?")
    for i, field in enumerate(FIELDS, start=1):
        print(f"{i}) {field}")

    print("0) Cancel")
    pick = input("Enter a number (0-9): ").strip()

    if pick == "0":
        print("Edit canceled.")
        return

    try:
        pick_num = int(pick)
        if not (1 <= pick_num <= len(FIELDS)):
            raise ValueError
    except ValueError:
        print("Invalid selection.")
        return

    field_name = FIELDS[pick_num - 1]
    new_value_raw = input(f"Enter new value for {field_name}: ").strip()

    # Convert types for numeric fields
    try:
        new_value = convert_field_value(field_name, new_value_raw)
    except ValueError as e:
        print(f"Invalid value: {e}")
        return

    # Update
    cur.execute(f"UPDATE Students SET {field_name} = ? WHERE StudentID = ?", (new_value, student_id))
    conn.commit()

    print("\nRecord updated successfully.")
    cur.execute("SELECT StudentID, FirstName, LastName, Major, GPA, CreditsCompleted, Email, Standing, IsFullTime, GradYear FROM Students WHERE StudentID = ?",
                (student_id,))
    updated = cur.fetchone()
    print("Updated record:")
    print_record(updated)

def convert_field_value(field_name, raw):
    """Convert input text to correct data type for the chosen field."""
    if field_name == "GPA":
        val = float(raw)
        if val < 0.0 or val > 4.0:
            raise ValueError("GPA should be between 0.0 and 4.0.")
        return val

    if field_name in ("CreditsCompleted", "GradYear"):
        return int(raw)

    if field_name == "IsFullTime":
        # Accept 0/1, yes/no, true/false
        lowered = raw.lower()
        if lowered in ("1", "yes", "y", "true", "t"):
            return 1
        if lowered in ("0", "no", "n", "false", "f"):
            return 0
        raise ValueError("IsFullTime must be 1/0 or yes/no.")

    # Everything else is text
    if field_name == "Email" and "@" not in raw:
        # light validation
        raise ValueError("Email must contain '@'.")
    return raw

def print_record(row):
    """Pretty-print a full student record row."""
    (sid, first, last, major, gpa, credits, email, standing, full_time, grad_year) = row
    print(f"StudentID:         {sid}")
    print(f"FirstName:         {first}")
    print(f"LastName:          {last}")
    print(f"Major:             {major}")
    print(f"GPA:               {gpa}")
    print(f"CreditsCompleted:  {credits}")
    print(f"Email:             {email}")
    print(f"Standing:          {standing}")
    print(f"IsFullTime:        {full_time}  (1=Yes, 0=No)")
    print(f"GradYear:          {grad_year}")

if __name__ == '__main__':
    main()