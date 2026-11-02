"""Render Anthropology notes using each page's existing manually edited styles."""
from pathlib import Path
from urllib.parse import quote
import ast,html,re,sys
root=Path(__file__).resolve().parents[1]
subject=root/'Anthropology'
pdfs={'01':'Meaning Scope and Development.pdf','02':'Relationship with Other Disciplines.pdf','03':'Main Branches of Anthropology.pdf','04':'Human Evolution and Emergence of Man.pdf'}
def render_chapter(chapter,pdf):
 # Keep the established chapter layout. Subsequent rebuilds inherit this page's own styles.
 old=chapter/'Quick Revision Notes.html'
 reference=old if old.exists() else subject/'03. Main Branches of Anthropology/Quick Revision Notes.html'
 css=re.search(r'<style>(.*?)</style>',reference.read_text(),re.S)[1].replace('tr:first-child{display:none}','thead{display:none}')
 if 'td[data-label]:before' not in css:css+='@media(max-width:600px){td[data-label]:before{content:attr(data-label) ": ";font-weight:700}}'
 tree=ast.parse((root/'tools/build_current_affairs_notes.py').read_text());ns={'html':html,'re':re}
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'inline','render'}],type_ignores=[]),'renderer','exec'),ns)
 if '.branches ol' not in css:css+=' .branches ol{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.branches li{margin:0}.branches li+li:before{content:none}.branches{max-width:600px}@media(max-width:600px){.branches ol{grid-template-columns:1fr}}@media print{.branches{max-width:160mm}}'
 text=(chapter/'Quick Revision Notes.md').read_text();figures=[];title=text.splitlines()[0].lstrip('# ').strip()
 def flow(m):
  fields=[x.strip() for x in m[1].split('|')];n=len(figures)
  figures.append('<figure class="'+('diagram branches' if fields[0]=='One discipline, four connected fields' else 'diagram')+'"><figcaption>'+html.escape(fields[0])+'</figcaption><ol>'+''.join('<li>'+html.escape(x)+'</li>' for x in fields[1:])+'</ol></figure>');return f'DIAGRAMPLACEHOLDER{n}'
 body=ns['render'](re.sub(r'<!-- flow:(.*?) -->',flow,text))
 body=re.sub(r'(<h3>\d{4}.*?)(?=<h[23]>|$)',r'<section class="answer-block">\1</section>',body,flags=re.S)
 if '.answer-block{' not in css:css+=' .answer-block{break-inside:avoid}'
 for n,f in enumerate(figures):body=body.replace(f'<p>DIAGRAMPLACEHOLDER{n}</p>',f)
 def table(m):
  s=m[0];heads=re.findall(r'<th>(.*?)</th>',s,re.S)
  def row(m):
   cells=re.findall(r'<td>(.*?)</td>',m[0],re.S)
   return '<tr>'+''.join('<td'+(' data-label="'+html.escape(html.unescape(re.sub('<.*?>','',heads[i])),quote=True)+'"' if i else '')+'>'+v+'</td>' for i,v in enumerate(cells))+'</tr>' if cells else m[0]
  s=re.sub(r'<tr>.*?</tr>',row,s,flags=re.S)
  return re.sub(r'<table>(<tr>.*?</tr>)(.*?)</table>',r'<table><thead>\1</thead><tbody>\2</tbody></table>',s,flags=re.S)
 body=re.sub(r'<table>.*?</table>',table,body,flags=re.S)
 controls='<div class="controls"><button onclick="window.print()">Print / Save as PDF</button><a href="Quick%20Revision%20Notes.md">Editable notes</a><a href="'+quote(pdf)+'">Download PDF</a></div>'
 old.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>'+css+'</style></head><body><main>'+controls+body+'</main></body></html>')
 print('Rendered',chapter.name)

for chapter in sorted(subject.iterdir()):
 if len(sys.argv)>1 and not chapter.name.startswith(sys.argv[1].zfill(2)+'.'):continue
 if chapter.is_dir() and (chapter/'Quick Revision Notes.md').exists():render_chapter(chapter,pdfs.get(chapter.name[:2],chapter.name+'.pdf'))
