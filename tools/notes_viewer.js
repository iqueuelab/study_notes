<script>
(() => {
 const topics=JSON.parse(document.getElementById('topic-data').textContent);
 const browse=document.getElementById('browse'),viewer=document.getElementById('topic-view');
 const title=document.getElementById('topic-title');let currentId='';
 function topicLink(t,label){const a=document.createElement('a');a.href='#topic='+encodeURIComponent(t.id);a.textContent=label;return a}
 function element(tag,text){const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node}
 function url(value,t){
  const resolved=new URL(value,(t.asset_base?new URL(t.asset_base,location.href):location.href));
  if(!['http:','https:','file:'].includes(resolved.protocol))return '#';
  const chapter=topics.find(c=>c.asset_base&&new URL('Quick%20Revision%20Notes.html',new URL(c.asset_base,location.href)).href===resolved.href);
  return chapter?'#topic='+encodeURIComponent(chapter.id):resolved.href;
 }
 function appendSpans(node,parts,t){for(const part of parts){let child;
  if(part.type==='text'){node.append(document.createTextNode(part.text));continue}
  const tags={strong:'strong',emphasis:'em',code:'code',link:'a'};
  if(!tags[part.type])throw Error('Unknown inline content '+part.type);
  child=element(tags[part.type],part.text);if(part.type==='link')child.href=url(part.url,t);node.append(child);
 }}
 function renderBlocks(blocks,t){const nodes=[];for(const b of blocks){let node;
  if(b.type==='heading'){if(b.level===1&&t.collection==='subject')continue;node=element('h'+Math.min(6,Math.max(2,b.level)));appendSpans(node,b.content,t)}
  else if(b.type==='paragraph'){node=element('p');appendSpans(node,b.content,t)}
  else if(b.type==='list'){node=element(b.ordered?'ol':'ul');for(const item of b.items){const li=element('li');appendSpans(li,item,t);node.append(li)}}
  else if(b.type==='table'){node=element('div');node.className='table';const table=element('table'),head=element('thead'),body=element('tbody');const makeRow=(cells,tag)=>{const row=element('tr');for(const cell of cells){const c=element(tag);if(tag==='th')c.scope='col';appendSpans(c,cell,t);row.append(c)}return row};head.append(makeRow(b.headers,'th'));for(const row of b.rows)body.append(makeRow(row,'td'));table.append(head,body);node.append(table)}
  else if(b.type==='diagram'){node=element('figure');const img=element('img');img.src=url(b.asset,t);img.alt=b.caption;node.append(img,element('figcaption',b.caption))}
  else if(b.type==='code'){node=element('pre');node.append(element('code',b.text))}
  else throw Error('Unknown note block '+b.type);
  nodes.push(node);
 }return nodes}
 function navigate(){
  const params=new URLSearchParams(location.hash.slice(1)),id=params.get('topic');
  const i=topics.findIndex(t=>t.id===id);
  if(i<0){browse.hidden=false;viewer.hidden=true;document.title=location.pathname.includes('Subject')?'Subject Notes':'Current Affairs';currentId='';return}
  const t=topics[i];browse.hidden=true;viewer.hidden=false;document.title=t.title;
  title.textContent=t.title;document.getElementById('topic-subject').textContent=t.subject;
  const content=document.getElementById('topic-content');
  content.replaceChildren(...renderBlocks(t.blocks,t));
  if(t.flow?.length){const flow=element('div');flow.className='flow';flow.setAttribute('aria-label','Recall flowchart');t.flow.forEach((step,j)=>{if(j){const arrow=element('div','↓');arrow.className='arrow';arrow.setAttribute('aria-hidden','true');flow.append(arrow)}const box=element('div',step);box.className='step';flow.append(box)});content.append(flow)}
  if(t.coverage){content.append(element('h2','PDF coverage'),element('p',Object.entries(t.coverage).sort().map(([d,ps])=>d+': pp. '+ps.join(', ')).join(' · ')))}
  document.getElementById('topic-editable').href=t.editable;
  for(const key of ['top','bottom']){
   const nav=document.getElementById('topic-nav-'+key);nav.replaceChildren();
   const all=document.createElement('a');all.href='#browse';all.textContent=t.collection==='subject'?'All chapters':'All topics';nav.append(all);
   const prev=i?topicLink(topics[i-1],'← Back'):Object.assign(document.createElement('a'),{href:'#browse',textContent:t.collection==='subject'?'← Back to all chapters':'← Back to all topics'});
   const next=i+1<topics.length?topicLink(topics[i+1],'Next →'):Object.assign(document.createElement('a'),{href:'#browse',textContent:t.collection==='subject'?'Next → All chapters':'Next → All topics'});
   prev.rel='prev';next.rel='next';nav.append(prev,next);
  }
  if(currentId!==id){window.scrollTo(0,0);title.focus({preventScroll:true})}currentId=id;
 }
 addEventListener('hashchange',navigate);navigate();
})();
</script>
