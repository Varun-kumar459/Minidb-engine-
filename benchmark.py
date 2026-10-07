"""Shows why indexes matter:   python benchmark.py"""
import random
import time

from minidb import Database

N = 20000
LOOKUPS = 200

db = Database()
db.execute("CREATE TABLE users (id INT PRIMARY KEY, email TEXT, age INT)")
print(f"Inserting {N:,} rows ...")
for start in range(0, N, 1000):
    values = ",".join(f"({i}, 'user{i}@mail.com', {20 + i % 40})" for i in range(start, start + 1000))
    db.execute(f"INSERT INTO users VALUES {values}")

random.seed(1)
targets = [random.randrange(N) for _ in range(LOOKUPS)]


def timed(label, make_sql):
    t = time.perf_counter()
    examined = 0
    for x in targets:
        r = db.execute(make_sql(x))
        examined = r.examined
    elapsed = time.perf_counter() - t
    print(f"{label:<34} {elapsed / LOOKUPS * 1000:8.3f} ms/query   rows examined per query: {examined:,}")
    return elapsed


print(f"\nRunning {LOOKUPS} point lookups:\n")
a = timed("WHERE id = ...  (primary key)", lambda x: f"SELECT * FROM users WHERE id = {x}")
b = timed("WHERE email = ... (no index)", lambda x: f"SELECT * FROM users WHERE email = 'user{x}@mail.com'")
db.execute("CREATE INDEX ON users (email)")
c = timed("WHERE email = ... (with index)", lambda x: f"SELECT * FROM users WHERE email = 'user{x}@mail.com'")
print(f"\nThe index made the email lookup about {b / c:,.0f}x faster.")
