# CampusFlow: project walkthrough

## 1. Define the problem

Build a coherent student workspace covering identity, course selection and
learning status. A successful first version lets a reviewer both understand the
screen and reproduce a data change through SQL-backed behavior.

Primary user stories:

- As a student, I want to see my current courses and today's classes.
- As a student, I want to enroll without accidentally creating a time conflict.
- As a student, I want to know my pending tasks and completed credits.
- As a reviewer, I want to trace a displayed number to a database query.

Acceptance criteria: seven English views, data read from SQL rather than
hardcoded frontend values, persistent changes, deterministic core metric tests,
and instructions that work without a dependency installation step.

## 2. Design the workspace

The initial image explored a light university dashboard with indigo highlights,
a sidebar and grouped cards. The implementation translates the concept into
English, using system fonts, CSS cards, inline SVG charts and responsive grids.
The overview prioritizes actionable tasks and current courses.

The concept image is retained as process evidence, not implementation evidence.
For the English result, run the app or publish the static demo. No fabricated
screenshot is presented as a browser capture.

## 3. Choose the architecture

SQLite keeps the project runnable on a laptop and demonstrates real relational
queries. Python's standard library avoids environment setup friction. Vanilla
JavaScript keeps API calls and rendering easy to inspect. The tradeoff is that
this foundation is intentionally small and does not provide an authentication
framework, production deployment stack or ORM migrations.

## 4. Model and query data

Separate student identity, courses, registrations, tasks and study events.
Compute completed credits and credit-weighted GPA from enrollment/course joins.
Aggregate study sessions by day, then fill unrecorded weekdays with zero in the
API response. See [database design](DATABASE.md) and [query examples](../queries.sql).

## 5. Complete the interaction loop

The frontend loads a single consistent dashboard response. Profile edits, task
updates and enrollment changes use POST endpoints. After success, the client
reloads the dashboard so cards, course lists and timetable agree with SQL.
Business-rule errors are displayed as user feedback rather than silently ignored.

## 6. Validate meaningful behavior

Integration tests use a temporary database and a real local HTTP server. They
exercise metric calculations, conflicting and duplicate enrollment, persistence,
invalid requests and SQL parameter binding. The demo export queries the same
backend using an independent temporary database. See [validation](VALIDATION.md).

## 7. Make the result reviewable

The repository includes the live-server source, SQL schema, sample output,
read-only Pages export, tests, architecture explanation and publishing guide.
The hosted demo is deliberately marked read-only: it cannot execute server-side
Python on GitHub Pages. The full local app demonstrates the persistent writes.

## Future iteration

Add student authentication and a teacher workflow before using real records.
Then introduce migrations and a production web server; consider PostgreSQL when
multi-user concurrency justifies it. Collect user feedback before expanding the
analytics beyond the current study-hour, progress and academic-record views.
