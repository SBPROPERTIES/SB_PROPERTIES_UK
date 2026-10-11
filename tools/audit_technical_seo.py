"""Read-only static SEO audit; emits JSON to stdout. No files or network changed."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, urljoin, unquote
from collections import Counter, defaultdict, deque
from itertools import combinations
import json, re, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://sbproperties.uk"

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.url = '/' + path.relative_to(ROOT).as_posix()
        self.url = self.url[:-10] if self.url.endswith('index.html') else self.url
        self.source = path.read_text(encoding='utf-8')
        self.ids = []; self.links = []; self.images = []; self.assets = []
        self.meta = {}; self.canonicals = []; self.schemas = []; self.h1 = 0
        self.title = ''; self.text = ''; self.stack = []; self.json_text = None
        self.schema_errors = []; self.lang = None
        self.feed(self.source)
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.stack.append(tag)
        if tag == 'html': self.lang = d.get('lang')
        if d.get('id'): self.ids.append(d['id'])
        if tag == 'a' and d.get('href'): self.links.append(d['href'])
        if tag == 'h1': self.h1 += 1
        if tag == 'img': self.images.append(d)
        if tag == 'meta': self.meta[d.get('name') or d.get('property')] = d.get('content')
        if tag == 'link' and d.get('rel') == 'canonical': self.canonicals.append(d.get('href'))
        if tag in ('img','script') and d.get('src'): self.assets.append(d['src'])
        if tag == 'link' and d.get('rel') == 'stylesheet': self.assets.append(d['href'])
        if tag == 'script' and d.get('type') == 'application/ld+json': self.json_text = ''
        if tag in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):
            self.stack.pop()
    def handle_endtag(self, tag):
        if tag == 'script' and self.json_text is not None:
            try:
                data = json.loads(self.json_text)
                self.schemas.extend(data.get('@graph',[data]) if isinstance(data,dict) else data)
            except ValueError as e: self.schema_errors.append(str(e))
            self.json_text = None
        if tag in self.stack:
            self.stack = self.stack[:len(self.stack)-1-self.stack[::-1].index(tag)]
    def handle_data(self, data):
        if self.json_text is not None: self.json_text += data
        if self.stack and self.stack[-1] == 'title': self.title += data
        if 'body' in self.stack and not any(x in self.stack for x in ('script','style','header','footer','nav')):
            self.text += ' '+data

pages = [Page(p) for p in sorted(ROOT.rglob('*.html')) if not any(x in p.parts for x in ('.git','research','tmp','dist'))]
by_url = {p.url:p for p in pages}
issues = defaultdict(list); graph = defaultdict(set); inbound = defaultdict(set)

def local_target(url, page):
    u = urlsplit(urljoin(BASE+page.url,url))
    if u.netloc not in ('sbproperties.uk','www.sbproperties.uk'): return None,u
    target = ROOT / unquote(u.path).lstrip('/')
    if target.is_dir(): target /= 'index.html'
    return target, u

for p in pages:
    if p.h1 != 1: issues['h1'].append([p.url,p.h1])
    if not p.lang: issues['missing_lang'].append(p.url)
    if not p.meta.get('viewport'): issues['missing_viewport'].append(p.url)
    if 'noindex' not in p.meta.get('robots','') and (len(p.canonicals)!=1 or p.canonicals[0] != BASE+p.url): issues['canonical'].append([p.url,p.canonicals])
    if not p.meta.get('description'): issues['missing_description'].append(p.url)
    if p.schema_errors: issues['invalid_jsonld'].append([p.url,p.schema_errors])
    if len(p.title)>65: issues['long_title'].append([p.url,len(p.title),p.title])
    if len(p.meta.get('description',''))>165: issues['long_description'].append([p.url,len(p.meta.get('description',''))])
    if any(n>1 for n in Counter(p.ids).values()): issues['duplicate_ids'].append(p.url)
    for link in p.links:
        target,u = local_target(link,p)
        if target is None: continue
        if not target.exists(): issues['broken_links'].append([p.url,link]); continue
        dest = '/' + target.relative_to(ROOT).as_posix()
        if dest.endswith('index.html'): dest=dest[:-10]
        if dest in by_url:
            graph[p.url].add(dest)
            if dest != p.url: inbound[dest].add(p.url)
            if u.fragment and unquote(u.fragment) not in by_url[dest].ids:
                issues['broken_fragments'].append([p.url,link])
    for asset in p.assets:
        target,u = local_target(asset,p)
        if target is not None and not target.exists(): issues['missing_assets'].append([p.url,asset])
    for im in p.images:
        if 'alt' not in im: issues['missing_alt'].append([p.url,im.get('src')])
        if not all(x in im for x in ('width','height')): issues['missing_image_dimensions'].append([p.url,im.get('src')])
    for s in p.schemas:
        for field in ('image','logo'):
            vals=s.get(field,[])
            if isinstance(vals,str): vals=[vals]
            elif isinstance(vals,dict): vals=[vals.get('url','')]
            for val in vals:
                if isinstance(val,str) and val:
                    target,u=local_target(val,p)
                    if target is not None and not target.exists(): issues['missing_schema_asset'].append([p.url,field,val])
    types=Counter(s.get('@type','') if isinstance(s.get('@type',''),str) else str(s.get('@type')) for s in p.schemas)
    if any(types[t]>1 for t in ('Organization','WebPage','WebSite','BreadcrumbList','Article','Service')):
        issues['duplicate_schema_entities'].append([p.url,dict(types)])

indexable=[p for p in pages if 'noindex' not in p.meta.get('robots','') and p.url!='/404.html']
for attr in ('title','description'):
    grouped=defaultdict(list)
    for p in indexable: grouped[p.title if attr=='title' else p.meta.get('description')].append(p.url)
    issues['duplicate_'+attr]=[v for v in grouped.values() if len(v)>1]
sitemap=ET.parse(ROOT/'sitemap.xml')
listed=[x.text for x in sitemap.findall('.//{*}loc')]
issues['sitemap_missing']=[p.url for p in indexable if BASE+p.url not in listed]
issues['sitemap_unknown']=[u for u in listed if urlsplit(u).path not in by_url]
depth={'/':0}; queue=deque(['/'])
while queue:
    url=queue.popleft()
    for child in graph[url]:
        if child not in depth: depth[child]=depth[url]+1; queue.append(child)
issues['orphans']=[p.url for p in indexable if p.url not in depth]
shingles={}
for p in indexable:
    if p.url.startswith('/sell-my-house-fast-'):
        words=re.findall(r'[a-z]+',p.text.lower())
        shingles[p.url]=set(tuple(words[i:i+5]) for i in range(len(words)-4))
similar=[]
for a,b in combinations(shingles,2):
    score=len(shingles[a]&shingles[b])/len(shingles[a]|shingles[b])
    if score>.8: similar.append([round(score,3),a,b])
assets=[]
for p in ROOT.rglob('*'):
    if p.is_file() and p.suffix.lower() in ('.jpg','.jpeg','.png','.webp','.css','.js') and not any(x in p.parts for x in ('.git','research','dist')):
        assets.append([p.stat().st_size,p.relative_to(ROOT).as_posix()])
page_assets=[]
for p in pages:
    local=[]
    for asset in set(p.assets):
        target,u=local_target(asset,p)
        if target and target.is_file():local.append(target.stat().st_size)
    page_assets.append([p.path.stat().st_size+sum(local),p.url])
result={'pages':len(pages),'indexable_pages':len(indexable),'sitemap_urls':len(listed),'depth_counts':dict(Counter(depth.values())),
    'issue_counts':{k:len(v) for k,v in issues.items()},'issues':dict(issues),
    'near_duplicate_location_pairs':sorted(similar,reverse=True)[:20],
    'largest_assets':sorted(assets,reverse=True)[:15],'largest_page_asset_totals':sorted(page_assets,reverse=True)[:12],
    'lowest_internal_inbound':sorted([[len(inbound[p.url]),p.url] for p in indexable])[:20]}
print(json.dumps(result,indent=2,ensure_ascii=False))
