"""Package only public pages and their referenced assets. Default: read-only audit.

Run with --build to write ./dist. This does not upload or deploy anything.
Research, search exports, migration scripts and logs are never selected.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, urljoin, unquote
import argparse, json, re, shutil, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'dist'
MANIFEST = ROOT / 'tmp' / 'public-build-manifest.json'
BASE = 'https://sbproperties.uk/'
ASSET_EXTENSIONS = {'.css','.js','.png','.jpg','.jpeg','.webp','.svg','.ico','.gif','.avif','.woff','.woff2','.ttf','.otf','.pdf','.mp4','.webm'}

class References(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.urls=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        for name in ('src','href','poster'):
            if d.get(name): self.urls.append(d[name])
        if d.get('srcset'):
            self.urls.extend(part.strip().split()[0] for part in d['srcset'].split(',') if part.strip())
        if tag=='meta' and d.get('property') in ('og:image','og:video'):
            self.urls.append(d.get('content',''))
        if tag=='meta' and d.get('name')=='twitter:image': self.urls.append(d.get('content',''))

def confined(relative):
    path=(ROOT/relative).resolve()
    if not path.is_relative_to(ROOT): raise ValueError(f'Path escapes project: {relative}')
    return path

def references(path):
    source=path.read_text(encoding='utf-8')
    refs=[]
    if path.suffix=='.html':
        parser=References(); parser.feed(source); refs.extend(parser.urls)
        refs.extend(re.findall(r'"(?:url|image|logo)"\s*:\s*"([^"]+)"',source))
    refs.extend(re.findall(r'url\(\s*[\'"]?([^\)\'"\s]+)',source))
    return refs

def inventory():
    selected=set()
    for node in ET.parse(ROOT/'sitemap.xml').findall('.//{*}loc'):
        url=urlsplit(node.text)
        if url.scheme!='https' or url.netloc!='sbproperties.uk':
            raise ValueError(f'Unexpected public URL: {node.text}')
        path=confined(unquote(url.path).lstrip('/'))
        if path.is_dir(): path/='index.html'
        if not path.is_file() or path.suffix!='.html': raise ValueError(f'Missing public page: {node.text}')
        selected.add(path)
    public_pages=set(selected)
    for name in ('404.html','robots.txt','sitemap.xml','llms.txt','CNAME','favicon.ico'):
        path=ROOT/name
        if path.is_file():selected.add(path)
    pending=[p for p in selected if p.suffix in ('.html','.css')]
    scanned=set()
    while pending:
        path=pending.pop()
        if path in scanned:continue
        scanned.add(path)
        relative=path.relative_to(ROOT).as_posix()
        for ref in references(path):
            url=urlsplit(urljoin(BASE+relative,ref))
            if url.netloc not in ('sbproperties.uk','www.sbproperties.uk') or url.scheme not in ('http','https'):continue
            target=confined(unquote(url.path).lstrip('/'))
            if target.is_dir():target/='index.html'
            if target.suffix=='.html':
                if target not in public_pages and target!=ROOT/'404.html':
                    raise ValueError(f'Public page links outside sitemap: {relative}: {ref}')
                continue
            if target.suffix.lower() not in ASSET_EXTENSIONS:continue
            if not target.is_file():raise ValueError(f'Missing asset: {relative}: {ref}')
            if target not in selected:
                selected.add(target)
                if target.suffix=='.css':pending.append(target)
    return sorted(selected)

def build(selected):
    # Resolve/check every output before writing or removing a previously generated file.
    out=OUTPUT.resolve()
    if out.parent!=ROOT or out.name!='dist':raise ValueError('Unexpected build directory')
    old=[]
    if MANIFEST.exists():old=json.loads(MANIFEST.read_text(encoding='utf-8'))['files']
    if out.exists() and not old and any(out.iterdir()):
        raise ValueError('dist is not owned by this build; preserve or move it before building')
    if out.exists():
        existing={p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file() or p.is_symlink()}
        unexpected=existing-set(old)
        if unexpected:
            raise ValueError('Unexpected files in dist; inspect and remove them before publishing: '+', '.join(sorted(unexpected)))
    wanted={p.relative_to(ROOT).as_posix() for p in selected}|{'.nojekyll'}
    for relative in old:
        target=(out/relative).resolve()
        if not target.is_relative_to(out):raise ValueError('Invalid prior build manifest')
        if relative not in wanted and target.is_file():target.unlink()
    for source in selected:
        target=(out/source.relative_to(ROOT)).resolve()
        if not target.is_relative_to(out):raise ValueError('Invalid output path')
        target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target)
    (out/'.nojekyll').write_text('',encoding='utf-8')
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    MANIFEST.write_text(json.dumps({'files':sorted(wanted)},indent=2)+'\n',encoding='utf-8')
    return str(out)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',action='store_true',help='Write confined public files to ./dist (no deployment)')
    args=parser.parse_args(); selected=inventory()
    result={'mode':'build' if args.build else 'check','files':len(selected),'bytes':sum(p.stat().st_size for p in selected),
            'pages':sum(p.suffix=='.html' for p in selected),
            'excluded':'Search-Data, research, tmp, source scripts, logs and unreferenced assets'}
    if args.build:result['output']=build(selected)
    print(json.dumps(result,indent=2))
