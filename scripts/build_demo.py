"""Export a read-only Pages demo from a fresh temporary SQL database."""
import json
from pathlib import Path
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import app


def build():
    with tempfile.TemporaryDirectory() as tmp:
        app.DB = Path(tmp)/'demo.db'
        app.initialize()
        fixture = app.dashboard()
    output = ROOT/'docs'/'demo'
    output.mkdir(parents=True,exist_ok=True)
    html = (ROOT/'static'/'index.html').read_text()
    html = html.replace('href="/style.css"','href="./style.css"').replace('src="/app.js"','src="./app.js"')
    html = html.replace('Local demo · SQL connected','Read-only demo · SQL snapshot')
    html = html.replace('Live data from SQLite','Read-only SQL snapshot · '+fixture['today'])
    js = (ROOT/'static'/'app.js').read_text()
    start = js.index('async function load()')
    end = js.index('function go(',start)
    js = js[:start]+'''async function load(){const r=await fetch('./snapshot.json');if(!r.ok)throw Error('Could not load demo snapshot.');data=await r.json();render()}
async function write(){toast('Read-only preview. Run the Python project locally to save changes.');render();return false}
'''+js[end:]
    (output/'index.html').write_text(html)
    (output/'app.js').write_text(js)
    (output/'style.css').write_text((ROOT/'static'/'style.css').read_text())
    (output/'snapshot.json').write_text(json.dumps(fixture,indent=2)+'\n')
    # Same result is independently inspectable without JavaScript.
    (ROOT/'docs'/'results.json').write_text(json.dumps(fixture,indent=2)+'\n')
    print('Exported SQL snapshot and read-only Pages demo:',fixture['today'])

if __name__=='__main__': build()
