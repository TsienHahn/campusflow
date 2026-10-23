"""Export a read-only Pages demo from a fresh temporary SQL database."""
import json
from pathlib import Path
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import app


def build():
    original_db = app.DB
    try:
        with tempfile.TemporaryDirectory() as tmp:
            app.DB = Path(tmp)/'demo.db'
            app.initialize()
            fixture = app.dashboard()
    finally:
        app.DB = original_db
    output = ROOT/'docs'/'demo'
    output.mkdir(parents=True,exist_ok=True)
    html = (ROOT/'static'/'index.html').read_text(encoding='utf-8')
    html = html.replace('href="/style.css"','href="./style.css"').replace('src="/app.js"','src="./app.js"')
    html = html.replace('class="brand" href="/"','class="brand" href="./dashboard.html"')
    html = html.replace('Local demo · SQL connected','Read-only demo · SQL snapshot')
    html = html.replace('Live data from SQLite','Read-only SQL snapshot · '+fixture['today'])
    js = (ROOT/'static'/'app.js').read_text(encoding='utf-8')
    start = js.index('async function load()')
    end = js.index('function go(',start)
    js = js[:start]+'''async function load(){const r=await fetch('./snapshot.json');if(!r.ok)throw Error('Could not load demo snapshot.');data=await r.json();render()}
async function write(){toast('Read-only preview. Run the Python project locally to save changes.');render();return false}
'''+js[end:]
    # The static demo has an entry screen, never simulated password authentication.
    js = js[:js.index("$('#logout').addEventListener")]+"$('#logout').addEventListener('click',()=>location.replace('./'));\n"
    login = (ROOT/'static'/'login.html').read_text(encoding='utf-8')
    login = login.replace('Sign in · CampusFlow','Explore demo · CampusFlow')
    login = login.replace('Welcome back.','Explore CampusFlow.')
    login = login.replace('Sign in to continue your learning journey.','A read-only preview of your student workspace.')
    form_start = login.index('<form id="loginForm">')
    form_end = login.index('</form>',form_start)+len('</form>')
    login = login[:form_start]+'<a class="submit" href="./dashboard.html" style="text-decoration:none">Open demo workspace <span>→</span></a>'+login[form_end:]
    box_start = login.index('<div class="demo-box">')
    box_end = login.index('</div>',box_start)+len('</div>')
    login = login[:box_start]+'<div class="demo-box"><strong>Read-only SQL snapshot</strong><p>No sign-in is performed on GitHub Pages. Run the Python application locally to use real login and persistent changes.</p></div>'+login[box_end:]
    login = login.replace('<script src="./login.js" defer></script>','')
    login = login.replace('Local learning project · fictional student records.<br>Sessions expire after 8 hours. No registration is required.','Fictional records · public static demonstration.<br>The full local version includes authenticated sessions.')
    (output/'index.html').write_text(login,encoding='utf-8')
    (output/'dashboard.html').write_text(html,encoding='utf-8')
    (output/'app.js').write_text(js,encoding='utf-8')
    for asset in ('style.css','login.css'):
        (output/asset).write_text((ROOT/'static'/asset).read_text(encoding='utf-8'),encoding='utf-8')
    snapshot = json.dumps(fixture,ensure_ascii=False,indent=2)+'\n'
    (output/'snapshot.json').write_text(snapshot,encoding='utf-8')
    (ROOT/'docs'/'results.json').write_text(snapshot,encoding='utf-8')
    print('Demo exported successfully.')
    print('Output directory:',output)

if __name__=='__main__': build()
