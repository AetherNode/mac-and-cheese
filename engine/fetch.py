# Fetches all market data for Mac and Cheese into ./data and eia.json. Standard library only.
import urllib.request, json, os, sys, time, re, datetime, statistics
K=os.path.dirname(os.path.abspath(__file__))+'/'; D=K+'data/'
UA={'User-Agent':'mac-and-cheese/1.0 (+https://aethernode.github.io/mac-and-cheese/)'}
def get(url,tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=40) as r: return r.read().decode('utf-8','replace')
        except Exception as e:
            err=e; time.sleep(3*(i+1))
    raise RuntimeError(f'{url}: {err}')
fails=[]
start=(datetime.date.today()-datetime.timedelta(days=400)).isoformat()
for s in ['BAMLH0A0HYM2','DEXJPUS','DEXUSEU','DEXUSUK','DFII10','DGS10','DGS2','DTWEXBGS','ICSA','NFCI','T10Y2Y','T10YIE','VIXCLS']:
    try:
        t=get(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}&cosd={start}')
        if not t.lower().startswith('observation_date') and 'DATE' not in t[:20].upper(): raise RuntimeError('not csv')
        open(D+s+'.csv','w').write(t)
    except Exception as e: fails.append(f'FRED {s}: {e}')
q='$order=report_date_as_yyyy_mm_dd%20DESC&$limit=12'
for kind,ds,codes in [('d','72hh-3qpy',['088691','084691','067651']),('t','gpe5-46if',['13874A','209742','239742','124603','133741'])]:
    for c in codes:
        try:
            j=json.loads(get(f'https://publicreporting.cftc.gov/resource/{ds}.json?cftc_contract_market_code={c}&{q}'))
            if not j: raise RuntimeError('empty')
            json.dump(j,open(D+f'cot_{kind}_{c}.json','w'))
        except Exception as e: fails.append(f'CFTC {c}: {e}')
# Yahoo chart API (unofficial)
S=['GC=F','SI=F','^FTSE','^GDAXI','^STOXX50E','^RUT','CL=F','BZ=F','^GSPC','^NDX','^DJI','^N225','BTC-USD','^VIX','DX-Y.NYB']
rows=['sym|date|last|d1|d5|d20|sma50|sma200|hi|lo']
for s in S:
    try:
        u='https://query1.finance.yahoo.com/v8/finance/chart/'+urllib.request.quote(s,safe='')+'?range=1y&interval=1d&includePrePost=false'
        res=json.loads(get(u))['chart']['result'][0]
        pts=[[t,c] for t,c in zip(res['timestamp'],res['indicators']['quote'][0]['close']) if c is not None]
        m=res['meta']; live,lt=m.get('regularMarketPrice'),m.get('regularMarketTime')
        day=lambda t:datetime.datetime.fromtimestamp(t,datetime.timezone.utc).date().isoformat()
        if live and lt:
            if day(lt)==day(pts[-1][0]): pts[-1][1]=live
            elif day(lt)>day(pts[-1][0]): pts.append([lt,live])
        v=[p[1] for p in pts]; n=len(v); avg=lambda k:sum(v[-k:])/min(k,n); f=lambda x:f'{x:.2f}'
        rows.append('|'.join([s,day(pts[-1][0]),f(v[-1]),f(v[-2]),f(v[-6]),f(v[-21]),f(avg(50)),f(avg(200)),f(max(v)),f(min(v))]))
        time.sleep(0.6)
    except Exception as e: fails.append(f'Yahoo {s}: {e}')
if len(rows)==len(S)+1: open(D+'yahoo_1y.psv','w').write('\n'.join(rows)+'\n')
# EIA weekly crude stocks (excluding SPR)
try:
    h=get('https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=WCESTUS1&f=W')
    W=[]
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>',h,flags=re.S|re.I):
        txt=re.sub(r'<[^>]+>',' ',tr); txt=re.sub(r'&nbsp;',' ',txt); txt=re.sub(r'\s+',' ',txt).strip()
        mm=re.match(r'(\d{4})-[A-Z][a-z]{2}',txt)
        if not mm: continue
        for a,b,val in re.findall(r'(\d{2})/(\d{2}) ([\d,]+)',txt): W.append((f'{mm.group(1)}-{a}-{b}',int(val.replace(',',''))/1000))
    if len(W)<60: raise RuntimeError('table not found')
    L,P,Y=W[-1],W[-2],W[-53]; d=datetime.date.fromisoformat(L[0])
    json.dump({'stocks_m':round(L[1],1),'week_change_m':round(L[1]-P[1],1),'vs_last_year_m':round(L[1]-Y[1],1),'week_label':f"{d.day} {d.strftime('%b')}",'week_end':L[0]},open(K+'eia.json','w'),indent=1)
except Exception as e: fails.append(f'EIA: {e}')
print('\n'.join(fails) if fails else 'all data fetched')
# Prices are essential; other sources fall back to the last saved files.
if any(x.startswith('Yahoo') for x in fails): sys.exit('Price fetch failed; site not updated.')
