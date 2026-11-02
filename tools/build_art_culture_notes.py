"""Render Art and Culture chapter 1, preserving its manually edited CSS."""
from pathlib import Path
import ast,html,re
root=Path(__file__).resolve().parents[1]
subject=root/'Indian Art & Culture'
chapter=subject/'01. Prehistoric Cultures in India'
# Keep the established chapter layout. Subsequent rebuilds inherit this page's own styles.
old=chapter/'Quick Revision Notes.html'
reference=old if old.exists() else root/'Ancient & Medieval History/01. Pre-Historic India/Quick Revision Notes.html'
css=re.search(r'<style>(.*?)</style>',reference.read_text(),re.S)[1].replace('tr:first-child{display:none}','thead{display:none}')
if 'td[data-label]:before' not in css:css+='@media(max-width:600px){td[data-label]:before{content:attr(data-label) ": ";font-weight:700}}'
tree=ast.parse((root/'tools/build_current_affairs_notes.py').read_text());ns={'html':html,'re':re}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'inline','render'}],type_ignores=[]),'renderer','exec'),ns)
text=(chapter/'Quick Revision Notes.md').read_text();figures=[]
def flow(m):
 fields=[x.strip() for x in m[1].split('|')];n=len(figures)
 figures.append('<figure class="diagram"><figcaption>'+html.escape(fields[0])+'</figcaption><ol>'+''.join('<li>'+html.escape(x)+'</li>' for x in fields[1:])+'</ol></figure>');return f'DIAGRAMPLACEHOLDER{n}'
body=ns['render'](re.sub(r'<!-- flow:(.*?) -->',flow,text))
for n,f in enumerate(figures):body=body.replace(f'<p>DIAGRAMPLACEHOLDER{n}</p>',f)
def table(m):
 s=m[0];heads=re.findall(r'<th>(.*?)</th>',s,re.S)
 def row(m):
  cells=re.findall(r'<td>(.*?)</td>',m[0],re.S)
  return '<tr>'+''.join('<td'+(' data-label="'+html.escape(re.sub('<.*?>','',heads[i]),quote=True)+'"' if i else '')+'>'+v+'</td>' for i,v in enumerate(cells))+'</tr>' if cells else m[0]
 s=re.sub(r'<tr>.*?</tr>',row,s,flags=re.S)
 return re.sub(r'<table>(<tr>.*?</tr>)(.*?)</table>',r'<table><thead>\1</thead><tbody>\2</tbody></table>',s,flags=re.S)
body=re.sub(r'<table>.*?</table>',table,body,flags=re.S)
controls='<div class="controls"><button onclick="window.print()">Print / Save as PDF</button><a href="Quick%20Revision%20Notes.md">Editable notes</a><a href="Prehistoric%20Cultures%20in%20India.pdf">Download PDF</a><a href="../Chronology.html">History timeline</a></div>'
old.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Prehistoric Cultures in India</title><style>'+css+'</style></head><body><main>'+controls+body+'</main></body></html>')

print('Rendered',chapter.name)
