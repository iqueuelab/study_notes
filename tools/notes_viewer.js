<script>
(() => {
 const topics=JSON.parse(document.getElementById('topic-data').textContent);
 const browse=document.getElementById('browse'),viewer=document.getElementById('topic-view');
 const title=document.getElementById('topic-title');let currentId='';
 function topicLink(t,label){const a=document.createElement('a');a.href='#topic='+encodeURIComponent(t.id);a.textContent=label;return a}
 function navigate(){
  const params=new URLSearchParams(location.hash.slice(1)),id=params.get('topic');
  const i=topics.findIndex(t=>t.id===id);
  if(i<0){browse.hidden=false;viewer.hidden=true;document.title=location.pathname.includes('Subject')?'Subject Notes':'Current Affairs';currentId='';return}
  const t=topics[i];browse.hidden=true;viewer.hidden=false;document.title=t.title;
  title.textContent=t.title;document.getElementById('topic-subject').textContent=t.subject;
  const content=document.getElementById('topic-content');
  if(t.document){
   const frame=document.createElement('iframe');frame.id='chapter-frame';frame.title=t.title;
   frame.onload=()=>{const resize=()=>{frame.style.height=frame.contentDocument.documentElement.scrollHeight+'px'};resize();new ResizeObserver(resize).observe(frame.contentDocument.body);frame.contentDocument.querySelectorAll('img').forEach(im=>im.addEventListener('load',resize));};
   frame.srcdoc=t.document;content.replaceChildren(frame);
  }else content.innerHTML=t.content;
  document.getElementById('topic-editable').href=t.editable;
  for(const key of ['top','bottom']){
   const nav=document.getElementById('topic-nav-'+key);nav.replaceChildren();
   const all=document.createElement('a');all.href='#browse';all.textContent=t.document?'All chapters':'All topics';nav.append(all);
   const prev=i?topicLink(topics[i-1],'← Back'):Object.assign(document.createElement('a'),{href:'#browse',textContent:t.document?'← Back to all chapters':'← Back to all topics'});
   const next=i+1<topics.length?topicLink(topics[i+1],'Next →'):Object.assign(document.createElement('a'),{href:'#browse',textContent:t.document?'Next → All chapters':'Next → All topics'});
   prev.rel='prev';next.rel='next';nav.append(prev,next);
  }
  if(currentId!==id){window.scrollTo(0,0);title.focus({preventScroll:true})}currentId=id;
 }
 addEventListener('hashchange',navigate);navigate();
})();
</script>
