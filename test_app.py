"""Integration tests use an isolated database; never alter the demo database."""
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
import app

class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        app.DB = Path(cls.tmp.name)/'test.db'
        app.initialize()
        cls.server = ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.tmp.cleanup()
    def setUp(self):
        self.cookie = ''
        status,_ = self.request('/api/login',{'username':'alex.morgan','password':'CampusFlow2026!'})
        self.assertEqual(status,200)

    def request(self,path,body=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port)
        request_headers={'Content-Type':'application/json'}
        if getattr(self,'cookie',''): request_headers['Cookie']=self.cookie
        request_headers.update(headers or {})
        c.request('GET' if body is None else 'POST',path,None if body is None else json.dumps(body),request_headers)
        r=c.getresponse(); status=r.status
        if r.getheader('Set-Cookie'): self.cookie=r.getheader('Set-Cookie').split(';')[0]
        payload=r.read(); c.close()
        return status,json.loads(payload)
    def test_login_logout_and_expiry(self):
        self.cookie=''
        self.assertEqual(self.request('/api/dashboard')[0],401)
        self.assertEqual(self.request('/api/profile',{'name':'No','email':'no@example.org'})[0],401)
        self.assertEqual(self.request('/api/login',{'username':'alex.morgan','password':'wrong'})[0],401)
        self.assertEqual(self.request('/api/login',{'username':'missing','password':'wrong'})[0],401)
        self.assertEqual(self.request('/api/login',{'username':'alex.morgan','password':'CampusFlow2026!'})[0],200)
        token=self.cookie
        self.assertEqual(self.request('/api/dashboard')[0],200)
        self.assertEqual(self.request('/api/logout',{})[0],200)
        self.cookie=token
        self.assertEqual(self.request('/api/dashboard')[0],401)
        self.request('/api/login',{'username':'alex.morgan','password':'CampusFlow2026!'})
        with app.connect() as db: db.execute('UPDATE sessions SET expires_at=0')
        self.assertEqual(self.request('/api/dashboard')[0],401)

    def test_student_isolation(self):
        with app.connect() as db:
            db.execute("INSERT OR IGNORE INTO students VALUES (2,'Other Student','OTHER','other@example.org','CS',1,120)")
            salt='11'*16
            db.execute('INSERT OR IGNORE INTO accounts VALUES (2,?,?,?)',('other',salt,app.password_hash('other-password',salt)))
        self.request('/api/login',{'username':'other','password':'other-password'})
        status,d=self.request('/api/dashboard')
        self.assertEqual(status,200)
        self.assertEqual(d['student']['id'],2)
        self.assertEqual(d['courses'],[])
        self.assertEqual(d['tasks'],[])
        self.assertEqual(self.request('/api/tasks',{'id':1,'completed':True})[0],400)
        self.assertEqual(self.request('/api/enrollments',{'course_id':1,'enroll':True})[0],200)
        with app.connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM enrollments WHERE student_id=2').fetchone()[0],1)
            db.execute('DELETE FROM enrollments WHERE student_id=2')

    def test_aggregate_values(self):
        status,d=self.request('/api/dashboard')
        self.assertEqual(status,200)
        self.assertEqual(d['totals']['credits'],72)
        self.assertAlmostEqual(d['totals']['gpa'],3.6)
        self.assertEqual(len([c for c in d['courses'] if c['status']=='active']),3)
    def test_enroll_drop_and_conflict(self):
        status,d=self.request('/api/enrollments',{'course_id':6,'enroll':True})
        self.assertEqual(status,400); self.assertIn('conflict',d['error'])
        self.assertEqual(self.request('/api/enrollments',{'course_id':4,'enroll':True})[0],200)
        self.assertEqual(self.request('/api/enrollments',{'course_id':4,'enroll':True})[0],400)
        self.assertEqual(self.request('/api/enrollments',{'course_id':4,'enroll':False})[0],200)
    def test_task_profile_persistence_and_sql_safety(self):
        self.assertEqual(self.request('/api/tasks',{'id':1,'completed':True})[0],200)
        name="Alex'); DROP TABLE students; --"
        self.assertEqual(self.request('/api/profile',{'name':name,'email':'alex@example.org'})[0],200)
        d=self.request('/api/dashboard')[1]
        self.assertTrue(next(t for t in d['tasks'] if t['id']==1)['completed'])
        self.assertEqual(d['student']['name'],name)
        app.initialize() # Restart initialization must preserve existing data.
        self.assertEqual(app.dashboard()['student']['name'],name)
    def test_validation_and_origin(self):
        self.assertEqual(self.request('/api/tasks',{'id':999,'completed':True})[0],400)
        self.assertEqual(self.request('/api/tasks',{'id':1,'completed':'false'})[0],400)
        self.assertEqual(self.request('/api/profile',{'name':'','email':'bad'})[0],400)
        self.assertEqual(self.request('/api/tasks',{'id':1,'completed':True},{'Origin':'https://foreign.example'})[0],403)
        self.assertEqual(self.request('/../app.py')[0],404)

if __name__=='__main__': unittest.main()
