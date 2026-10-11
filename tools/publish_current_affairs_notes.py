"""Copy only authored notes and review metadata into the Git checkout.

Downloaded PDFs, images, external-drive metadata and originals are never copied.
"""
import argparse,hashlib,json
from pathlib import Path

repo=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,default=repo/'Current Affairs'/'Notes')
args=parser.parse_args()
source=args.source.resolve();target=repo/'Current Affairs Notes'
data=json.loads((source/'Topics.json').read_text())
queue=json.loads((source/'Processing Log.json').read_text())
ids=[t['id'] for t in data['topics']]
assert len(ids)==len(set(ids)), 'Duplicate topic IDs'
paths={Path(x) for x in ['index.html','index.md','Topics.json','Processing Log.json','PYQ Review.json']}
for t in data['topics']:
 for suffix in ['.md','.html']:paths.add(Path(t['subject'])/(t['id']+suffix))
 for stage in ['Prelim','Mains']:paths.add(Path(t['subject'])/f'PYQ-{stage}.json')
for path in paths:
 assert path.suffix in {'.md','.html','.json'} and not path.is_absolute() and '..' not in path.parts
 assert (source/path).is_file() and not (source/path).is_symlink()
 if path.name.startswith('PYQ-'):
  doc=json.loads((source/path).read_text());seen=set()
  for question in doc['questions']:
   assert isinstance(question['year'],int) and question['question'] and question['chapter']
   assert not {'source','sources','answer_source'}&question.keys()
   key=(question['year'],question['question']);assert key not in seen;seen.add(key)
# Read/write content only: avoids importing AppleDouble/resource-fork metadata.
for path in sorted(paths):
 content=(source/path).read_bytes();out=target/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(content)
 assert hashlib.sha256(out.read_bytes()).digest()==hashlib.sha256(content).digest()
print(f'Published {len(paths)} notes/metadata files; {len(data["topics"])} topics; {sum(f["status"]=="reviewed" for f in queue["files"])} reviewed daily PDFs. No downloaded files copied.')
