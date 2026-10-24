"""CampusFlow local teaching demo. Python 3.10+, no third-party dependencies."""
import argparse
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import hashlib
import hmac
import secrets
import re
import time
from http.cookies import SimpleCookie
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
        db.executescript((ROOT / 'schema.sql').read_text(encoding='utf-8'))
        # Add a demo account to existing databases without changing student records.
        if db.execute('SELECT 1 FROM students WHERE id=1').fetchone():
            ensure_demo_account(db)
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

        ensure_demo_account(db)

def password_hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 260000).hex()

def ensure_demo_account(db):
    if not db.execute('SELECT 1 FROM accounts WHERE student_id=1').fetchone():
        salt = secrets.token_hex(16)
        db.execute('INSERT INTO accounts(student_id,username,salt,password_hash) VALUES (1,?,?,?)',
                   ('alex.morgan',salt,password_hash('CampusFlow2026!',salt)))

def rows(db, sql, params=()):
    return [dict(r) for r in db.execute(sql, params).fetchall()]

def dashboard(student_id=1):
    today = date.today()
    monday = today-timedelta(days=today.weekday())
    with connect() as db:
        student = dict(db.execute('SELECT * FROM students WHERE id=?',(student_id,)).fetchone())
        courses = rows(db,'''SELECT c.*, e.progress,e.grade,e.status FROM enrollments e
          JOIN courses c ON c.id=e.course_id WHERE e.student_id=? ORDER BY e.status,c.code''',(student_id,))
        catalog = rows(db,'''SELECT c.*, (SELECT count(*) FROM enrollments e WHERE e.course_id=c.id AND e.status='active') AS enrolled_count,
          EXISTS(SELECT 1 FROM enrollments e WHERE e.course_id=c.id AND e.student_id=?) AS enrolled
          FROM courses c WHERE c.id < 7 ORDER BY c.code''',(student_id,))
        tasks = rows(db,'''SELECT t.*,c.code FROM tasks t LEFT JOIN courses c ON c.id=t.course_id WHERE t.student_id=? ORDER BY t.completed,t.due_date''',(student_id,))
        sessions = rows(db,'''SELECT study_date, SUM(minutes) minutes FROM study_sessions WHERE student_id=? AND study_date BETWEEN ? AND ? GROUP BY study_date''',(student_id,str(monday),str(monday+timedelta(days=6))))
        totals = dict(db.execute('''SELECT COALESCE(SUM(CASE WHEN status='completed' THEN credits ELSE 0 END),0) AS credits,
          SUM(CASE WHEN grade IS NOT NULL THEN grade*credits END)/NULLIF(SUM(CASE WHEN grade IS NOT NULL THEN credits END),0) AS gpa
          FROM enrollments JOIN courses ON courses.id=enrollments.course_id WHERE student_id=?''',(student_id,)).fetchone())
    by_date = {s['study_date']:s['minutes'] for s in sessions}
    trend = [{'date':str(monday+timedelta(days=i)),'minutes':by_date.get(str(monday+timedelta(days=i)),0)} for i in range(7)]
    return dict(student=student,courses=courses,catalog=catalog,tasks=tasks,trend=trend,totals=totals,today=str(today))

class Handler(BaseHTTPRequestHandler):
    def session(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get('Cookie',''))
        except Exception:
            return None
        token = cookie.get('campusflow_session')
        if not token: return None
        digest = hashlib.sha256(token.value.encode()).hexdigest()
        with connect() as db:
            return db.execute('SELECT student_id FROM sessions WHERE token_hash=? AND expires_at>?',
                              (digest,time.time())).fetchone()

    def redirect(self, path):
        self.send_response(302)
        self.send_header('Location',path)
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length','0')
        self.end_headers()

    def reply(self, status, obj, cookie=None):
        payload = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        if cookie: self.send_header('Set-Cookie',cookie)
        self.send_header('Content-Length',str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/' and not self.session():
            self.redirect('/login'); return
        if path == '/api/dashboard':
            session = self.session()
            if not session:
                self.reply(401,{'error':'Please sign in.'}); return
            try: self.reply(200,dashboard(session['student_id']))
            except sqlite3.Error: self.reply(500,{'error':'Database query failed.'})
            return
        files = {'/':'index.html','/login':'login.html','/register':'register.html','/register.html':'register.html','/register.js':'register.js','/login.html':'login.html','/login.js':'login.js','/login.css':'login.css','/app.js':'app.js','/style.css':'style.css'}
        if path not in files:
            self.reply(404,{'error':'Not found'}); return
        file = ROOT/'static'/files[path]
        body = file.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type',{'html':'text/html; charset=utf-8','js':'text/javascript; charset=utf-8','css':'text/css; charset=utf-8'}[file.suffix[1:]])
        self.send_header('Cache-Control','no-store')
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
            if self.headers.get('Content-Type','').split(';')[0] != 'application/json':
                self.reply(415,{'error':'Expected application/json.'}); return
            if path == '/api/register':
                fields = ('name','email','username','password','confirm_password','program')
                if any(not isinstance(data.get(k),str) for k in fields):
                    raise ValueError('Complete all registration fields.')
                name = data['name'].strip()
                email = data['email'].strip().lower()
                username = data['username'].strip().lower()
                password = data['password']
                program = data['program'].strip()
                if not 1 <= len(name) <= 80:
                    raise ValueError('Full name must contain 1 to 80 characters.')
                if len(email)>160 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email):
                    raise ValueError('Enter a valid email address.')
                if not re.fullmatch(r'[a-z0-9][a-z0-9._-]{2,31}',username):
                    raise ValueError('Username must be 3–32 characters: letters, numbers, dots, underscores or hyphens; start with a letter or number.')
                if not 10 <= len(password) <= 128:
                    raise ValueError('Password must contain 10 to 128 characters.')
                if password != data['confirm_password']:
                    raise ValueError('Passwords do not match.')
                if program not in ('Computer Science','Data Science','Software Engineering'):
                    raise ValueError('Choose a listed study program.')
                salt = secrets.token_hex(16)
                hashed = password_hash(password,salt)
                with connect() as db:
                    db.execute('BEGIN IMMEDIATE')
                    if db.execute('SELECT 1 FROM accounts WHERE username=?',(username,)).fetchone():
                        self.reply(409,{'error':'This username is already taken.'}); return
                    # Student identity is assigned by the server, not the request.
                    student_number = 'CF-' + secrets.token_hex(8).upper()
                    cursor = db.execute('INSERT INTO students(name,student_number,email,program,semester,target_credits) VALUES (?,?,?,?,1,120)',
                      (name,student_number,email,program))
                    db.execute('INSERT INTO accounts(student_id,username,salt,password_hash) VALUES (?,?,?,?)',
                      (cursor.lastrowid,username,salt,hashed))
                self.reply(201,{'ok':True,'message':'Account created. Please sign in.'})
                return
            if path == '/api/login':
                username = str(data.get('username','')).strip().lower()
                password = str(data.get('password',''))
                if len(username)>100 or len(password)>256:
                    raise ValueError('Invalid credentials.')
                with connect() as db:
                    account = db.execute('SELECT * FROM accounts WHERE username=?',(username,)).fetchone()
                    salt = account['salt'] if account else '00'*16
                    candidate = password_hash(password,salt)
                    if not account or not hmac.compare_digest(candidate,account['password_hash']):
                        self.reply(401,{'error':'Incorrect username or password.'}); return
                    token = secrets.token_urlsafe(32)
                    db.execute('DELETE FROM sessions WHERE expires_at<=?',(time.time(),))
                    # Rotate any session presented by this browser.
                    old = SimpleCookie()
                    old.load(self.headers.get('Cookie',''))
                    if old.get('campusflow_session'):
                        db.execute('DELETE FROM sessions WHERE token_hash=?',
                          (hashlib.sha256(old['campusflow_session'].value.encode()).hexdigest(),))
                    db.execute('INSERT INTO sessions VALUES (?,?,?)',
                      (hashlib.sha256(token.encode()).hexdigest(),account['student_id'],time.time()+28800))
                self.reply(200,{'ok':True},f'campusflow_session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800')
                return
            session = self.session()
            if not session:
                self.reply(401,{'error':'Please sign in.'}); return
            student_id = session['student_id']
            if path == '/api/logout':
                cookie = SimpleCookie(self.headers.get('Cookie',''))
                digest = hashlib.sha256(cookie['campusflow_session'].value.encode()).hexdigest()
                with connect() as db: db.execute('DELETE FROM sessions WHERE token_hash=?',(digest,))
                self.reply(200,{'ok':True},'campusflow_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0')
                return
            with connect() as db:
                if path == '/api/tasks':
                    if type(data.get('completed')) is not bool: raise ValueError('Completed must be boolean.')
                    cur = db.execute('UPDATE tasks SET completed=? WHERE id=? AND student_id=?',(int(data['completed']),int(data['id']),student_id))
                    if not cur.rowcount: raise ValueError('Task not found.')
                elif path == '/api/profile':
                    name, email = str(data.get('name','')).strip(), str(data.get('email','')).strip()
                    if not 1 <= len(name) <= 80 or not 3 <= len(email) <= 160 or '@' not in email: raise ValueError('Enter a name and valid email address.')
                    db.execute('UPDATE students SET name=?,email=? WHERE id=?',(name,email,student_id))
                elif path == '/api/enrollments':
                    cid = int(data['course_id'])
                    if type(data.get('enroll')) is not bool: raise ValueError('Enroll must be boolean.')
                    db.execute('BEGIN IMMEDIATE')
                    course = db.execute('SELECT * FROM courses WHERE id=? AND id<7',(cid,)).fetchone()
                    if not course: raise ValueError('Course not available.')
                    if data['enroll']:
                        if db.execute('SELECT 1 FROM enrollments WHERE student_id=? AND course_id=?',(student_id,cid)).fetchone(): raise ValueError('Already enrolled.')
                        count = db.execute("SELECT COUNT(*) FROM enrollments WHERE course_id=? AND status='active'",(cid,)).fetchone()[0]
                        if count >= course['capacity']: raise ValueError('Course is full.')
                        conflict = db.execute('''SELECT c.title FROM courses c JOIN enrollments e ON e.course_id=c.id
                          WHERE e.student_id=? AND e.status='active' AND c.weekday=? AND c.start_time < ? AND c.end_time > ?''',
                          (student_id,course['weekday'],course['end_time'],course['start_time'])).fetchone()
                        if conflict: raise ValueError('Schedule conflict with '+conflict['title']+'.')
                        db.execute('INSERT INTO enrollments(student_id,course_id) VALUES (?,?)',(student_id,cid))
                    else:
                        cur = db.execute("DELETE FROM enrollments WHERE student_id=? AND course_id=? AND status='active'",(student_id,cid))
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
