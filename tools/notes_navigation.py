"""Keep completed HTML notes connected without changing their subject content."""
from pathlib import Path
from urllib.parse import quote
import html,json,os,re

STYLE='''<style id="notes-sequence-style">.sequence-nav{display:flex;flex-wrap:wrap;gap:10px;max-width:1040px;margin:18px auto;padding:0 16px;align-items:center}.sequence-nav a{display:inline-block;background:#e3eee7;color:#14685c;padding:9px 14px;border-radius:8px;text-decoration:none;font:15px/1.5 system-ui,sans-serif}.sequence-nav a:focus-visible{outline:3px solid #14685c;outline-offset:3px}@media print{.sequence-nav{display:none!important}}</style>'''

def relative(source,target):
    return quote(os.path.relpath(target,source.parent).replace(os.sep,'/'))

def natural(path):
    return tuple(int(x) if x.isdigit() else x.casefold() for x in re.split(r'(\d+)',path.as_posix()))

def title(path):
    match=re.search(r'<h1[^>]*>(.*?)</h1>',path.read_text(),re.S)
    return html.unescape(re.sub('<[^>]+>','',match[1])).strip() if match else path.stem

def navigation(page,back,next_page,back_label='← Back',next_label='Next →',position='top'):
    return f'<nav class="sequence-nav" data-position="{position}" aria-label="Notes sequence"><a rel="prev" href="{relative(page,back)}" title="{html.escape(title(back),quote=True)}">{back_label}</a><a rel="next" href="{relative(page,next_page)}" title="{html.escape(title(next_page),quote=True)}">{next_label}</a></nav>'

def connect(page,back,next_page,home):
    text=page.read_text()
    text=re.sub(r'<nav\b[^>]*class="sequence-nav"[^>]*>.*?</nav>','',text,flags=re.S)
    # Replace older chapter arrows only; keep home, filters and other controls.
    text=re.sub(r'<a\b[^>]*>\s*(?:←\s*)?(?:Previous|Next|Back)\s+chapter\s*(?:→)?\s*</a>','',text,flags=re.I)
    text=re.sub(r'<nav\b[^>]*>\s*</nav>','',text)
    back_label='← Back to study home' if back==home else '← Back'
    next_label='Next → Study home' if next_page==home else 'Next →'
    top=navigation(page,back,next_page,back_label,next_label)
    bottom=navigation(page,back,next_page,back_label,next_label,'bottom')
    if 'id="notes-sequence-style"' not in text:
        if '</head>' in text:text=text.replace('</head>',STYLE+'</head>',1)
        else:text=text.replace('<main>',STYLE+'<main>',1)
    if re.search(r'<body\b',text):
        text=re.sub(r'(<body[^>]*>)',lambda m:m[1]+top,text,count=1)
        text=text.replace('</body>',bottom+'</body>',1)
    else:
        text=text.replace('<main>', '<main>'+top,1)
        text=text.replace('</main>',bottom+'</main>',1)
    if text!=page.read_text():page.write_text(text)

def ensure_navigation(root):
    root=Path(root);home=root/'index.html';count=0
    for folder in sorted(root.iterdir()):
        if not folder.is_dir() or folder.is_symlink() or folder.name.startswith('.') or folder.name in {'tools','Current Affairs Notes','UPSC-PYQ'}:continue
        chapters=sorted(folder.rglob('Quick Revision Notes.html'),key=natural)
        if not chapters:continue
        summaries=sorted((p for p in folder.glob('*.html') if not p.name.startswith('._')),key=natural)
        sequence=chapters+summaries
        for i,page in enumerate(sequence):
            connect(page,sequence[i-1] if i else home,sequence[i+1] if i+1<len(sequence) else home,home);count+=1
    ca=root/'Current Affairs Notes';data_path=ca/'Topics.json'
    if data_path.exists():
        data=json.loads(data_path.read_text());topics=sorted(data['topics'],key=lambda t:(t['subject'],t['title']))
        pages=[ca/t['subject']/(t['id']+'.html') for t in topics]
        if pages:
            index=ca/'index.html'
            connect(index,home,pages[0],home);count+=1
            # Existing topic chains are generated in subject/title order.
            for page,label in [(pages[0],'← Back to all topics'),(pages[-1],'Next → All topics')]:
                text=page.read_text()
                if label not in text:
                    anchor=f'<a href="../index.html">{label}</a>'
                    text=re.sub(r'(<nav>)(.*?)(</nav>)',lambda m:m[1]+m[2]+anchor+m[3],text,flags=re.S)
                    page.write_text(text)
                count+=1
    return count

if __name__=='__main__':
    print('Connected navigation on',ensure_navigation(Path(__file__).resolve().parents[1]),'pages.')
