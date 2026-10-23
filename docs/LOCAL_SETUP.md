# CampusFlow — SQL Student Dashboard

A working English-language student dashboard inspired by the supplied design.
All dashboard records come from SQLite through a Python JSON API. No CDN, npm,
pip packages, API keys, or internet connection are needed.

## Quick start (Windows / macOS / Linux)

Requires Python **3.10 or newer**.

1. Extract this project ZIP.
2. Open a terminal in the `campusflow` directory (the folder containing `app.py`).
3. Run:

```powershell
python app.py
```

On Windows, use `py app.py` if `python` is unavailable. On macOS/Linux, use
`python3 app.py` if necessary.

4. Open **http://127.0.0.1:8000** in your browser.
5. Stop the server with **Ctrl+C**.

If port 8000 is occupied: `python app.py --port 8080` and open
http://127.0.0.1:8080. Do not open `static/index.html` directly: it needs the API.

The included `data/campusflow.db` has fictional demo data. If missing, it is
created and seeded automatically. Changes persist across refreshes and restarts.
Dates for new seed data are relative to the day you initialize the database.
The interface always uses the current server date; only recorded study sessions
count toward the current week. Future/unrecorded days show zero, not forecasts.

## Implemented features

- English overview with SQL-derived course, credit, study-hour and task totals.
- Editable student name and email, persisted to SQL.
- Searchable course catalog; enroll/drop with transactional capacity checks,
  duplicate checks and schedule-conflict detection.
- Active courses and learning progress read from SQL.
- Learning analytics, weekly study hours and credit-weighted GPA.
- Academic record and weekly timetable.
- Task completion toggles persisted to SQL.
- Responsive layout, keyboard focus, semantic controls and API error feedback.

This is a **single-student local demonstration**, with student ID 1 as the demo
identity. It deliberately has no login, real LMS integration, grade entry UI or
course content player. “Details” displays course information. Study logs,
progress and grades are sample records managed in SQL, not browser activity
tracking. All text is in English; the UI uses a demonstration 4.0 GPA scale,
not the German grading scale.

## Architecture

Browser HTML/CSS/JavaScript → HTTP JSON API → Python sqlite3 → SQLite file.
Frontend values are rendered from `/api/dashboard`; the browser does not open
the database directly. Writes use SQL parameters and foreign-key enforcement.
The server only binds to loopback (`127.0.0.1`). The project is not deployed.

```text
campusflow/
  app.py                 Python HTTP server, SQL reads/writes, initialization
  schema.sql             Tables, constraints, indexes
  queries.sql            Example queries for inspecting real records
  data/campusflow.db     Seeded SQLite database
  static/index.html      English app shell
  static/style.css       Responsive design
  static/app.js          API client, charts, navigation, interactions
  test_app.py            Isolated API/database integration tests
  README.md              English instructions
  START_HERE_ZH.md        Chinese quick-start instructions
```

## Database relationships

| Table | Purpose | Relations |
|---|---|---|
| students | Personal and academic identity | One student has many enrollments, tasks, sessions |
| courses | Course catalog and weekly time slots | Referenced by enrollments, tasks and sessions |
| enrollments | Student/course relationship, progress, status, grade | Composite student/course primary key |
| tasks | Deadline and completion state | Belongs to a student, optionally a course |
| study_sessions | Date and minutes studied | Belongs to a student and course |

Completed credits: sum course credits for completed enrollments.
GPA: sum(grade × credits) / sum(credits with a grade).
Weekly study time: sum session minutes from Monday through Sunday.
Pending tasks: count tasks with completed = 0.

## API

| Method | Path | Body / response |
|---|---|---|
| GET | /api/dashboard | Student, enrolled courses, catalog, tasks, weekly trend, totals, current date |
| POST | /api/profile | `{"name":"Alex Morgan","email":"alex@example.org"}` |
| POST | /api/tasks | `{"id":1,"completed":true}` |
| POST | /api/enrollments | `{"course_id":4,"enroll":true}` (false to drop) |

Writes return `{"ok":true}` or `{"error":"..."}` with a suitable HTTP status.

## Inspect or change SQL data

Open `data/campusflow.db` with DB Browser for SQLite or a VS Code SQLite extension,
or use Python's built-in sqlite3 module. Example inspection:

```python
import sqlite3
with sqlite3.connect('data/campusflow.db') as db:
    for row in db.execute('SELECT code, title, credits FROM courses'):
        print(row)
```

Example adding a learning record (run from the project directory):

```python
import sqlite3
from datetime import date
with sqlite3.connect('data/campusflow.db') as db:
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('INSERT INTO study_sessions(student_id,course_id,study_date,minutes) VALUES (?,?,?,?)',
               (1,1,str(date.today()),45))
```

Refresh the dashboard to see the updated totals. See `queries.sql` for more.
To reset: stop the server, **back up the database**, remove
`data/campusflow.db`, then restart. This deletes your demo changes.
To initialize without serving: `python app.py --init-only`.

## Validation

```powershell
python -m unittest -v test_app
```

Tests create a temporary database and verify SQL aggregates, task/profile
persistence, enroll/drop, conflict checks, input validation, parameterized SQL
and cross-origin write rejection. They do not modify your demo database.
Optional JavaScript syntax check when Node is installed:
`node --check static/app.js`.

## Extending the project

For a multi-student system, add authentication and authorize every query by the
signed-in student rather than ID 1. Add migrations, CSRF protection suitable for
the chosen authentication, monitoring and a production web server before any
public deployment. To use MySQL/PostgreSQL, replace the connection/SQL layer and
adapt schema, placeholders and transaction handling; they are not drop-in file
replacements. No connection to an existing university database is configured.
