"""Static checks for preserved delivery, links, schema, labels and honest dates."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
import json,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
errors=[];forms=0;pages=0
class Inspect(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.ids=[];self.links=[];self.labels=[];self.inputs=[];self.form_actions=[];self.h1=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:self.ids.append(d['id'])
        if tag=='h1':self.h1+=1
        if tag=='a' and 'href' in d:self.links.append(d['href'])
        if tag in ('img','script','link'):
            if d.get('src') or d.get('href'):self.links.append(d.get('src') or d.get('href'))
        if tag=='label' and 'for' in d:self.labels.append(d['for'])
        if tag in ('input','textarea','select') and d.get('type')!='hidden':self.inputs.append(d)
        if tag=='form':self.form_actions.append(d.get('action'))
for path in ROOT.rglob('*.html'):
    if any(part in ('dist','tmp','research','.git') for part in path.relative_to(ROOT).parts):continue
    s=path.read_text(encoding='utf-8');p=Inspect();p.feed(s);pages+=1
    for key,n in Counter(p.ids).items():
        if n>1:errors.append(f'{path.relative_to(ROOT)}: duplicate id {key}')
    if p.h1!=1:errors.append(f'{path.relative_to(ROOT)}: expected one h1, got {p.h1}')
    for link in p.links:
        u=urlsplit(link)
        if u.scheme or u.netloc or not u.path:continue
        target=ROOT/unquote(u.path).lstrip('/') if u.path.startswith('/') else path.parent/unquote(u.path)
        if not target.exists():errors.append(f'{path.relative_to(ROOT)}: missing {link}')
    for inp in p.inputs:
        if inp.get('id') not in p.labels and not inp.get('aria-label'):errors.append(f'{path.relative_to(ROOT)}: unlabelled {inp.get("id")}')
    forms+=len(p.form_actions)
    if any(a!='https://formspree.io/f/mwpyrrke' for a in p.form_actions):errors.append(f'{path}: unexpected form destination')
    for raw in re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>',s,re.S):
        try:json.loads(raw)
        except json.JSONDecodeError as e:errors.append(f'{path}: invalid schema {e}')
    if 'dateStr' in s:errors.append(f'{path}: artificial date script remains')
    relative=path.relative_to(ROOT).as_posix()
    old=subprocess.run(['git','show',f'HEAD:{relative}'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8').stdout
    # Existing secondary webhook handler must be preserved verbatim.
    for script in re.findall(r'<script\b[^>]*>.*?</script>',old,re.S):
        if 'sb-property-lead' in script and script not in s:errors.append(f'{relative}: existing webhook changed')
print(f'Checked {pages} HTML pages and {forms} form destinations.')
if errors:
    print('\n'.join(errors));raise SystemExit(1)
print('PASS: local targets, unique IDs, labels, JSON-LD, stable dates and original webhook handlers.')
