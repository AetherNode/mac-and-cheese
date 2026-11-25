# Rebuilds Mac and Cheese from ./data, eia.json, news.json and events.json. Writes out/index.html.
import json, os, sys, csv, datetime, subprocess
from zoneinfo import ZoneInfo
K=os.path.dirname(os.path.abspath(__file__))+'/'
def dm(d): return f"{d.day} {d.strftime('%b')}"
now=datetime.datetime.now(ZoneInfo('Europe/London'))
Y={l.split('|')[0]:l.split('|')[1] for l in open(K+'data/yahoo_1y.psv').read().strip().split('\n')[1:] if '|' in l}
need=['GC=F','SI=F','^FTSE','^GDAXI','^STOXX50E','^RUT','CL=F','BZ=F','^GSPC','^NDX','^DJI','^N225','BTC-USD','^VIX','DX-Y.NYB']
miss=[s for s in need if s not in Y]
if miss: sys.exit('Missing Yahoo symbols: '+', '.join(miss))
pxd=max(Y.values()); lag=[s for s in need if Y[s]<pxd]
def fl(s):
    r=[x for x in csv.reader(open(K+'data/'+s+'.csv'))][1:]; r=[x for x in r if len(x)>1 and x[1] not in ('','.')]; return r[-1][0]
fd=sorted({fl(s) for s in ['BAMLH0A0HYM2','DFII10','DGS10','T10YIE','DEXUSUK']})
cot=json.load(open(K+'data/cot_d_088691.json'))[0]['report_date_as_yyyy_mm_dd'][:10]
eia=json.load(open(K+'eia.json'))
D=lambda s:dm(datetime.date.fromisoformat(s))
names={'^N225':'Nikkei','^FTSE':'FTSE','^GDAXI':'DAX','^STOXX50E':'Euro Stoxx'}
lagtxt=(' ('+', '.join(f"{names.get(s,s)}: {D(Y[s])} close" for s in lag)+')') if lag else ''
fred=f"to {D(fd[0])}" if fd[0]==fd[-1] else f"{D(fd[0])} to {D(fd[-1])}"
meta={"asof_iso":now.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z'),
"asof_label":now.strftime('%a ')+str(now.day)+now.strftime(' %b %Y, %H:%M London'),
"yahoo_label":"live "+dm(now),
"sources":f"Prices: Yahoo Finance, {now.strftime('%H:%M')} London{lagtxt}. Rates, spreads and dollar: FRED, {fred}. Positioning: CFTC, {D(cot)}. Oil stocks: EIA, week to {eia['week_label']}."}
json.dump(meta,open(K+'meta.json','w'),indent=1)
n=json.load(open(K+'news.json')); assert 3<=len(n)<=10 and all(x['headline'] and x['url'].startswith('http') for x in n), 'news.json invalid'
subprocess.run([sys.executable,'-I',K+'score.py'],check=True,stdout=subprocess.DEVNULL)
B=json.load(open(K+'out/board.json')); assert len(B['assets'])==13
subprocess.run([sys.executable,'-I',K+'render4.py'],check=True)
ev=json.load(open(K+'events.json')); today=now.date()
for g,xs in ev.items():
    up=[x for x in xs if datetime.date.fromisoformat(x['date'])>=today]
    if len(up)<2: print(f'WARNING events group "{g}" has only {len(up)} upcoming events; add the next dates to events.json')
for a in B['assets']: print(f"{a['name']:24s} Mac {a['score']:+3d}  Cheese {a['trend']:+3d}  {a['state']}")
print(meta['sources'])
