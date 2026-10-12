"""Structured note content: JSON blocks and inline spans, without HTML payloads."""
import re

def spans(text):
    result=[];pattern=r'\[([^\]]+)\]\(([^)]+)\)|\*\*(.+?)\*\*|`([^`]+)`|(?<!\*)\*([^*]+)\*(?!\*)'
    pos=0
    for m in re.finditer(pattern,text):
        if m.start()>pos:result.append({'type':'text','text':text[pos:m.start()]})
        if m[1] is not None:result.append({'type':'link','text':m[1],'url':m[2]})
        elif m[3] is not None:result.append({'type':'strong','text':m[3]})
        elif m[4] is not None:result.append({'type':'code','text':m[4]})
        else:result.append({'type':'emphasis','text':m[5]})
        pos=m.end()
    if pos<len(text):result.append({'type':'text','text':text[pos:]})
    return result

def parse(markdown):
    lines=markdown.splitlines();blocks=[];i=0
    while i<len(lines):
        line=lines[i]
        if not line.strip():i+=1;continue
        image=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line.strip())
        heading=re.match(r'^(#{1,6})\s+(.*)',line)
        if image:blocks.append({'type':'diagram','asset':image[2],'caption':image[1]});i+=1
        elif heading:blocks.append({'type':'heading','level':len(heading[1]),'content':spans(heading[2])});i+=1
        elif line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                cells=[c.strip().replace('\\|','|') for c in re.split(r'(?<!\\)\|',lines[i].strip().strip('|'))];i+=1
                if all(re.fullmatch(r':?-+:?',c) for c in cells):continue
                rows.append([spans(c) for c in cells])
            blocks.append({'type':'table','headers':rows[0],'rows':rows[1:]})
        elif line.startswith('- '):
            items=[]
            while i<len(lines) and lines[i].startswith('- '):items.append(spans(lines[i][2:]));i+=1
            blocks.append({'type':'list','ordered':False,'items':items})
        elif re.match(r'^\d+[.)] ',line):
            items=[]
            while i<len(lines) and re.match(r'^\d+[.)] ',lines[i]):items.append(spans(re.sub(r'^\d+[.)] ','',lines[i])));i+=1
            blocks.append({'type':'list','ordered':True,'items':items})
        elif line.startswith('```'):
            language=line[3:].strip();i+=1;code=[]
            while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
            i+=1;blocks.append({'type':'code','language':language,'text':'\n'.join(code)})
        else:blocks.append({'type':'paragraph','content':spans(line)});i+=1
    return blocks

def inline_markdown(parts):
    out=[]
    for p in parts:
        text=p['text'];kind=p['type']
        out.append('**'+text+'**' if kind=='strong' else '*'+text+'*' if kind=='emphasis' else '`'+text+'`' if kind=='code' else '['+text+']('+p['url']+')' if kind=='link' else text)
    return ''.join(out)

def markdown(blocks):
    out=[]
    for b in blocks:
        kind=b['type']
        if kind=='heading':out.append('#'*b['level']+' '+inline_markdown(b['content']))
        elif kind=='paragraph':out.append(inline_markdown(b['content']))
        elif kind=='list':out.append('\n'.join((str(i+1)+'. ' if b['ordered'] else '- ')+inline_markdown(x) for i,x in enumerate(b['items'])))
        elif kind=='table':
            row=lambda cells:'| '+' | '.join(inline_markdown(c).replace('|','\\|') for c in cells)+' |'
            out.append('\n'.join([row(b['headers']),'| '+' | '.join('---' for _ in b['headers'])+' |']+[row(r) for r in b['rows']]))
        elif kind=='diagram':out.append('!['+b['caption']+']('+b['asset']+')')
        elif kind=='code':out.append('```'+b.get('language','')+'\n'+b['text']+'\n```')
        else:raise ValueError('Unsupported block '+kind)
    return '\n\n'.join(out)

def text(blocks):
    # Use span values for semantic preservation checks.
    def walk(v):
        if isinstance(v,dict):
            for k,x in v.items():
                if k in {'text','caption'}:yield x
                elif isinstance(x,(dict,list)):yield from walk(x)
        elif isinstance(v,list):
            for x in v:yield from walk(x)
    return '\n'.join(walk(blocks))
