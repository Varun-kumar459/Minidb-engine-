"""Scripted tour of every feature:   python demo.py"""
from minidb import Database, DBError
from minidb.formatter import format_table

db = Database()


def run(sql, note=None):
    if note:
        print(f"\n# {note}")
    print(f"minidb> {' '.join(sql.split())}")
    try:
        r = db.execute(sql)
    except DBError as e:
        print(f"Error: {e}")
        return
    if r.is_query:
        print(format_table(r.columns, r.rows))
        if r.examined is not None:
            print(f"(examined {r.examined} row(s))")
    else:
        print(r.message)


print("=" * 64 + "\n MiniDB demo\n" + "=" * 64)
with open("examples/school.sql", encoding="utf-8") as f:
    setup = f.read().split("SELECT dept")[0]
for stmt in db.execute_script(setup):
    pass
print("Loaded examples/school.sql (3 tables)")

run("SHOW TABLES", "1. Tables in the database")
run("DESCRIBE students", "2. Table structure")
run("SELECT name, cgpa FROM students WHERE cgpa >= 7 AND dept = 'CSE' ORDER BY cgpa DESC",
    "3. Filtering and sorting")
run("SELECT name FROM students WHERE cgpa IS NULL", "4. NULL handling (cgpa = NULL would match nothing)")
run("SELECT name FROM students WHERE name LIKE '%a' ", "5. Pattern matching")
run("""SELECT s.name, c.title, e.grade FROM enrollments e
       JOIN students s ON e.student_id = s.id
       JOIN courses c ON e.course_code = c.code
       WHERE e.grade >= 85 ORDER BY e.grade DESC""", "6. Joining three tables")
run("SELECT s.name, e.course_code FROM students s LEFT JOIN enrollments e ON e.student_id = s.id "
    "WHERE e.id IS NULL", "7. LEFT JOIN: students with no enrollments")
run("SELECT dept, COUNT(*) AS students, AVG(cgpa) AS avg_cgpa FROM students "
    "GROUP BY dept ORDER BY students DESC", "8. GROUP BY with aggregates")
run("UPDATE students SET cgpa = cgpa + 0.2 WHERE dept = 'ECE'", "9. UPDATE with an expression")
run("INSERT INTO students VALUES (1, 'Duplicate', 'CSE', 5.0)", "10. Constraint: PRIMARY KEY must be unique")
run("INSERT INTO students VALUES (6, 'Ok', 'CSE', 7.0), (6, 'Clash', 'CSE', 7.0)",
    "11. Failed multi-row INSERT is rolled back completely")
run("SELECT COUNT(*) FROM students", "    (still 5 rows - nothing was half-inserted)")

run("BEGIN", "12. Transactions")
run("DELETE FROM enrollments")
run("SELECT COUNT(*) FROM enrollments")
run("ROLLBACK")
run("SELECT COUNT(*) FROM enrollments", "    (the 6 enrollments are back)")

run("EXPLAIN SELECT * FROM students WHERE name = 'Asha'", "13. Query planner: no index yet")
run("CREATE INDEX ON students (name)")
run("EXPLAIN SELECT * FROM students WHERE name = 'Asha'", "    ...and after CREATE INDEX")
run("SELECT * FROM students WHERE name = 'Asha'")
