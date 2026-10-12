"""Build the offline home page from completed subject and current-affairs notes."""
from pathlib import Path
from urllib.parse import quote
import html,json,re

ROOT=Path(__file__).resolve().parents[1]
chapter_lookup={}
for jp in ROOT.glob('*/Chapters.json'):
 for c in json.loads(jp.read_text())['chapters']:chapter_lookup[str(ROOT/c['path'])]=c
def esc(s):return html.escape(str(s),quote=True)
def href(p):
 if str(p) in chapter_lookup:return 'Subject%20Notes/index.html#topic='+quote(chapter_lookup[str(p)]['id'],safe='')
 return quote(p.relative_to(ROOT).as_posix())
def title(p):
 if str(p) in chapter_lookup:return chapter_lookup[str(p)]['title']
 m=re.search(r'<h1[^>]*>(.*?)</h1>',p.read_text(),re.S)
 return html.unescape(re.sub('<[^>]+>','',m[1])).strip() if m else p.stem

subjects=[]
for folder in sorted(ROOT.iterdir()):
 if not folder.is_dir() or folder.is_symlink() or folder.name.startswith('.') or folder.name in {'tools','Current Affairs Notes','UPSC-PYQ'}:continue
 chapters=sorted([Path(p) for p in chapter_lookup if Path(p).is_relative_to(folder)]) if (folder/'Chapters.json').exists() else sorted(folder.rglob('Quick Revision Notes.html'))
 if not chapters:continue
 groups={}
 for p in chapters:
  rel=p.relative_to(folder);unit=rel.parts[0] if len(rel.parts)>2 else ''
  groups.setdefault(unit,[]).append(p)
 resources=[p for p in sorted(folder.glob('*.html'))]
 subjects.append((folder,groups,resources,chapters))
ca=ROOT/'Current Affairs Notes';data=json.loads((ca/'Topics.json').read_text()) if (ca/'Topics.json').exists() else {'topics':[]}
queue=json.loads((ca/'Processing Log.json').read_text()) if (ca/'Processing Log.json').exists() else {'files':[]}
reviewed=[f for f in queue['files'] if f['status']=='reviewed']
CSS='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f4f6f2;color:#20332d;font:17px/1.55 system-ui,sans-serif}main{max-width:1040px;margin:auto;padding:28px 24px 60px}a{color:#14685c;text-underline-offset:3px;overflow-wrap:anywhere}h1{font-size:clamp(30px,6vw,46px);line-height:1.1;margin:14px 0}h2{font-size:24px;margin:30px 0 14px}h3{font-size:18px}.intro{color:#58675e;margin-top:0}.shortcuts{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:24px 0}.shortcut{display:block;text-decoration:none;color:inherit;padding:22px;border:1px solid #ccdbd0;border-radius:16px;background:white}.shortcut strong{display:block;font-size:22px;color:#14685c}.shortcut span{display:block;margin:8px 0;color:#56675e}.shortcut b{font-weight:600;font-size:15px}label{display:block;font-size:14px;font-weight:650;margin-bottom:6px}.filters{display:grid;grid-template-columns:2fr 1fr 1fr;gap:12px}input,select,button{font:inherit;border:1px solid #bacbc0;border-radius:9px;background:white;padding:11px;width:100%;color:inherit}button{cursor:pointer;width:auto}input:focus-visible,select:focus-visible,summary:focus-visible,a:focus-visible,button:focus-visible{outline:3px solid #247c67;outline-offset:3px}.actions{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0}.browse-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}details.group{background:white;border:1px solid #d7e2d9;border-radius:12px;align-self:start}details.group[open]{grid-column:1/-1}summary{cursor:pointer;padding:16px;font-weight:650;line-height:1.4}.count{font-size:14px;color:#5a6c60;font-weight:400;display:block;margin-top:3px}.content{padding:0 18px 12px}.row{display:block;border-top:1px solid #e1e8e2;padding:13px 0}.row a{font-weight:600}.row small{display:block;color:#617165;font-size:13px;margin-top:3px}.unit{border-top:1px solid #d7e2d9}.unit summary{padding-left:0}.unit .content{padding-left:8px}.resources{display:flex;gap:9px;flex-wrap:wrap;padding:10px 0}.resources a{font-size:14px;background:#eef4ed;border-radius:6px;padding:7px 10px}.section-head{display:flex;align-items:baseline;justify-content:space-between;gap:15px;flex-wrap:wrap}.section-head a{font-size:15px}.empty{padding:22px;background:white;border-radius:10px}.collection{margin-top:25px;border:1px solid #d7e2d9;border-radius:12px;background:#edf3eb}.collection>summary{font-size:22px}.collection>section{padding:0 16px 16px}.status{color:#617165;font-size:14px;margin-top:30px}[hidden]{display:none!important}@media(max-width:650px){main{padding:20px 16px}.shortcuts,.browse-grid,.filters{grid-template-columns:1fr}.shortcut{padding:18px}h2{font-size:22px}.content{padding:0 14px 10px}summary{padding:14px}.section-head{gap:0}}@page{size:A4;margin:16mm}@media print{body{background:white;font-size:11pt}main{padding:0;max-width:none}.filters,.actions,.shortcuts,.status{display:none}.browse-grid{display:block}details.group{border:none}summary{padding:8px 0}.content{padding:0}.row{padding:6px 0;break-inside:avoid}h2{break-after:avoid}a{color:inherit;text-decoration:none}.resources a{background:none;padding:0}}'''
count=sum(len(x[3]) for x in subjects)
body=f'''<header><h1>Study Notes</h1><p class="intro">Subject chapters and current affairs, together.</p></header>
<div class="shortcuts"><a class="shortcut" href="#subject-notes"><strong>Subject notes</strong><span>{count} chapters · {len(subjects)} subjects</span><b>Browse chapters ↓</b></a><a class="shortcut" href="Current%20Affairs%20Notes/index.html"><strong>Current affairs</strong><span>{len(data['topics'])} topics · {len(reviewed)} reviewed daily files</span><b>Browse by topic or date →</b></a></div>
<div class="filters"><div><label for="search">Find a chapter or topic</label><input id="search" type="search" placeholder="Search titles, subjects or dates"></div><div><label for="kind">Collection</label><select id="kind"><option value="">All notes</option><option value="subject">Subject notes</option><option value="current">Current affairs</option></select></div><div><label for="subject">Subject</label><select id="subject"><option value="">All subjects</option>'''+''.join(f'<option>{esc(s)}</option>' for s in sorted({f.name for f,_,_,_ in subjects}|{t['subject'] for t in data['topics']}))+'''</select></div></div><div class="actions"><button id="collapse" type="button">Collapse all</button><button id="clear" type="button">Clear filters</button><button type="button" onclick="window.print()">Print / Save as PDF</button></div>
<section id="subject-notes" data-section="subject"><div class="section-head"><h2>Subject notes</h2></div><div class="browse-grid">'''
for folder,units,resources,chapters in subjects:
 label=f'{len(chapters)} chapters'+(' · '+str(len(resources))+(' summary' if len(resources)==1 else ' summaries') if resources else '')
 body+=f'<details class="group" data-kind="subject" data-subject="{esc(folder.name)}"><summary>{esc(folder.name)}<span class="count" data-label="notes" data-default="{esc(label)}">{esc(label)}</span></summary><div class="content">'
 if resources:body+='<div class="resources">'+''.join(f'<div class="row" data-search="{esc(folder.name+" "+p.stem)}"><a href="{href(p)}">{esc(p.stem)}</a></div>' for p in resources)+'</div>'
 for unit,files in units.items():
  if unit:body+=f'<details class="unit"><summary>{esc(unit)}</summary><div class="content">'
  for p in files:
   label=p.parent.name
   body+=f'<div class="row" data-search="{esc(folder.name+" "+unit+" "+label+" "+title(p))}"><a href="{href(p)}">{esc(label)}</a></div>'
  if unit:body+='</div></details>'
 body+='</div></details>'
body+='</div></section><details class="collection" id="ca-collection"><summary>Current affairs topics<span class="count">Browse topics by subject</span></summary><section id="current-notes" data-section="current"><div class="section-head"><h2>Topics by subject</h2><a href="Current%20Affairs%20Notes/index.html">Browse year / month / date →</a></div><div class="browse-grid">'
for subject in sorted({t['subject'] for t in data['topics']}):
 topics=sorted([t for t in data['topics'] if t['subject']==subject],key=lambda t:t['title'])
 noun='topic' if len(topics)==1 else 'topics'
 body+=f'<details class="group" data-kind="current" data-subject="{esc(subject)}"><summary>{esc(subject)}<span class="count" data-label="topics" data-default="{len(topics)} {noun}">{len(topics)} {noun}</span></summary><div class="content">'
 for t in topics:
  dates=', '.join(sorted(t['coverage']));p=ca/'index.html'
  body+=f'<div class="row" data-search="{esc(subject+" "+t["title"]+" "+dates)}"><a href="{href(p)}#topic={quote(t["id"])}">{esc(t["title"])}</a><small>{esc(dates)}</small></div>'
 body+='</div></details>'
body+='</div></section></details><p id="empty" class="empty" role="status" hidden>No matching notes. Try another title or clear the filters.</p><p class="status">Current affairs coverage grows as daily files are reviewed.</p>'
body+=r'''<script>
const search=document.querySelector('#search'),kind=document.querySelector('#kind'),subject=document.querySelector('#subject');let filtering=false;
function words(s){return s.toLowerCase().normalize('NFKD').replace(/\p{M}/gu,'').split(/[^\p{L}\p{N}]+/u).filter(Boolean)}
function matches(text,query){const tokens=words(text);return words(query).every(q=>tokens.some(t=>t.startsWith(q)))}
function filter(){const query=search.value.trim().toLowerCase(),active=!!query||!!kind.value||!!subject.value;let total=0;document.querySelectorAll('.group').forEach(g=>{const eligible=(!kind.value||kind.value===g.dataset.kind)&&(!subject.value||subject.value===g.dataset.subject);let n=0;g.querySelectorAll('.row').forEach(r=>{r.hidden=!(eligible&&matches(r.dataset.search,query));if(!r.hidden)n++});g.hidden=!n;g.querySelector('.count').textContent=active?n+' matching '+(n===1?'note':'notes'):g.querySelector('.count').dataset.default;g.querySelectorAll('.unit').forEach(u=>{u.hidden=![...u.querySelectorAll('.row')].some(r=>!r.hidden);if(active)u.open=!u.hidden;else if(filtering)u.open=false});if(active)g.open=!!n;else if(filtering)g.open=false;total+=n});document.querySelectorAll('[data-section]').forEach(s=>s.hidden=![...s.querySelectorAll('.group')].some(g=>!g.hidden));const ca=document.querySelector('#ca-collection');ca.hidden=document.querySelector('#current-notes').hidden;if(active)ca.open=!ca.hidden;else if(filtering)ca.open=false;document.querySelector('#empty').hidden=!!total;filtering=active}
search.addEventListener('input',filter);kind.addEventListener('change',filter);subject.addEventListener('change',filter);document.querySelector('#clear').addEventListener('click',()=>{search.value='';kind.value='';subject.value='';filter()});document.querySelector('#collapse').addEventListener('click',()=>document.querySelectorAll('details').forEach(d=>d.open=false));let printState=[];addEventListener('beforeprint',()=>{printState=[...document.querySelectorAll('details')].map(d=>d.open);document.querySelectorAll('details').forEach(d=>d.open=true)});addEventListener('afterprint',()=>document.querySelectorAll('details').forEach((d,i)=>d.open=printState[i]));
</script>'''
(ROOT/'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Study Notes</title><style>'+CSS+'</style></head><body><main>'+body+'</main></body></html>')
# Add reversible home navigation without rewriting any note content or print styles.
files=[p for _,_,resources,chapters in subjects for p in resources+chapters if p.exists()]+list(ca.rglob('*.html'))
for p in files:
 text=p.read_text();relative='../'*len(p.relative_to(ROOT).parts[:-1])+'index.html'
 nav=f'<nav id="study-home" aria-label="Study home" style="max-width:1040px;margin:14px auto;padding:0 16px;font:15px system-ui"><a href="{relative}" style="color:#14685c">← Study home</a></nav>'
 text=re.sub(r'<nav id="study-home".*?</nav>','',text,flags=re.S)
 if '<body' in text:text=re.sub(r'(<body[^>]*>)',r'\1'+nav,text,count=1)
 else:text=text.replace('<main>',nav+'<main>',1)
 if 'style id="study-home-print"' not in text:text=text.replace('</style>','</style><style id="study-home-print">@media print{#study-home{display:none}}</style>',1)
 p.write_text(text)
print(f'Built study home: {count} chapters, {len(data["topics"])} current-affairs topics; linked {len(files)} note pages.')

# Keep chapter sequences and collection endpoints correct after every rebuild.
from notes_navigation import ensure_navigation
ensure_navigation(ROOT)
