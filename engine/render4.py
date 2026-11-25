import json, html, re, os
K=os.path.dirname(os.path.abspath(__file__))+'/'
B=json.load(open(K+'out/board.json'))
META=json.load(open(K+'meta.json'))
A=B['assets']; R=B['regime']; e=html.escape
# reuse news, regime and helper logic from render3 without executing its page build
NEWS=[(n['tag'],n['headline'],n['summary'],n['source'],n['url'],n['affects']) for n in json.load(open(K+'news.json'))]
def tilecls(a):
    s,t,st=a['score'],a['trend'],a['state']
    if st=='Aligned':
        if abs(s)>=4 and abs(t)>=4: return 'sr' if s<0 else 'sl'
        return 'or' if s<0 else 'ol'
    if st=='Conflict': return 'oy'
    if st=='Macro only': return 'or' if s<0 else 'ol'
    if st=='Trend only': return 'or' if t<0 else 'ol'
    return 'ow'
def statetxt(a):
    s,t,st=a['score'],a['trend'],a['state']; d=lambda x:'short' if x<0 else 'long'
    return {'Aligned':f"Aligned, {d(s)}",'Conflict':'Conflict','Macro only':f"Mac only, {d(s)}",'Trend only':f"Cheese only, {d(t)}",'Neutral':'No lean'}[st]
def lean(a):
    if a['state']=='Aligned': return 'long' if a['score']>0 else 'short'
    return 'mixed'
def px(a):
    v=a['last']; return f"{v:,.0f}" if v>=1000 else (f"{v:.4f}" if v<20 else f"{v:,.2f}")
def num(x): return f"{x:+d}" if x else "0"
def mi(x): return num(x).replace('-','−')
def short(a): return a['name'].split(' (')[0].replace(' crude','')
def sc(v,big=False): return f'<i class="sc{" big" if big else ""}"><u style="--p:{(v+10)*5}%"></u></i>'
ENDS='<span class="ends"><em>−10</em><em>0</em><em>+10</em></span>'
GO=[]
for a in A:
    if a['group'] not in GO: GO.append(a['group'])
def tile(i,a):
    k=a['key']
    return (f'<button class="tile {tilecls(a)}" data-f="{lean(a)}" data-k="{k}" data-g="{GO.index(a["group"])*100+i}" data-m="{a["score"]}" data-c="{a["trend"]}" style="view-transition-name:t-{k}" aria-label="{e(a["name"])}, Mac {num(a["score"])}, Cheese {num(a["trend"])}, {e(statetxt(a))}">'
      f'<span class="tt"><span class="gk">{e(a["group"])}</span><b>{e(short(a))}</b><span class="p">{px(a)}<em class="{"u" if a["d5"]>0 else "d"}">{a["d5"]:+.1f}% 5d</em></span></span>'
      f'<span class="nums"><span>Mac<span class="v" data-n="{a["score"]}">{mi(a["score"])}</span>{sc(a["score"])}{ENDS}</span><span>Cheese<span class="v" data-n="{a["trend"]}">{mi(a["trend"])}</span>{sc(a["trend"])}{ENDS}</span></span>'
      f'<span class="s">{e(statetxt(a))}</span></button>')
def div(v,mx):  # diverging bar
    w=min(abs(v)/mx,1)*50
    side='l' if v<0 else 'r'
    c='red' if v<0 else ('lime' if v>0 else 'yel')
    return f'<i class="db"><u class="{side} {c}" style="width:{w:.1f}%"></u></i>'
def row(a,i):
    return (f'<button class="lr" data-k="{a["key"]}" data-f="{lean(a)}" data-g="{GO.index(a["group"])*100+i}" data-m="{a["score"]}" data-c="{a["trend"]}" style="view-transition-name:r-{a["key"]}">'
      f'<span class="ln"><b>{e(short(a))}</b><small>{e(a["group"])}</small></span>'
      f'<span class="lc"><span class="lv">{mi(a["score"])}</span>{div(a["score"],10)}</span>'
      f'<span class="lc"><span class="lv">{mi(a["trend"])}</span>{div(a["trend"],10)}</span>'
      f'<span class="ls {tilecls(a)}">{e(statetxt(a))}</span>'
      f'<span class="l5 {"u" if a["d5"]>0 else "d"}">{a["d5"]:+.1f}%</span></button>')
def pnum(s):
    m=re.search(r'[-+]?\d+(\.\d+)?',s); return float(m.group()) if m else 0
def detail(a):
    c=tilecls(a)
    drv=''
    for d in a['drivers']:
        v=d['pts']*d['w']; nm=e(d['name'])+(' <em>×2</em>' if d['w']==2 else '')
        bar=div(v,2) if d['w'] else '<i class="db off"></i>'
        drv+=f'<div class="cr"><div class="ct"><span class="n">{nm}</span><span class="t">{e(d["read"])}</span></div>{bar}<div class="src">{e(d["src"])}</div></div>'
    trd=''
    for t in a['trendrows']:
        v=pnum(t[1]); trd+=f'<div class="cr"><div class="ct"><span class="n">{e(t[0])}</span><span class="t">{e(t[1])}</span></div>{div(v if t[2] else 0,20) if t[2] else div(0,1)}</div>'
    st=a['state']
    chk={'Aligned':('Aligned',"Mac and Cheese point the same way."),'Conflict':('Conflict',"Mac and Cheese point opposite ways."),'Macro only':('Mac only',"Mac leans one way; price has not confirmed it."),'Trend only':('Cheese only',"Price is trending; the Mac backdrop does not lean the same way."),'Neutral':('No lean',"Neither Mac nor Cheese has a clear direction.")}[st]
    fl=''.join(f'<div class="sv"><span>{e(n)} neutral</span><span>Mac {mi(a["score"])} → {mi(nw)}</span></div>' for n,nw in a['flips']) or '<p class="pp">No single driver moves the Mac score materially.</p>'
    ev=''.join(f'<div class="evr"><span>{e(x[1])}</span><span>{e(x[0])}</span></div>' for x in sorted(a['events'],key=lambda x:x[2]))
    return (f'<template id="d-{a["key"]}" data-c="{c}" data-share="{e(short(a))} is a {num(a["score"])} on Mac &amp; Cheese, Cheese {num(a["trend"])}." data-name="{e(short(a))}" data-group="{e(a["group"])}" data-mac="{a["score"]}" data-cheese="{a["trend"]}" data-state="{e(statetxt(a))}" data-px="{px(a)}" data-d5="{a["d5"]:+.1f}">'
      f'<div class="hd"><div><span class="gk2">{e(a["group"])}</span><b>{e(a["name"])}</b><span class="q">{e(a["stance"])} · {e(a["conviction"].lower())} conviction</span><span class="q">{px(a)} · 5d {a["d5"]:+.1f}% · 20d {a["d20"]:+.1f}%</span></div>'
      f'<div class="hb"><button class="ib pv" aria-label="Previous asset">‹</button><button class="ib nx" aria-label="Next asset">›</button><button class="ib x" aria-label="Close">×</button></div></div>'
      f'<div class="two"><div>Mac<span class="v">{mi(a["score"])}</span>{sc(a["score"],1)}{ENDS}</div><div>Cheese<span class="v">{mi(a["trend"])}</span>{sc(a["trend"],1)}{ENDS}</div></div>'
      f'<div class="verdict {c}"><b>{chk[0]}.</b> {chk[1]}</div><p class="pp why">{e(a["why"])}</p>'
      f'<div class="sec">Mac · economic drivers</div>{drv}<div class="sec">Cheese · price trend</div>{trd}'
      f'<div class="sec">Mac · driver sensitivity</div>{fl}<div class="sec">Key events</div><div class="evs">{ev}</div>'
      f'<button class="share">Share this reading</button><div class="shm" hidden><div class="shp"><img alt="Share card preview"></div><div class="shl"><button data-to="instagram">Instagram</button><button data-to="snapchat">Snapchat</button><button data-to="facebook">Facebook</button><button data-to="x">X</button><button data-to="whatsapp">WhatsApp</button><button data-to="save">Save image</button><button data-to="copy">Copy link</button></div></div></template>')
# ---- board summary
nl=sum(lean(a)=='long' for a in A); ns=sum(lean(a)=='short' for a in A); nm=len(A)-nl-ns
avgM=sum(a['score'] for a in A)/len(A); avgC=sum(a['trend'] for a in A)/len(A)
board=round((avgM+avgC)/2)
mixed=[short(a) for a in A if lean(a)=='mixed']
tone='Risk-off' if board<=-3 else ('Risk-on' if board>=3 else 'Two-way')
if ns>=nl: line=f"{ns} of {len(A)} assets aligned short"
else: line=f"{nl} of {len(A)} assets aligned long"
line+= (f"; {', '.join(mixed)} mixed." if mixed else '.') if len(mixed)<=3 else f"; {nm} mixed."
# ---- map
pts={}
for a in A: pts.setdefault((a['score'],a['trend']),[]).append(a)
def X(v): return 200+v*14.5
def Y(v): return 200-v*14.5
mp=['<svg viewBox="0 10 400 396" class="map" role="img" aria-label="Mac and Cheese map: Mac score across, Cheese score up">',
 '<defs><radialGradient id="gl" r=".7"><stop offset="0" stop-color="#4EE3AE" stop-opacity=".16"/><stop offset="1" stop-color="#4EE3AE" stop-opacity="0"/></radialGradient><radialGradient id="gs" cx="0" cy="1" r=".9"><stop offset="0" stop-color="#FF6A3D" stop-opacity=".22"/><stop offset="1" stop-color="#FF6A3D" stop-opacity="0"/></radialGradient><radialGradient id="gr" cx="1" cy="0" r=".9"><stop offset="0" stop-color="#4EE3AE" stop-opacity=".2"/><stop offset="1" stop-color="#4EE3AE" stop-opacity="0"/></radialGradient></defs>',
 '<rect x="40" y="40" width="320" height="320" rx="26" class="mf"/>',
 '<rect x="40" y="200" width="160" height="160" rx="22" fill="url(#gs)"/><rect x="200" y="40" width="160" height="160" rx="22" fill="url(#gr)"/>']
for v in (-10,-5,5,10):
    mp.append(f'<line x1="{X(v)}" y1="40" x2="{X(v)}" y2="360" class="gd"/><line x1="40" y1="{Y(v)}" x2="360" y2="{Y(v)}" class="gd"/>')
mp.append('<line x1="200" y1="40" x2="200" y2="360" class="ax"/><line x1="40" y1="200" x2="360" y2="200" class="ax"/>')
mp.append('<text x="360" y="30" class="ql lime" text-anchor="end">ALIGNED LONG</text><text x="40" y="377" class="ql red">ALIGNED SHORT</text><text x="40" y="30" class="ql yel">CONFLICT</text><text x="360" y="377" class="ql yel" text-anchor="end">CONFLICT</text>')
mp.append('<text x="200" y="398" class="al" text-anchor="middle">MAC →</text><text x="16" y="200" class="al" text-anchor="middle" transform="rotate(-90 16 200)">CHEESE →</text>')
mp.append('<text x="40" y="398" class="tn">−10</text><text x="360" y="398" class="tn" text-anchor="end">+10</text>')
items=sorted(pts.items(),key=lambda kv:(kv[0][1],kv[0][0]))
dots=[(X(m),Y(c),7+2*(len(g)-1)) for (m,c),g in items]
boxes=[]
def hit(b):
    x0,y0,x1,y1=b
    if x0<42 or x1>358 or y0<42 or y1>358: return True
    for (cx,cy,r) in dots:
        if x0<cx+r and x1>cx-r and y0<cy+r and y1>cy-r: return True
    for q in boxes:
        if x0<q[2]+3 and x1>q[0]-3 and y0<q[3]+2 and y1>q[1]-2: return True
    return False
for j,((m,c),g) in enumerate(items):
    a=g[0]; cl='red' if lean(a)=='short' else ('lime' if lean(a)=='long' else 'yel')
    x,y=X(m),Y(c); r=7+2*(len(g)-1); lab=' · '.join(short(z) for z in g); w=len(lab)*6.1; h=11
    cands=[(r+5,4,'start'),(-r-5,4,'end'),(0,-r-6,'middle'),(0,r+13,'middle'),(r+3,-r-2,'start'),(-r-3,-r-2,'end'),(r+3,r+10,'start'),(-r-3,r+10,'end')]
    pick=None
    for dx,dy,an in cands:
        x0={'start':x+dx,'end':x+dx-w,'middle':x+dx-w/2}[an]; b=(x0,y+dy-h+2,x0+w,y+dy+2)
        if not hit(b): pick=(dx,dy,an,b); break
    if not pick:
        dx,dy,an=cands[0]; pick=(dx,dy,an,(x+dx,y+dy-h,x+dx+w,y+dy))
    dx,dy,an,b=pick; boxes.append(b)
    keys=','.join(z['key'] for z in g)
    mp.append(f'<g class="pt {cl}" data-ks="{keys}" tabindex="0" role="button" aria-label="{e(lab)}: Mac {num(m)}, Cheese {num(c)}" style="--d:{j*60}ms"><circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="halo"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{4.5+1.5*(len(g)-1)}" class="dot"/><text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{an}" class="pl">{e(lab)}</text></g>')
mp.append('</svg>')
MAP=''.join(mp)
# ---- regime
def rt(k,v,d,c,sig): return f'<div class="rt {c}"><div class="k"><i class="d {c}"></i>{k}</div><div class="v">{v}</div><div class="dd">{d}</div><div class="sig">{sig}</div></div>'
RT={'Volatility (VIX)':rt('Volatility (VIX)',f"{R['vix']:.1f}",f"{R['vix5']:+.0f}% in 5 days",'red','Supports shorts'),
'High-yield spread':rt('High-yield spread',f"{R['hy']:.2f}%",f"{R['hy5']:+.2f} in 5 days",'red','Supports shorts'),
'Financial conditions':rt('Financial conditions',f"{R['nfci']:.2f}",'Loose','lime','Supports longs'),
'US 10y yield':rt('US 10y yield',f"{R['y10']:.2f}%",f"{R['y10_5']:+.2f} in 5 days",'yel','Mixed'),
'10y real yield':rt('10y real yield',f"{R['real']:.2f}%",f"{R['real5']:+.2f} in 5 days",'lime','Supports longs'),
'10y breakeven':rt('10y breakeven',f"{R['be']:.2f}%",'Inflation expectations','yel','Mixed'),
'US dollar (DXY)':rt('US dollar (DXY)',f"{R['dxy']:.1f}",f"{R['dxy50']:+.1f}% vs 50-day",'red','Supports shorts'),
'Jobless claims':rt('Jobless claims',f"{R['ics']/1000:.0f}k",'Low','lime','Supports longs')}
RG=[('Volatility and credit',['Volatility (VIX)','High-yield spread','Financial conditions']),('Rates and inflation',['US 10y yield','10y real yield','10y breakeven']),('Dollar and labour',['US dollar (DXY)','Jobless claims'])]
regime=''.join(f'<div class="rg"><div class="rl">{n}</div><div class="reg">'+''.join(RT[k] for k in ks)+'</div></div>' for n,ks in RG)
# ---- ticker
def tk(sym,val,chg,v): return f'<span class="ti"><b>{sym}</b><span>{val}</span><em class="{"u" if v>0 else "d" if v<0 else "n"}">{chg}</em></span>'
T=[tk(e(short(a)),px(a),f"{a['d5']:+.1f}%",a['d5']) for a in A]+[tk('DXY',f"{R['dxy']:.1f}",f"{R['dxy50']:+.1f}%",R['dxy50']),tk('US10Y',f"{R['y10']:.2f}%",f"{R['y10_5']*100:+.0f}bp",R['y10_5']),tk('VIX',f"{R['vix']:.1f}",f"{R['vix5']:+.0f}%",R['vix5'])]
TKH=''.join(T)
cards=''.join(f'<article class="nc{" on" if i==0 else ""}"><span class="ng">{e(t)}</span><h3>{e(h)}</h3>'+(f'<p>{e(b)}</p>' if b else '')+f'<div class="nf"><a href="{u}" target="_blank" rel="noopener noreferrer">{e(s)}</a>'+''.join(f'<span>{e(x)}</span>' for x in af)+'</div></article>' for i,(t,h,b,s,u,af) in enumerate(NEWS))
tiles=''.join(tile(i,a) for i,a in enumerate(A))
rows=''.join(row(a,i) for i,a in enumerate(A))
dets=''.join(detail(a) for a in A)
CSS=open(K+'v4.css').read()
JS=open(K+'v4.js').read()
TPL=open(K+'v4.html').read()
rep={'%CSS%':CSS,'%JS%':JS,'%TICKER%':TKH+TKH,'%ASOF%':e(B['asof'].replace(', ',' · ')),'%TONE%':tone,'%LINE%':e(line),
'%NS%':str(ns),'%NL%':str(nl),'%NM%':str(nm),'%NA%':str(len(A)),'%BOARD%':mi(board),'%AVGM%':f"{avgM:+.1f}".replace('-','−'),'%AVGC%':f"{avgC:+.1f}".replace('-','−'),
'%BOARDP%':f"{(board+10)*5}%",'%MAP%':MAP,'%NEWS%':cards,'%NNEWS%':str(len(NEWS)),'%REGIME%':regime,'%TILES%':tiles,'%ROWS%':rows,'%DETS%':dets,'%ISO%':META['asof_iso'],'%SOURCES%':e(META['sources'])}
for k,v in rep.items(): TPL=TPL.replace(k,v)
open(K+'out/index.html','w').write(TPL)
print(len(TPL), tone, line, board)
