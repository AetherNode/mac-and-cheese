import csv, json, datetime, os
K=os.path.dirname(os.path.abspath(__file__))+'/'
D=K+'data/'
META=json.load(open(K+'meta.json'))
EIA=json.load(open(K+'eia.json'))
EV=json.load(open(K+'events.json'))
def fred(s):
    r=list(csv.reader(open(D+s+'.csv')))[1:]
    return [(x[0],float(x[1])) for x in r if len(x)>1 and x[1] not in ('','.')]
def chg(s,n):
    v=fred(s); return v[-1][1], v[-1][1]-v[-1-n][1], v[-1][0]
Y={}
for l in open(D+'yahoo_1y.psv').read().strip().split('\n')[1:]:
    p=l.split('|'); Y[p[0]]=dict(date=p[1],last=float(p[2]),d1=float(p[3]),d5=float(p[4]),d20=float(p[5]),sma50=float(p[6]),sma200=float(p[7]),hi=float(p[8]),lo=float(p[9]))
def pct(a,b): return (a/b-1)*100
real,real5,real_d=chg('DFII10',5)
y10,y10_5,y10_d=chg('DGS10',5)
be,be5,be_d=chg('T10YIE',5)
hy,hy5,hy_d=chg('BAMLH0A0HYM2',5)
gbp,gbp20,gbp_d=chg('DEXUSUK',20)
eur,eur20,eur_d=chg('DEXUSEU',20)
jpy,jpy20,jpy_d=chg('DEXJPUS',20)
nfci,nfci4,nfci_d=chg('NFCI',4)
ics,ics4,ics_d=chg('ICSA',4)
gbp_p=pct(gbp,gbp-gbp20); eur_p=pct(eur,eur-eur20); jpy_p=pct(jpy,jpy-jpy20)
vix=Y['^VIX']; dxy=Y['DX-Y.NYB']
def _cot(kind,code):
    r=json.load(open(D+f'cot_{kind}_{code}.json'))[0]; g=lambda k:float(r.get(k) or 0)
    if kind=='d': net=g('m_money_positions_long_all')-g('m_money_positions_short_all'); wk=g('change_in_m_money_long_all')-g('change_in_m_money_short_all')
    else: net=g('lev_money_positions_long')-g('lev_money_positions_short'); wk=g('change_in_lev_money_long')-g('change_in_lev_money_short')
    return (net,wk,g('open_interest_all'),r['report_date_as_yyyy_mm_dd'][:10])
COT={'gold':_cot('d','088691'),'silver':_cot('d','084691'),'wti':_cot('d','067651'),'sp':_cot('t','13874A'),'ndx':_cot('t','209742'),'rut':_cot('t','239742'),'dow':_cot('t','124603'),'btc':_cot('t','133741')}
def _dm(iso): d=datetime.date.fromisoformat(iso); return f"{d.day} {d.strftime('%b')}"
COTD=_dm(COT['gold'][3])
LIVE=META['yahoo_label']
def sgn(x,up,dn): return 1 if x>up else (-1 if x<dn else 0)
def D_(name,read,pts,w,src): return dict(name=name,read=read,pts=pts,w=w,src=src)
# shared drivers
def d_vix(): 
    spike=pct(vix['last'],vix['d5'])
    pts=-1 if (vix['last']>25 or spike>30) else (1 if vix['last']<16 else 0)
    return D_('Volatility (VIX)',f"{vix['last']:.1f}, {spike:+.0f}% in 5 days",pts,2,f'Yahoo ^VIX, {LIVE}')
def d_credit():
    pts=-1 if hy5>0.20 else (1 if hy5<-0.20 else 0)
    return D_('Credit spreads',f"HY spread {hy:.2f}%, {hy5:+.2f} in 5 days",pts,1,f'FRED BAMLH0A0HYM2, {hy_d}')
def d_dxy(name='US dollar',inv=True):
    p=pct(dxy['last'],dxy['sma50']); pts=-1 if p>1 else (1 if p<-1 else 0)
    return D_(name,f"DXY {dxy['last']:.1f}, {p:+.1f}% vs 50-day",pts,1,f'Yahoo DX-Y.NYB, {LIVE}')
def d_real(): 
    pts=1 if real5<-0.10 else (-1 if real5>0.10 else 0)
    return D_('Real yields',f"10y real {real:.2f}%, {real5:+.2f} in 5 days",pts,1,f'FRED DFII10, {real_d}')
def d_nfci(): 
    pts=1 if nfci<-0.3 else (-1 if nfci>0 else 0)
    return D_('Financial conditions',f"NFCI {nfci:.2f} ({'loose' if nfci<-0.3 else 'tight' if nfci>0 else 'neutral'})",pts,1,f'FRED NFCI, {nfci_d}')
def d_claims():
    pts=1 if ics<220000 else (-1 if ics>260000 else 0)
    return D_('Jobless claims',f"{ics/1000:.0f}k a week",pts,1,f'FRED ICSA, {ics_d}')
def d_cot(k,label,flip=False):
    net,wk,oi,rank=COT[k]; r=wk/oi*100
    pts=1 if r>1 else (-1 if r<-1 else 0)
    return D_(label,f"net {net/1000:+.0f}k, {wk/1000:+.0f}k last week ({r:+.1f}% of OI)",pts,1,f'CFTC, report date {COTD}')
def d_cot_info(k,label):
    net,wk,oi,rank=COT[k]
    return D_(label,f"net {net/1000:+.0f}k, {wk/1000:+.0f}k last week; shown, not scored",0,0,f'CFTC, report date {COTD}')
A=[]
def side(x): return 1 if x>=2 else (-1 if x<=-2 else 0)
def asset(key,name,yk,group,drivers,events):
    p=Y[yk]
    sm=sum(d['pts']*d['w'] for d in drivers); mx=sum(d['w'] for d in drivers)
    score=int(round(10*sm/mx)) if mx else 0
    nbull=sum(1 for d in drivers if d['pts']>0 and d['w']); nbear=sum(1 for d in drivers if d['pts']<0 and d['w']); n=sum(1 for d in drivers if d['w'])
    agree=max(nbull,nbear)/n
    stance='Longs only' if score>=4 else 'Lean long' if score>=2 else 'Shorts only' if score<=-4 else 'Lean short' if score<=-2 else 'Both ways'
    conv='High' if abs(score)>=6 and agree>=0.6 else 'Medium' if abs(score)>=3 else 'Low'
    d5=pct(p['last'],p['d5']); d20=pct(p['last'],p['d20'])
    v50=pct(p['last'],p['sma50']); v200=pct(p['last'],p['sma200']); x=pct(p['sma50'],p['sma200'])
    T=[('Price vs 50-day',f"{v50:+.1f}%",1 if v50>0 else -1),('Price vs 200-day',f"{v200:+.1f}%",1 if v200>0 else -1),('50-day vs 200-day',f"{x:+.1f}%",1 if x>0 else -1),('20-day move',f"{d20:+.1f}%",1 if d20>3 else (-1 if d20<-3 else 0)),('5-day move',f"{d5:+.1f}%",1 if d5>1.5 else (-1 if d5<-1.5 else 0))]
    trend=int(round(10*sum(t[2] for t in T)/len(T)))
    sm_,st_=side(score),side(trend)
    if sm_!=0 and sm_==st_: state='Aligned'
    elif sm_*st_==-1: state='Conflict'
    elif sm_!=0: state='Macro only'
    elif st_!=0: state='Trend only'
    else: state='Neutral'
    up=[d['name'] for d in drivers if d['pts']>0 and d['w']]; dn=[d['name'] for d in drivers if d['pts']<0 and d['w']]
    why=('Pointing down: '+', '.join(dn)+'. ' if dn else 'Nothing points down. ')+('Pointing up: '+', '.join(up)+'.' if up else 'Nothing points up.')
    flips=[]
    for d in drivers:
        if d['pts'] and d['w']:
            nw=int(round(10*(sm-d['pts']*d['w'])/mx))
            if abs(nw)<abs(score): flips.append((d['name'],nw))
    flips.sort(key=lambda z:abs(z[1])); flips=flips[:2]
    A.append(dict(key=key,name=name,group=group,score=score,trend=trend,state=state,stance=stance,conviction=conv,last=p['last'],pxdate=p['date'],d1=pct(p['last'],p['d1']),d5=d5,d20=d20,trendrows=T,why=why,flips=flips,drivers=drivers,events=events,bull=nbull,bear=nbear,n=n))
TODAY=datetime.date.fromisoformat(META['asof_iso'][:10])
def evs(group,n=4):
    out=[]
    for x in EV[group]:
        d=datetime.date.fromisoformat(x['date']); dd=(d-TODAY).days
        if dd<0: continue
        lab='Today'+(' '+x['time'] if x.get('time') else '') if dd==0 else f"{d.strftime('%a')} {d.day} {d.strftime('%b')}"
        out.append((lab,x['name'],dd))
    return sorted(out,key=lambda z:z[2])[:n]
ev_us=evs('us'); ev_oil=evs('oil',5)
usI=lambda:[d_vix(),d_credit(),d_nfci(),d_claims()]
asset('gold','Gold','GC=F','Metals',[d_real(),d_dxy(),d_cot('gold','COT managed money'),D_('Inflation expectations',f"10y breakeven {be:.2f}%, {be5:+.2f} in 5 days",1 if be5>0.05 else (-1 if be5<-0.05 else 0),1,f'FRED T10YIE, {be_d}')],evs('us_macro',3))
gs=Y['GC=F']['last']/Y['SI=F']['last']; gs20=Y['GC=F']['d20']/Y['SI=F']['d20']
asset('silver','Silver','SI=F','Metals',[d_real(),d_dxy(),d_cot('silver','COT managed money'),D_('Gold/silver ratio',f"{gs:.1f} vs {gs20:.1f} 20 days ago",-1 if pct(gs,gs20)>5 else (1 if pct(gs,gs20)<-5 else 0),1,'Yahoo GC=F, SI=F'),d_vix()],evs('us_macro',3))
def oil(key,name,yk,ck):
    return [d_dxy(),d_cot('wti','COT managed money (WTI)'),D_('US crude stocks',f"{EIA['stocks_m']:.1f}m barrels, {EIA['week_change_m']:+.1f}m week, {abs(EIA['vs_last_year_m']):.1f}m {'below' if EIA['vs_last_year_m']<0 else 'above'} last year",1 if EIA['week_change_m']<-2 else (-1 if EIA['week_change_m']>2 else 0),1,f"EIA weekly report, week to {EIA['week_label']}"),d_vix(),d_credit()]
asset('wti','WTI crude','CL=F','Oil',oil('wti','WTI','CL=F','wti'),ev_oil)
asset('brent','Brent crude','BZ=F','Oil',oil('brent','Brent','BZ=F','wti'),ev_oil)
asset('sp','US500 (S&P 500)','^GSPC','US indices',usI()+[d_cot_info('sp','COT leveraged funds')],ev_us)
asset('ndx','USTEC (Nasdaq 100)','^NDX','US indices',usI()+[d_cot_info('ndx','COT leveraged funds')],ev_us)
asset('dow','US30 (Dow)','^DJI','US indices',usI()+[d_cot_info('dow','COT leveraged funds')],ev_us)
asset('rut','US2000 (Russell 2000)','^RUT','US indices',usI()+[D_('US 10y yield',f"{y10:.2f}%, {y10_5:+.2f} in 5 days",1 if y10_5<-0.10 else (-1 if y10_5>0.10 else 0),1,f'FRED DGS10, {y10_d}'),d_cot_info('rut','COT leveraged funds')],ev_us)
oilp=pct(Y['CL=F']['last'],Y['CL=F']['d20']); goldp=pct(Y['GC=F']['last'],Y['GC=F']['d20'])
asset('uk','UK100 (FTSE 100)','^FTSE','UK, Europe, Japan',[d_vix(),d_credit(),D_('Sterling',f"GBP/USD {gbp:.3f}, {gbp_p:+.1f}% in 20 days (weak helps)",1 if gbp_p<-1 else (-1 if gbp_p>1 else 0),1,f'FRED DEXUSUK, {gbp_d}'),D_('Oil (index is energy-heavy)',f"WTI {oilp:+.0f}% in 20 days",1 if oilp>5 else (-1 if oilp<-5 else 0),1,'Yahoo CL=F'),D_('Gold and miners',f"gold {goldp:+.0f}% in 20 days",1 if goldp>5 else (-1 if goldp<-5 else 0),1,'Yahoo GC=F')],evs('uk'))
eurd=[d_vix(),d_credit(),D_('Euro',f"EUR/USD {eur:.3f}, {eur_p:+.1f}% in 20 days (weak helps exporters)",1 if eur_p<-1 else (-1 if eur_p>1 else 0),1,f'FRED DEXUSEU, {eur_d}'),d_dxy()]
asset('de','DE40 (DAX)','^GDAXI','UK, Europe, Japan',eurd,evs('euro'))
asset('eu','EU50 (Euro Stoxx 50)','^STOXX50E','UK, Europe, Japan',eurd,evs('euro'))
asset('jp','JP225 (Nikkei)','^N225','UK, Europe, Japan',[d_vix(),d_credit(),D_('Yen',f"USD/JPY {jpy:.1f}, {jpy_p:+.1f}% in 20 days (weak yen helps)",1 if jpy_p>1 else (-1 if jpy_p<-1 else 0),1,f'FRED DEXJPUS, {jpy_d}'),d_nfci()],evs('us_macro',3))
asset('btc','Bitcoin','BTC-USD','Crypto',[d_vix(),d_credit(),d_dxy(),d_real(),d_nfci(),d_cot_info('btc','COT CME leveraged funds')],evs('us_macro',3))
regime=dict(vix=vix['last'],vix5=pct(vix['last'],vix['d5']),hy=hy,hy5=hy5,hy_d=hy_d,dxy=dxy['last'],dxy50=pct(dxy['last'],dxy['sma50']),y10=y10,y10_5=y10_5,real=real,real5=real5,nfci=nfci,ics=ics,be=be)
json.dump(dict(assets=A,regime=regime,asof=META['asof_label']),open(K+'out/board.json','w'),indent=1)
for a in A: print(f"{a['name']:24s} score {a['score']:+3d} {a['stance']:12s} {a['conviction']:6s} bull{a['bull']} bear{a['bear']} of {a['n']} | 5d {a['d5']:+.1f}% | {a['state']} | trend {a['trend']:+d}")
print(regime)
