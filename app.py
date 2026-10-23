"""CampusFlow local teaching demo. Python 3.10+, no third-party dependencies."""
import argparse
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'data' / 'campusflow.db'

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    return db

def initialize():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.executescript((ROOT / 'schema.sql').read_text())
        if db.execute('SELECT COUNT(*) FROM students').fetchone()[0]:
            return
        db.execute('INSERT INTO students VALUES (1,?,?,?,?,?,?)',
                   ('Alex Morgan','202400128','alex.morgan@campus.example','Computer Science',3,120))
        courses = [
            (1,'CS501','Machine Learning','Prof. Chen',6,0,'09:00','10:30','A201',35,'Supervised learning, model evaluation and neural networks.','#6366f1'),
            (2,'CS402','Database Systems','Prof. Wang',6,1,'14:00','15:30','B105',30,'Relational modeling, SQL and transaction processing.','#10b981'),
            (3,'CS310','Software Engineering','Prof. Li',6,2,'10:00','11:30','C302',40,'Build maintainable software with testing and design patterns.','#f59e0b'),
            (4,'CS420','Data Visualization','Dr. Taylor',6,3,'11:00','12:30','D104',25,'Communicate data through effective visual design.','#ec4899'),
            (5,'CS430','Cloud Computing','Dr. Patel',6,4,'13:00','14:30','A108',30,'Distributed systems, cloud services and deployment.','#0ea5e9'),
            (6,'CS440','Artificial Intelligence','Prof. Rivera',6,0,'09:30','11:00','B202',25,'Search, reasoning and intelligent agents.','#8b5cf6'),
        ]
        db.executemany('INSERT INTO courses VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', courses)
        db.executemany('INSERT INTO enrollments VALUES (1,?,?,?,?)',[(1,68,None,'active'),(2,82,None,'active'),(3,45,None,'active')])
        # Completed modules provide real SQL-derived credit and GPA totals.
        for i in range(7,19):
            db.execute('INSERT INTO courses VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
              (i,f'CS{100+i}',f'Foundation Module {i-6}','Faculty of Computing',6,0,'08:00','09:00','Online',100,'Completed foundation module.','#94a3b8'))
            db.execute('INSERT INTO enrollments VALUES (1,?,100,?,\'completed\')',(i,[3.7,3.5,3.6][i%3]))
        today = date.today()
        db.executemany('INSERT INTO tasks VALUES (?,1,?,?,?,0)',[
            (1,1,'ML Assignment 03',str(today+timedelta(days=1))),
            (2,2,'Database Project',str(today+timedelta(days=3))),
            (3,3,'Review design patterns',str(today+timedelta(days=4))),
            (4,None,'Confirm next semester courses',str(today+timedelta(days=5)))])
        monday = today-timedelta(days=today.weekday())
        for day, minutes in enumerate([120,150,240,210,300,180,120]):
            d = monday+timedelta(days=day)
            if d <= today:
                db.execute('INSERT INTO study_sessions(student_id,course_id,study_date,minutes) VALUES (1,?,?,?)', (day%3+1,str(d),minutes))

def rows(db, sql, params=()):
    return [dict(r) for r in db.execute(sql, params).fetchall()]

def dashboard():
    today = date.today()
    monday = today-timedelta(days=today.weekday())
    with connect() as db:
        student = dict(db.execute('SELECT * FROM students WHERE id=1').fetchone())
        courses = rows(db,'''SELECT c.*, e.progress,e.grade,e.status FROM enrollments e
          JOIN courses c ON c.id=e.course_id WHERE e.student_id=1 ORDER BY e.status,c.code''')
        catalog = rows(db,'''SELECT c.*, (SELECT count(*) FROM enrollments e WHERE e.course_id=c.id AND e.status='active') AS enrolled_count,
          EXISTS(SELECT 1 FROM enrollments e WHERE e.course_id=c.id AND e.student_id=1) AS enrolled
          FROM courses c WHERE c.id < 7 ORDER BY c.code''')
        tasks = rows(db,'''SELECT t.*,c.code FROM tasks t LEFT JOIN courses c ON c.id=t.course_id WHERE t.student_id=1 ORDER BY t.completed,t.due_date''')
        sessions = rows(db,'''SELECT study_date, SUM(minutes) minutes FROM study_sessions WHERE student_id=1 AND study_date BETWEEN ? AND ? GROUP BY study_date''',(str(monday),str(monday+timedelta(days=6))))
        totals = dict(db.execute('''SELECT COALESCE(SUM(CASE WHEN status='completed' THEN credits ELSE 0 END),0) AS credits,
          SUM(CASE WHEN grade IS NOT NULL THEN grade*credits END)/NULLIF(SUM(CASE WHEN grade IS NOT NULL THEN credits END),0) AS gpa
          FROM enrollments JOIN courses ON courses.id=enrollments.course_id WHERE student_id=1''').fetchone())
    by_date = {s['study_date']:s['minutes'] for s in sessions}
    trend = [{'date':str(monday+timedelta(days=i)),'minutes':by_date.get(str(monday+timedelta(days=i)),0)} for i in range(7)]
    return dict(student=student,courses=courses,catalog=catalog,tasks=tasks,trend=trend,totals=totals,today=str(today))

class Handler(BaseHTTPRequestHandler):
    def reply(self, status, obj):
        payload = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/dashboard':
            try: self.reply(200,dashboard())
            except sqlite3.Error: self.reply(500,{'error':'Database query failed.'})
            return
        files = {'/':'index.html','/app.js':'app.js','/style.css':'style.css'}
        if path not in files:
            self.reply(404,{'error':'Not found'}); return
        file = ROOT/'static'/files[path]
        body = file.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type',{'html':'text/html; charset=utf-8','js':'text/javascript; charset=utf-8','css':'text/css; charset=utf-8'}[file.suffix[1:]])
        self.send_header('Content-Length',str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def do_POST(self):
        # Browser writes are restricted to the local application origin.
        origin = self.headers.get('Origin')
        if origin and origin != 'http://'+self.headers.get('Host',''):
            self.reply(403,{'error':'Cross-origin writes are not allowed.'}); return
        try:
            size = int(self.headers.get('Content-Length','0'))
            if size < 0 or size > 8192: raise ValueError('Invalid request size.')
            data = json.loads(self.rfile.read(size))
            if not isinstance(data,dict): raise ValueError('Expected a JSON object.')
            path = urlparse(self.path).path
            with connect() as db:
                if path == '/api/tasks':
                    if type(data.get('completed')) is not bool: raise ValueError('Completed must be boolean.')
                    cur = db.execute('UPDATE tasks SET completed=? WHERE id=? AND student_id=1',(int(data['completed']),int(data['id'])))
                    if not cur.rowcount: raise ValueError('Task not found.')
                elif path == '/api/profile':
                    name, email = str(data.get('name','')).strip(), str(data.get('email','')).strip()
                    if not 1 <= len(name) <= 80 or not 3 <= len(email) <= 160 or '@' not in email: raise ValueError('Enter a name and valid email address.')
                    db.execute('UPDATE students SET name=?,email=? WHERE id=1',(name,email))
                elif path == '/api/enrollments':
                    cid = int(data['course_id'])
                    if type(data.get('enroll')) is not bool: raise ValueError('Enroll must be boolean.')
                    db.execute('BEGIN IMMEDIATE')
                    course = db.execute('SELECT * FROM courses WHERE id=? AND id<7',(cid,)).fetchone()
                    if not course: raise ValueError('Course not available.')
                    if data['enroll']:
                        if db.execute('SELECT 1 FROM enrollments WHERE student_id=1 AND course_id=?',(cid,)).fetchone(): raise ValueError('Already enrolled.')
                        count = db.execute("SELECT COUNT(*) FROM enrollments WHERE course_id=? AND status='active'",(cid,)).fetchone()[0]
                        if count >= course['capacity']: raise ValueError('Course is full.')
                        conflict = db.execute('''SELECT c.title FROM courses c JOIN enrollments e ON e.course_id=c.id
                          WHERE e.student_id=1 AND e.status='active' AND c.weekday=? AND c.start_time < ? AND c.end_time > ?''',
                          (course['weekday'],course['end_time'],course['start_time'])).fetchone()
                        if conflict: raise ValueError('Schedule conflict with '+conflict['title']+'.')
                        db.execute('INSERT INTO enrollments(student_id,course_id) VALUES (1,?)',(cid,))
                    else:
                        cur = db.execute("DELETE FROM enrollments WHERE student_id=1 AND course_id=? AND status='active'",(cid,))
                        if not cur.rowcount: raise ValueError('Active enrollment not found.')
                else:
                    self.reply(404,{'error':'Not found'}); return
            self.reply(200,{'ok':True})
        except (ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
            self.reply(400,{'error':str(exc) or 'Invalid request.'})
        except sqlite3.Error:
            self.reply(500,{'error':'Database operation failed.'})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8000)
    parser.add_argument('--init-only',action='store_true')
    args = parser.parse_args()
    initialize()
    if not args.init_only:
        print(f'CampusFlow: http://127.0.0.1:{args.port}',flush=True)
        ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
