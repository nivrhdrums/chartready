import os,re,shutil,subprocess
H='/home/claude/'; B='/tmp/claude-0/build/'; OUT=H+'release/'
VN=int(open(B+'ver.txt').read()) if os.path.exists(B+'ver.txt') else 7
VN+=1; open(B+'ver.txt','w').write(str(VN)); CRV=f'2.0.{VN}'
VER='chartready-'+CRV
def build(secret):
    env=dict(os.environ,SECRET_OPEN='true' if secret else 'false',CR_VER=CRV)
    subprocess.run(['python3',B+'build.py'],env=env,check=True,stdout=subprocess.DEVNULL)
    return open(H+'chartready-site/index.html').read(), open(H+'chartready.html').read()
def site(dst,page):
    os.makedirs(dst,exist_ok=True)
    open(dst+'index.html','w').write(page)
    for f in ['icon-180.png','icon-192.png','icon-512.png']: shutil.copy(H+'chartready-site/'+f,dst+f)
    m=open(H+'chartready-site/manifest.webmanifest').read().replace('#0c0e12','#0b0c0e'); open(dst+'manifest.webmanifest','w').write(m)
    w=open(H+'chartready-site/sw.js').read(); w=re.sub(r"chartready-v\d+",VER,w)
    w=w.replace("  const url = new URL(req.url);\n","  const url = new URL(req.url);\n  if (url.pathname === '/lan' || url.pathname === '/ws') return;\n")
    open(dst+'sw.js','w').write(w)
shutil.rmtree(OUT,ignore_errors=True)
# ---- personal: local server, everything open ----
P=OUT+'ChartReady-אישי/'
page,single=build(True)
site(P+'public/',page)
for f in ['server.js','package.json']: shutil.copy(H+'cr-server/'+f,P+f)
shutil.copytree(H+'cr-server/node_modules',P+'node_modules')
open(P+'הפעלה-מק.command','w').write('''#!/bin/bash
cd "$(dirname "$0")"
if ! command -v node >/dev/null 2>&1; then echo "צריך להתקין Node.js מ- https://nodejs.org (פעם אחת) ואז להפעיל שוב."; read -p "Enter לסגירה"; exit 1; fi
( sleep 1.5; open "http://localhost:8787" ) &
LOCAL=1 node server.js
''')
os.chmod(P+'הפעלה-מק.command',0o755)
open(P+'הפעלה-בחלון (לבדיקות).bat','w',newline='\r\n').write('''@echo off
chcp 65001 >nul
cd /d "%~dp0"
where node >nul 2>nul || (echo צריך להתקין Node.js מ- https://nodejs.org ואז להפעיל שוב & pause & exit /b 1)
start "" http://localhost:8787
set LOCAL=1
node server.js
''')
W=B+'win/'
shutil.copy(B+'win/chartready.ico',P+'chartready.ico')
for src,dst in [('ChartReady.vbs','ChartReady.vbs'),('stop.vbs','כיבוי ChartReady.vbs'),('autostart.vbs','הפעלה אוטומטית עם המחשב.vbs')]:
    open(P+dst,'w',encoding='utf-16',newline='\r\n').write(open(W+src).read())
open(P+'קרא אותי.txt','w').write('''ChartReady · הגרסה האישית (רצה על המחשב שלך)

פעם אחת בלבד:
  להתקין Node.js מ- https://nodejs.org (הגרסה המומלצת, LTS).

ווינדוס (ברקע, בלי חלון):
  הפעלה:   לחיצה כפולה על "ChartReady.vbs". נפתח כאפליקציה בחלון משלו,
           ובפעם הראשונה נוצר אייקון ChartReady בשולחן העבודה. מעכשיו פותחים משם.
  כיבוי:    לחיצה כפולה על "כיבוי ChartReady.vbs".
  עם המחשב: לחיצה כפולה על "הפעלה אוטומטית עם המחשב.vbs" (לחיצה נוספת = ביטול).
           מעכשיו הוא פועל ברקע מרגע שהמחשב נדלק, והטלפון יכול להתחבר מתי שרוצים.
  "הפעלה-בחלון (לבדיקות).bat" מראה חלון עם הכתובות, למקרה שמשהו לא עובד.

מק:
  לחיצה כפולה על "הפעלה-מק.command" (בפעם הראשונה: קליק ימני › Open › Open).

שלט רחוק מהטלפון:
  1. הטלפון והמחשב על אותה רשת WiFi.
  2. במחשב: הגדרות › אודות › סודי › שלט רחוק. מופיע QR.
  3. בטלפון: לסרוק את ה-QR. הטלפון מתחבר לבד, בלי קוד.
  5. כדאי לשמור את הכתובת למסך הבית בטלפון.
  אם חומת האש של ווינדוס שואלת, לאשר "רשתות פרטיות".
''')

open(OUT+'chartready-אישי-קובץ-יחיד.html','w').write(single)
# ---- public: GitHub Pages, secret always wrong ----
G=OUT+'ChartReady-ציבורי/'
page,single=build(False)
site(G,page); open(G+'.nojekyll','w').write('')
open(G+'קרא אותי.txt','w').write('''ChartReady · הגרסה הציבורית (לתלמידים)

העלאה ל-GitHub Pages (פעם אחת, כ-5 דקות):
  1. להיכנס ל- https://github.com ולפתוח חשבון חינם.
  2. למעלה מימין: + › New repository. שם, למשל: chartready. לסמן Public › Create repository.
  3. בדף שנפתח: "uploading an existing file" › לגרור את כל הקבצים מהתיקייה הזו (לא את התיקייה עצמה) › Commit changes.
  4. Settings › Pages › Branch: main › Save.
  5. אחרי דקה-שתיים הכתובת מופיעה שם, למשל: https://השם-שלך.github.io/chartready/

עדכון גרסה: אותו דבר, פשוט לגרור את הקבצים החדשים מעל הישנים.
התלמידים מקבלים את העדכון בפתיחה הבאה עם אינטרנט.

בגרסה הזו "סודי" קיים, אבל כל סיסמה שגויה.
''')
open(OUT+'chartready-ציבורי-קובץ-יחיד.html','w').write(single)
subprocess.run(['python3',B+'build.py'],check=True,stdout=subprocess.DEVNULL)  # leave test build in default (public) state
print('release ok')
