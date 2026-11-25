# Builds news.json from public RSS feeds: headline, source and link only.
import urllib.request, json, os, re, email.utils, datetime, html
import xml.etree.ElementTree as ET
K=os.path.dirname(os.path.abspath(__file__))+'/'
UA={'User-Agent':'mac-and-cheese/1.0 (+https://aethernode.github.io/mac-and-cheese/)'}
FEEDS=[('CNBC','https://www.cnbc.com/id/20910258/device/rss/rss.html'),('CNBC','https://www.cnbc.com/id/10000664/device/rss/rss.html'),
('BBC News','https://feeds.bbci.co.uk/news/business/rss.xml'),('MarketWatch','https://feeds.content.dowjones.io/public/rss/mw_topstories'),
('FXStreet','https://www.fxstreet.com/rss/news')]
RULES=[(r'\b(fed|fomc|powell|warsh|rate (hike|cut|increase|decision))\b','United States · Fed',['US indices','USD','Gold']),
(r'\b(inflation|cpi|pce)\b','Inflation',['Gold','US indices','Yields']),
(r'\b(payrolls|jobs report|jobless claims|unemployment rate)\b','Jobs',['US indices','USD']),
(r'\b(gdp|recession)\b','Growth',['US indices','USD']),
(r'\b(treasury yields?|treasuries|bond yields?|10-year)\b','Rates',['Yields','Gold','USD']),
(r'\b(oil|crude|opec|brent|wti)\b','Commodities · Oil',['WTI','Brent']),
(r'\b(gold|silver)\b','Commodities · Metals',['Gold','Silver']),
(r'\b(bank of england|boe|bailey|sterling|ftse)\b','United Kingdom',['UK100','GBP']),
(r'\b(ecb|lagarde|eurozone|dax)\b','Europe',['DE40','EU50']),
(r'\b(yen|boj|bank of japan|nikkei)\b','Japan',['JP225','USD']),
(r'\b(bitcoin|crypto)\b','Crypto',['Bitcoin']),
(r'\b(tariffs?|trade war|trade deal)\b','Trade',['USD','US indices']),
(r'\b(dollar|currenc(y|ies)|forex)\b','Currencies',['USD']),
(r'\b(stocks?|wall street|nasdaq|s&p 500|dow|stock market|sell-off|selloff)\b','Equities',['US500','USTEC','US30'])]
items=[]
now=datetime.datetime.now(datetime.timezone.utc)
for src,url in FEEDS:
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30) as r: root=ET.fromstring(r.read())
    except Exception as e:
        print('feed failed',src,e); continue
    for it in root.iter('item'):
        t=html.unescape((it.findtext('title') or '').strip()); link=(it.findtext('link') or '').strip(); pd=it.findtext('pubDate')
        if not t or not link.startswith('http'): continue
        try: dt=email.utils.parsedate_to_datetime(pd)
        except Exception: continue
        if dt.tzinfo is None: dt=dt.replace(tzinfo=datetime.timezone.utc)
        if now-dt>datetime.timedelta(hours=36): continue
        low=t.lower()
        for rx,tag,aff in RULES:
            if re.search(rx,low):
                items.append(dict(tag=tag,headline=t,summary='',source=src,url=link,affects=aff,ts=dt.timestamp())); break
seen=set(); out=[]
for x in sorted(items,key=lambda z:-z['ts']):
    k=re.sub(r'\W+','',x['headline'].lower())[:50]
    if k in seen: continue
    seen.add(k); x.pop('ts'); out.append(x)
    if len(out)==8: break
if len(out)>=3: json.dump(out,open(K+'news.json','w'),indent=1); print(len(out),'stories')
else: print('too few stories; keeping previous news.json')
