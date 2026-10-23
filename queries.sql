-- SQLite examples. Run SELECTs against data/campusflow.db.
SELECT name, student_number, program, semester FROM students WHERE id = 1;
SELECT c.code, c.title, c.credits, e.progress, e.grade, e.status
FROM enrollments e JOIN courses c ON c.id=e.course_id
WHERE e.student_id=1 ORDER BY e.status,c.code;
SELECT SUM(c.credits) AS earned_credits
FROM enrollments e JOIN courses c ON c.id=e.course_id
WHERE e.student_id=1 AND e.status='completed';
SELECT SUM(e.grade*c.credits)/SUM(c.credits) AS weighted_gpa
FROM enrollments e JOIN courses c ON c.id=e.course_id
WHERE e.student_id=1 AND e.grade IS NOT NULL;
SELECT study_date, SUM(minutes)/60.0 AS hours
FROM study_sessions WHERE student_id=1 GROUP BY study_date ORDER BY study_date;
SELECT title, due_date FROM tasks WHERE student_id=1 AND completed=0 ORDER BY due_date;
-- Optional modification example (uncomment deliberately):
-- UPDATE enrollments SET progress=75 WHERE student_id=1 AND course_id=1;
