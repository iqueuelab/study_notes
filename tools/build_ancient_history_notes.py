"""Render editable Ancient & Medieval History chapter Markdown to responsive HTML."""
from pathlib import Path
import ast,html,re
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]
SUBJECT=ROOT/'Ancient & Medieval History'
# Reuse the notes renderer without executing the current-affairs build.
tree=ast.parse((ROOT/'tools/build_current_affairs_notes.py').read_text())
namespace={'html':html,'re':re}
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'inline','render'}]
exec(compile(ast.Module(body=functions,type_ignores=[]),'notes_renderer','exec'),namespace)
template=(SUBJECT/'01. Pre-Historic India/Quick Revision Notes.html').read_text()
css=re.search(r'<style>(.*?)</style>',template,re.S)[1]
# Three-column tables expose their header labels when stacked on phones.
css+='@media(max-width:600px){td[data-label]:before{content:attr(data-label) ": ";font-weight:700}}'
for chapter in sorted(SUBJECT.iterdir()):
 source=chapter/'Quick Revision Notes.md'
 if not chapter.is_dir() or not source.exists() or chapter.name.startswith('01.'):continue
 text=source.read_text();title=text.splitlines()[0].lstrip('# ').strip();diagrams=[]
 def diagram(match):
  fields=[x.strip() for x in match[1].split('|')];index=len(diagrams)
  figure='<figure class="diagram"><figcaption>'+html.escape(fields[0])+'</figcaption><ol>'+''.join('<li>'+html.escape(x)+'</li>' for x in fields[1:])+'</ol></figure>'
  diagrams.append(figure);return 'DIAGRAMPLACEHOLDER'+str(index)
 text=re.sub(r'<!-- flow:(.*?) -->',diagram,text)
 body=namespace['render'](text)
 for i,figure in enumerate(diagrams):body=body.replace('<p>DIAGRAMPLACEHOLDER'+str(i)+'</p>',figure)
 def labelled_table(match):
  table=match[0];headers=re.findall(r'<th>(.*?)</th>',table,re.S)
  if len(headers)<3:return table
  def row(m):
   cells=re.findall(r'<td>(.*?)</td>',m[0],re.S)
   if not cells:return m[0]
   return '<tr>'+''.join('<td'+(' data-label="'+html.escape(re.sub('<.*?>','',headers[i]),quote=True)+'"' if i else '')+'>'+cell+'</td>' for i,cell in enumerate(cells))+'</tr>'
  return re.sub(r'<tr>.*?</tr>',row,table,flags=re.S)
 body=re.sub(r'<table>.*?</table>',labelled_table,body,flags=re.S)
 pdf='Harappan Civilisation.pdf' if chapter.name.startswith('02.') else 'The Vedic Age.pdf'
 controls='<div class="controls"><button onclick="window.print()">Print / Save as PDF</button><a href="Quick%20Revision%20Notes.md">Editable notes</a><a href="'+quote(pdf)+'">Download PDF</a><a href="../Chronology.html">History timeline</a></div>'
 page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>'+css+'</style></head><body><main>'+controls+body+'</main></body></html>'
 (chapter/'Quick Revision Notes.html').write_text(page)
 print('Rendered',chapter.name)
