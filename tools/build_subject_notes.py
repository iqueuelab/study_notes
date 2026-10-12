"""Store chapter content in subject JSON files and build one offline chapter viewer."""
from pathlib import Path
from urllib.parse import quote,unquote
import json,re,html,os,hashlib
from notes_content import parse,markdown
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Subject Notes';OUT.mkdir(exist_ok=True)
def natural(s):return [int(x) if x.isdigit() else x.lower() for x in re.split(r'(\d+)',s)]
chapters=[];legacy=[]
for folder in sorted(ROOT.iterdir()):
 if not folder.is_dir() or folder.is_symlink() or folder.name.startswith('.') or folder.name in {'tools','Subject Notes','Current Affairs Notes','UPSC-PYQ'}:continue
 jp=folder/'Chapters.json';data=json.loads(jp.read_text()) if jp.exists() else {'subject':folder.name,'chapters':[]};by={c['id']:c for c in data['chapters']}
 for p in sorted(folder.rglob('Quick Revision Notes.html'),key=lambda p:natural(str(p))):
  doc=p.read_text();match=re.search(r'<h1[^>]*>(.*?)</h1>',doc,re.S);title=html.unescape(re.sub('<[^>]+>','',match[1])).strip() if match else p.parent.name
  rel=p.parent.relative_to(folder);id=folder.name+'/'+rel.as_posix();md=p.with_suffix('.md')
  by[id]={'id':id,'subject':folder.name,'unit':rel.parts[0] if len(rel.parts)>1 else '', 'chapter':p.parent.name,'title':title,'path':str(p.relative_to(ROOT)),'markdown':md.read_text() if md.exists() else '', 'document':doc}
  legacy.append(p)
 if not by:continue
 for c in by.values():
  mdpath=(ROOT/c['path']).with_suffix('.md')
  source=mdpath.read_text() if mdpath.exists() else c.get('markdown','')
  digest=hashlib.sha256(source.encode()).hexdigest()
  if 'blocks' not in c or c.get('editable_sha256')!=digest:c['blocks']=parse(source)
  assert c['blocks'],c['id']
  c['editable_sha256']=digest
  c.pop('document',None);c.pop('markdown',None)
 data['schema_version']=2
 data['chapters']=sorted(by.values(),key=lambda c:natural(c['path']));jp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');chapters.extend(data['chapters'])
assert len({c['id'] for c in chapters})==len(chapters)
routes={str((ROOT/c['path']).resolve()):'#topic='+quote(c['id'],safe='') for c in chapters}
def rewrite_links(doc,origin,for_frame=False):
 def replace(m):
  raw=html.unescape(m[2]);url,sep,fragment=raw.partition('#')
  if not url or re.match(r'[a-zA-Z]+:',url) or url.startswith('//'):return m[0]
  resolved=str((origin.parent/unquote(url)).resolve())
  if resolved in routes:
   return 'href='+m[1]+('index.html' if for_frame else quote(os.path.relpath(OUT/'index.html',origin.parent)))+routes[resolved]+m[1]
  # HTML summaries keep their own viewers; links in the embedded chapter open at top level.
  return m[0]
 return re.sub(r'href=([\"\'])(.*?)\1',replace,doc)
viewer=[]
for c in chapters:
 origin=ROOT/c['path']
 viewer.append({'id':c['id'],'title':c['title'],'subject':c['subject'],'collection':'subject','blocks':c['blocks'],'asset_base':'../'+quote(origin.parent.relative_to(ROOT).as_posix())+'/', 'editable':'../'+quote(origin.with_suffix('.md').relative_to(ROOT).as_posix())})
css='''*{box-sizing:border-box}body{margin:0;background:#f3f5f1;color:#182d2a;font:17px/1.65 system-ui,sans-serif;overflow-wrap:anywhere}main{max-width:950px;margin:auto;padding:24px}h1{font-size:clamp(28px,5vw,40px);line-height:1.2}a{color:#146c62}nav,.controls{display:flex;gap:10px;flex-wrap:wrap;margin:15px 0}nav a,button{padding:10px 14px;background:#e3eee7;border:0;border-radius:8px;font:inherit;text-decoration:none}input,select{font:inherit;padding:10px;width:100%;border:1px solid #bacbc0;border-radius:8px}details{border:1px solid #d7e2d9;background:white;border-radius:12px;margin:10px 0}summary{padding:14px;cursor:pointer;font-weight:650}.items{padding:0 16px 14px}.topic-row{padding:10px 0;border-top:1px solid #ddd}.tag{color:#526961;font-size:14px}article{background:white;border-radius:14px;padding:24px;margin:20px 0}li{margin:8px 0}table{border-collapse:collapse;width:100%;font-size:15px}td,th{padding:8px;border:1px solid #d7e2d9;text-align:left}.table{overflow-x:auto}figure{margin:24px auto;max-width:520px;text-align:center}figure img{width:100%;height:auto}figcaption{font-size:14px}h2{font-size:23px;border-bottom:2px solid #bdd4c5;padding-bottom:6px}.flow{display:grid;gap:8px;max-width:440px;margin:20px auto;text-align:center}.step{padding:12px;border:1px solid #8db3a4;border-radius:8px;background:#edf6ef} [hidden]{display:none!important}@media(max-width:480px){main{padding:14px}article{padding:14px}table{font-size:13px}}@media print{nav,.controls,#study-home,#browse{display:none!important}main{padding:0}article{padding:0}figure{max-width:90mm;break-inside:avoid}li,tr{break-inside:avoid}h2{break-after:avoid}}'''
body='<a id="study-home" href="../index.html">← Study home</a><div id="browse"><h1>Subject Notes</h1><input id="search" type="search" placeholder="Search chapters or facts" aria-label="Search chapters"><select id="subject"><option value="">All subjects</option>'+''.join('<option>'+html.escape(s)+'</option>' for s in sorted({c['subject'] for c in chapters}))+'</select>'
for subject in sorted({c['subject'] for c in chapters}):
 members=[c for c in chapters if c['subject']==subject];body+='<details class="subject-group"><summary>'+html.escape(subject)+'</summary><div class="items">'
 for unit in dict.fromkeys(c['unit'] for c in members):
  if unit:body+='<details class="unit"><summary>'+html.escape(unit)+'</summary><div class="items">'
  for c in members:
   if c['unit']!=unit:continue
   body+='<div class="topic-row" data-subject="'+html.escape(subject)+'" data-search="'+html.escape(c['title']+' '+c['chapter']+' '+markdown(c['blocks']),quote=True)+'"><a href="#topic='+quote(c['id'],safe='')+'">'+html.escape(c['chapter'])+'</a></div>'
  if unit:body+='</div></details>'
 body+='</div></details>'
body+='</div><section id="topic-view" hidden><nav id="topic-nav-top"></nav><p id="topic-subject" class="tag"></p><h1 id="topic-title" tabindex="-1"></h1><div class="controls"><button id="print-topic">Print / Save as PDF</button><a id="topic-editable">Editable notes</a></div><article id="topic-content"></article><nav id="topic-nav-bottom"></nav></section>'
body+='<script id="topic-data" type="application/json">'+json.dumps(viewer,ensure_ascii=False).replace('<','\\u003c')+'</script>'+(ROOT/'tools/notes_viewer.js').read_text()
body+='''<script>const q=document.querySelector('#search'),s=document.querySelector('#subject');function filter(){const active=!!q.value.trim()||!!s.value;document.querySelectorAll('.subject-group').forEach(g=>{let n=0;g.querySelectorAll('.topic-row').forEach(r=>{r.hidden=!(r.dataset.search.toLowerCase().includes(q.value.trim().toLowerCase())&&(!s.value||r.dataset.subject===s.value));if(!r.hidden)n++});g.hidden=!n;g.open=active&&n>0;g.querySelectorAll('.unit').forEach(u=>{u.hidden=![...u.querySelectorAll('.topic-row')].some(r=>!r.hidden);u.open=active&&!u.hidden})})}q.addEventListener('input',filter);s.addEventListener('change',filter);document.querySelector('#print-topic').onclick=()=>{window.print()};</script>'''
(OUT/'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Subject Notes</title><style>'+css+'</style></head><body><main>'+body+'</main></body></html>')
# Update common-summary links that previously pointed to per-chapter pages.
for folder in ROOT.iterdir():
 if folder.is_dir() and not folder.is_symlink() and not folder.name.startswith('.'):
  for p in folder.glob('*.html'):
   if p==OUT/'index.html':continue
   text=p.read_text();new=rewrite_links(text,p)
   if new!=text:p.write_text(new)
# Delete only migrated HTML files; Markdown, PDFs and diagram assets stay in place.
assert len(viewer)==len(chapters) and all(c['blocks'] for c in chapters)
for p in legacy:p.unlink()
print('Built one subject viewer;',len(chapters),'chapters preserved in subject JSON files')
