"""Interactive SQL shell:   python cli.py [--db mydata.json]

End each SQL statement with ';'.   Type .help for shell commands.
"""
import argparse
import sys
import time

from minidb import Database, DBError
from minidb.formatter import format_table
from minidb.parser import split_statements

HELP = """Shell commands:
  .help            show this help
  .tables          list tables
  .read FILE       run all statements in an .sql file
  .quit            exit
SQL examples:
  CREATE TABLE users (id INT PRIMARY KEY, name TEXT NOT NULL, age INT);
  INSERT INTO users VALUES (1, 'Asha', 21), (2, 'Ravi', 25);
  SELECT name, age FROM users WHERE age > 20 ORDER BY age DESC LIMIT 5;
  CREATE INDEX ON users (name);
  EXPLAIN SELECT * FROM users WHERE name = 'Asha';
  BEGIN;  ...  ROLLBACK;  (or COMMIT;)"""


def show(result, seconds):
    if result.is_query:
        print(format_table(result.columns, result.rows))
        extra = f", examined {result.examined}" if result.examined is not None else ""
        print(f"({len(result.rows)} row(s){extra}, {seconds * 1000:.2f} ms)")
    else:
        print(result.message)


def run_sql(db, sql):
    try:
        for stmt in split_statements(sql):
            start = time.perf_counter()
            result = db.execute(stmt)
            show(result, time.perf_counter() - start)
    except DBError as e:
        print(f"Error: {e}")


def main():
    ap = argparse.ArgumentParser(description="MiniDB interactive shell")
    ap.add_argument("--db", help="JSON file used to save/load the database")
    args = ap.parse_args()
    db = Database(args.db)
    print("MiniDB - type .help for help, .quit to exit")
    if args.db:
        print(f"Database file: {args.db}")
    buf = ""
    while True:
        try:
            line = input("minidb> " if not buf else "   ...> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        stripped = line.strip()
        if not buf and stripped.startswith("."):
            cmd, _, arg = stripped.partition(" ")
            if cmd in (".quit", ".exit"):
                break
            elif cmd == ".help":
                print(HELP)
            elif cmd == ".tables":
                run_sql(db, "SHOW TABLES;")
            elif cmd == ".read":
                try:
                    with open(arg.strip(), encoding="utf-8") as f:
                        run_sql(db, f.read())
                except OSError as e:
                    print(f"Cannot read file: {e}")
            else:
                print("Unknown command. Type .help")
            continue
        buf += line + "\n"
        if stripped.endswith(";"):
            run_sql(db, buf)
            buf = ""
    if db.in_transaction:
        print("Open transaction discarded (not committed).")


if __name__ == "__main__":
    sys.exit(main())
