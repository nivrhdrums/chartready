import re,os
os.chdir('/home/claude')
B='/tmp/claude-0/build/'
s=open(B+'template.html').read()
P=lambda k:open(B+f'part_{k}.txt').read()
out=s.replace('{{FONT}}',P('font')).replace('{{UICSS}}',open(B+'part_ui.css').read()).replace('{{UIJS}}',P('uijs')).replace('{{GEN}}',P('gen2')).replace('{{NOTA}}',P('nota')).replace('{{AUDIO}}',P('audio')).replace('{{FILM}}',P('film')).replace('{{EDITOR}}',P('editor')).replace('{{REMOTE}}',P('remote')).replace('{{VER}}',os.environ.get('CR_VER','dev')).replace('{{SECRET_OPEN}}',os.environ.get('SECRET_OPEN','false'))
open('chartready.html','w').write(out); open('nivbot.html','w').write(out)
js=re.findall(r'<script>(.*?)</script>',out,re.S); open('/tmp/t.js','w').write(js[-1])
old=open('chartready-site/index.html').read(); head=old[:old.index('<title>')]; tail=old[old.rindex("<script>\nif('serviceWorker'"):]
x=out.replace('<meta name="claude:viewport-fit-sides" content="cover">\n',''); head=head.replace('padding-bottom:env(safe-area-inset-bottom,0px);',''); i=x.index('</style>')+len('</style>')
page=head+x[:i]+'\n</head>\n<body>\n'+x[i:]+'\n'+tail
open('chartready-site/index.html','w').write(page); open('cr-server/public/index.html','w').write(page)
for p in ('chartready-site/sw.js','cr-server/public/sw.js'):
    w=open(p).read(); w=re.sub(r"chartready-v\d+","chartready-v15",w); open(p,'w').write(w)
html=out.replace("rhythm=genRhythm(); render();\n","rhythm=genRhythm(); render();\nwindow.__nb={setR:r=>{rhythm=r;render();},S,initAudio,get master(){return master},get rhythm(){return rhythm},TAP,FILM,filmDraw,genRhythm,beatCode,tapHit,filmOpen,filmGo,filmExit,start,stop,get ctx(){return ctx},get cur(){return cur},tapUI,diffOf,svgBar,widthFor,allPatterns,get ED(){return ED},get REC(){return REC},edNow,edCamT,setBpm,retime,get TRK(){return TRK},get visQ(){return visQ},edMix,lagToTimes,onsetsOf,envOf,histEntry,histBar,svgBar};\n",1)
open(B+'test.html','w').write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'+html+'</body></html>')
print('built')
