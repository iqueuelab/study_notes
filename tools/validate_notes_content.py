"""Validate structured JSON note content and its local diagram references."""
import json,re
from pathlib import Path
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1]
BLOCKS={'heading','paragraph','list','table','diagram','code'}
SPANS={'text','strong','emphasis','code','link'}
def check_spans(parts):
    assert isinstance(parts,list)
    for p in parts:
        assert p['type'] in SPANS and isinstance(p['text'],str)
        assert not re.search(r'</?[A-Za-z][^>]*>',p['text']), 'HTML in note text'
        if p['type']=='link':assert isinstance(p['url'],str)
def check(blocks,base):
    assert blocks
    for b in blocks:
        assert b['type'] in BLOCKS
        kind=b['type']
        if kind in {'heading','paragraph'}:check_spans(b['content'])
        elif kind=='list':
            assert isinstance(b['ordered'],bool)
            for item in b['items']:check_spans(item)
        elif kind=='table':
            for cell in b['headers']:check_spans(cell)
            for row in b['rows']:
                assert len(row)==len(b['headers']), 'Unequal table row'
                for cell in row:check_spans(cell)
        elif kind=='diagram':
            assert (base/unquote(b['asset'])).is_file(),b['asset']
            assert isinstance(b['caption'],str)
        elif kind=='code':assert isinstance(b['text'],str)
    return len(blocks)
count=0
for p in ROOT.glob('*/Chapters.json'):
    data=json.loads(p.read_text());assert data['schema_version']==2
    for c in data['chapters']:
        assert not {'document','markdown','html'}&c.keys()
        check(c['blocks'],(ROOT/c['path']).parent);count+=1
p=ROOT/'Current Affairs Notes/Topics.json';data=json.loads(p.read_text());assert data['schema_version']==2
for t in data['topics']:
    assert not {'document','markdown','html'}&t.keys()
    check(t['blocks'],p.parent/t['subject']);count+=1
print(f'{count} entries validated: structured blocks, tables, text and diagram assets; no HTML payloads.')
