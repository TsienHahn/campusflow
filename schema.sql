PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS students (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, student_number TEXT UNIQUE NOT NULL,
 email TEXT NOT NULL, program TEXT NOT NULL, semester INTEGER NOT NULL,
 target_credits INTEGER NOT NULL DEFAULT 120
);
CREATE TABLE IF NOT EXISTS courses (
 id INTEGER PRIMARY KEY, code TEXT UNIQUE NOT NULL, title TEXT NOT NULL,
 instructor TEXT NOT NULL, credits INTEGER NOT NULL CHECK(credits > 0),
 weekday INTEGER NOT NULL CHECK(weekday BETWEEN 0 AND 6),
 start_time TEXT NOT NULL, end_time TEXT NOT NULL, room TEXT NOT NULL,
 capacity INTEGER NOT NULL CHECK(capacity > 0), description TEXT NOT NULL,
 color TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS enrollments (
 student_id INTEGER REFERENCES students(id), course_id INTEGER REFERENCES courses(id),
 progress INTEGER NOT NULL DEFAULT 0 CHECK(progress BETWEEN 0 AND 100),
 grade REAL CHECK(grade BETWEEN 0 AND 4), status TEXT NOT NULL DEFAULT 'active'
 CHECK(status IN ('active','completed')), PRIMARY KEY(student_id,course_id)
);
CREATE TABLE IF NOT EXISTS tasks (
 id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES students(id),
 course_id INTEGER REFERENCES courses(id), title TEXT NOT NULL,
 due_date TEXT NOT NULL, completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1))
);
CREATE TABLE IF NOT EXISTS study_sessions (
 id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES students(id),
 course_id INTEGER NOT NULL REFERENCES courses(id), study_date TEXT NOT NULL,
 minutes INTEGER NOT NULL CHECK(minutes > 0)
);
CREATE INDEX IF NOT EXISTS sessions_student_date ON study_sessions(student_id,study_date);
CREATE INDEX IF NOT EXISTS tasks_student_due ON tasks(student_id,due_date);
CREATE TABLE IF NOT EXISTS accounts (
 student_id INTEGER PRIMARY KEY REFERENCES students(id),
 username TEXT UNIQUE NOT NULL,
 salt TEXT NOT NULL,
 password_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
 token_hash TEXT PRIMARY KEY,
 student_id INTEGER NOT NULL REFERENCES accounts(student_id),
 expires_at REAL NOT NULL
);
