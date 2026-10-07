# MiniDB - Database Simulation Engine

A small relational database engine written in **pure Python** (no external libraries).
It parses SQL, plans queries, uses indexes, enforces constraints, supports transactions
and saves data to disk. Built to understand how real databases like SQLite and MySQL work inside.

**Tech:** Python 3.9+, data structures (hash maps, sets), parsing, `unittest`

## Quick start

```bash
python cli.py                       # interactive SQL shell (in-memory)
python cli.py --db mydata.json      # shell that saves to / loads from a file
python demo.py                      # guided tour of every feature
python benchmark.py                 # shows how much faster indexes make queries
python -m unittest discover -s tests -v   # 33 tests
```

In the shell: `.read examples/school.sql` loads a sample database. `.help` lists commands.

## Features

| Area | Supported |
|---|---|
| DDL | `CREATE TABLE`, `DROP TABLE`, `CREATE INDEX ON t (col)`, `SHOW TABLES`, `DESCRIBE t` |
| Types | `INT`, `FLOAT`, `TEXT` (`VARCHAR`), `BOOL` with type checking |
| Constraints | `PRIMARY KEY`, `NOT NULL`, `UNIQUE` |
| Queries | `SELECT`, `DISTINCT`, `WHERE`, `ORDER BY` (multi-column, `DESC`), `LIMIT`/`OFFSET` |
| Conditions | `= != < > <= >=`, `AND OR NOT`, `LIKE`, `IN`, `BETWEEN`, `IS [NOT] NULL`, `+ - * /` |
| Functions | `COUNT SUM AVG MIN MAX`, `UPPER LOWER LENGTH ABS ROUND` |
| Grouping | `GROUP BY` with aggregates |
| Joins | `INNER JOIN`, `LEFT JOIN`, chained joins, table aliases |
| Data changes | `INSERT` (multi-row), `UPDATE` (with expressions), `DELETE` |
| Transactions | `BEGIN`, `COMMIT`, `ROLLBACK` |
| Planner | Hash indexes, hash joins, `EXPLAIN` shows the chosen plan |
| Storage | JSON file, written atomically |

## Project structure

```
minidb-engine/
├── cli.py               # interactive shell (REPL)
├── demo.py              # scripted feature tour
├── benchmark.py         # index speed test
├── minidb/
│   ├── parser.py        # tokenizer + recursive-descent SQL parser -> AST
│   ├── expressions.py   # evaluates WHERE/ON expressions (SQL NULL logic)
│   ├── table.py         # rows, type checks, constraints, hash indexes
│   ├── database.py      # executor, query planner, joins, transactions
│   ├── storage.py       # save / load JSON
│   └── formatter.py     # ASCII table output
├── tests/test_engine.py
└── examples/school.sql
```

## How a query runs

```
SQL text --> tokenize --> parse (AST) --> plan access path --> execute --> Result
                                           |                     |
                                  index lookup or full scan   join -> filter -> group
                                                              -> distinct -> sort -> limit
```

1. **Parse:** `parser.py` turns text into a nested structure. Operator precedence
   (`OR` < `AND` < `NOT` < comparison < `+ -` < `* /`) comes from the order of the parse functions.
2. **Plan:** if `WHERE` has `indexed_column = value`, the engine does an O(1) hash lookup instead of scanning every row.
   Joins use an index or build a temporary hash table instead of a nested loop.
3. **Execute:** rows become dictionaries; expressions are evaluated with three-valued logic, so `age = NULL` is never true.
4. **Atomic statements:** if the 3rd row of a multi-row `INSERT` fails, the first 2 are removed again.
5. **Transactions:** `BEGIN` takes a snapshot, `ROLLBACK` restores it, `COMMIT` keeps changes and saves to disk.

## Example session

```sql
minidb> CREATE TABLE users (id INT PRIMARY KEY, name TEXT NOT NULL, age INT);
minidb> INSERT INTO users VALUES (1, 'Asha', 21), (2, 'Ravi', 25);
minidb> EXPLAIN SELECT * FROM users WHERE id = 2;
  1. users: INDEX LOOKUP on id = 2  (hash index, ~1 row)
minidb> BEGIN;
minidb> DELETE FROM users;
minidb> ROLLBACK;
```

Benchmark (20,000 rows, point lookup): 23 ms without an index vs 0.03 ms with one (about 900x faster).

## Limitations (good to know / ideas to extend)

- Indexes are hash-based, so they speed up `=` only, not ranges. Next step: a B-tree or sorted index for `<`, `>`, `BETWEEN`.
- No `HAVING`, subqueries, `ALTER TABLE`, or `RIGHT`/`FULL JOIN`.
- `BEGIN` copies all tables, which is simple but slow for big databases. Real engines use a write-ahead log.
- One user at a time: no locking or concurrency.
- Whole database is rewritten on each save; real engines write pages.
