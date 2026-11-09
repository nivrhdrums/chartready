# build both versions, then publish: public at the site root, personal (secret open) at a hidden folder
import os,shutil,subprocess,json,sys
B='/tmp/claude-0/build/'; R='/home/claude/chartready/'; OUT='/home/claude/release/'
SECRET_DIR='c40b604d'
subprocess.run(['python3',B+'release.py'],check=True,stdout=subprocess.DEVNULL)
for f in os.listdir(R):
    if f in ('.git',SECRET_DIR): continue
    p=R+f; shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
for f in os.listdir(OUT+'ChartReady-ציבורי'):
    if f=='קרא אותי.txt': continue
    s=OUT+'ChartReady-ציבורי/'+f; shutil.copytree(s,R+f) if os.path.isdir(s) else shutil.copy(s,R+f)
S=R+SECRET_DIR+'/'; shutil.rmtree(S,ignore_errors=True); shutil.copytree(OUT+'ChartReady-אישי/public',S)
m=json.load(open(S+'manifest.webmanifest')); m['name']='ChartReady ⭐'; m['short_name']='ChartReady ⭐'
m['icons']=[{"src":"icon-star-192.png","sizes":"192x192","type":"image/png"},{"src":"icon-star-512.png","sizes":"512x512","type":"image/png"}]
json.dump(m,open(S+'manifest.webmanifest','w'),ensure_ascii=False,indent=1)
for n in ('192','512','180'): shutil.copy(B+f'win/icon-star-{n}.png',S+f'icon-star-{n}.png')
h=open(S+'index.html').read()
h=h.replace('<head>','<head><meta name="robots" content="noindex,nofollow">',1).replace('href="icon-180.png"','href="icon-star-180.png"').replace('<title>ChartReady</title>','<title>ChartReady ⭐</title>')
w=open(S+'sw.js').read().replace("'chartready-","'chartready-star-"); open(S+'sw.js','w').write(w)
open(S+'index.html','w').write(h)
msg=sys.argv[1] if len(sys.argv)>1 else 'Update'
g=lambda *a: subprocess.run(['git','-C',R]+list(a),check=True)
g('add','-A')
subprocess.run(['git','-C',R,'-c','user.name=nivrhdrums','-c','user.email=nivdrumstudio@gmail.com','commit','-qm',msg+'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_012j8rcQ33ceY5Y2XsebBv6C'])
g('push','-q')
os.chdir(OUT); subprocess.run('rm -f *.zip && zip -qr "ChartReady-אישי.zip" "ChartReady-אישי" && zip -qr "ChartReady-ציבורי.zip" "ChartReady-ציבורי"',shell=True)
print('deployed', open(B+'ver.txt').read())
