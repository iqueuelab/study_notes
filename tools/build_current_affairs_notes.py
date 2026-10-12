"""Build offline, responsive topic notes from manually reviewed Topics.json."""
import json,re,html,hashlib,os,calendar
from pathlib import Path
from urllib.parse import quote
ROOT=Path(os.environ.get('CA_SOURCE_ROOT',str(Path(__file__).resolve().parents[1]/'Current Affairs'))).resolve()
OUT=ROOT/'Notes'
def inline(s):
 s=html.escape(s)
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:f'<a href="{html.escape(html.unescape(m[2]),quote=True)}">{m[1]}</a>',s)
 return re.sub(r'\*\*(.*?)\*\*',r'<strong>\1</strong>',s)
def render(s):
 lines=s.splitlines();result=[];i=0
 while i<len(lines):
  l=lines[i]
  if not l.strip():i+=1;continue
  if l.startswith('#'):
   level=len(l)-len(l.lstrip('#'));result.append(f'<h{level}>{inline(l[level:].strip())}</h{level}>');i+=1
  elif l.startswith('- '):
   items=[]
   while i<len(lines) and lines[i].startswith('- '):items.append('<li>'+inline(lines[i][2:])+'</li>');i+=1
   result.append('<ul>'+''.join(items)+'</ul>')
  elif l.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].startswith('|'):
    cells=[c.strip() for c in lines[i].strip('|').split('|')];i+=1
    if all(re.fullmatch(r':?-+:?',c) for c in cells):continue
    tag='th' if not rows else 'td';rows.append('<tr>'+''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells)+'</tr>')
   result.append('<div class="table"><table>'+''.join(rows)+'</table></div>')
  else:result.append('<p>'+inline(l)+'</p>');i+=1
 return '\n'.join(result)
CSS='''*{box-sizing:border-box}body{overflow-wrap:anywhere;margin:0;background:#f3f5f1;color:#182d2a;font:17px/1.65 system-ui,sans-serif}main{max-width:850px;margin:auto;padding:24px}h1{font-size:clamp(27px,5vw,40px);line-height:1.15}h2{font-size:23px;border-bottom:2px solid #c7d8cb;padding-bottom:5px}a{color:#146c62;overflow-wrap:anywhere}header,nav,.controls{display:flex;flex-wrap:wrap;gap:12px;align-items:center}button,input,select{font:inherit;padding:10px;border:1px solid #c1cec9;border-radius:8px;background:white}input{width:100%}.card,article{background:white;border:1px solid #dbe3dd;border-radius:14px;padding:22px;margin:18px 0}li{margin:9px 0}small,.muted{color:#526961}table{border-collapse:collapse;width:100%;font-size:15px}th,td{text-align:left;padding:9px;border-bottom:1px solid #ddd;overflow-wrap:normal;word-break:normal}.table{overflow-x:auto}.flow{display:grid;gap:6px;text-align:center;margin:20px auto;max-width:440px}.step{padding:12px;border:1px solid #8db3a4;background:#edf6ef;border-radius:9px}.arrow{font-size:23px;line-height:1}.tag{font-size:13px;text-transform:uppercase;letter-spacing:.1em;color:#426452}.coverage{font-size:14px}nav a{padding:8px 14px;background:#e3eee7;border-radius:8px;text-decoration:none}@media(max-width:480px){main{padding:14px}article,.card{padding:16px}table{font-size:13px}th,td{padding:6px}}@page{size:A4;margin:16mm}@media print{body{background:white;font-size:11pt;line-height:1.4}main{padding:0;max-width:none}nav,.controls,input,select{display:none}article,.card{padding:0;border:none}h2{break-after:avoid}li,.step,tr{break-inside:avoid}a{color:inherit;text-decoration:none}.flow{max-width:90mm}h1{font-size:25pt}}'''
CSS+='''.subject-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.subject-grid>details.group{margin:0}.subject-grid>details[open]{grid-column:1/-1}@media(max-width:600px){.subject-grid{grid-template-columns:1fr}}details.group{background:white;border:1px solid #dbe3dd;border-radius:12px;margin:10px 0}summary{cursor:pointer;padding:13px 16px;font-weight:650;line-height:1.4}summary:hover{background:#edf6ef;border-radius:12px}summary:focus-visible{outline:3px solid #146c62;outline-offset:2px}.count{font-weight:400;color:#526961;font-size:14px;margin-left:8px}.group-content{padding:0 16px 12px}.topic-row{padding:11px 0;border-top:1px solid #e3e9e5;line-height:1.4}.topic-row a{font-weight:600}.topic-row small{display:block;margin-top:4px}.day{border-top:1px solid #e3e9e5}.day summary{padding-left:0}.day ul{margin-top:0}.compact-nav{margin:18px 0}.empty{padding:20px}#topics h2,#by-date h2{margin-top:25px}.group-content .group{margin-left:4px}[hidden]{display:none!important}@media print{summary{padding:6px 0}.group-content{padding:0}.group{border:none!important}.compact-nav{display:none}}'''

def shell(title,body,prefix=''):
 return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+html.escape(title)+'</title><style>'+CSS+'</style><main>'+body+'</main></html>'
data=json.loads((OUT/'Topics.json').read_text())
# Preserve edits made directly to the editable Markdown files.
state_path=OUT/'Build State.json'
prior=json.loads(state_path.read_text()) if state_path.exists() else {}
for t in data['topics']:
 path=OUT/t['subject']/(t['id']+'.md');key=str(path.relative_to(OUT))
 if path.exists() and key in prior and hashlib.sha256(path.read_bytes()).hexdigest()!=prior[key]:
  edited=path.read_text().split('\n## PDF coverage\n',1)[0].strip()
  t['markdown']=edited.split('\n',1)[1].strip() if edited.startswith('# ') else edited
(OUT/'Topics.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
new_state={}
topics=sorted(data['topics'],key=lambda t:(t['subject'],t['title']))
flows={'groundwater':['Pollutant source / geogenic chemistry','Groundwater contamination','Exposure through drinking / food','Health and livelihood harm','Source control + safe water + monitoring'],'renewable-energy':['Renewable generation','Transmission + storage + flexibility','Reliable grid integration','Affordable cleaner electricity'],'preventive-health':['Reduce population risk','Appropriate screening','Confirm diagnosis + referral','Affordable treatment + follow-up','Track disease control and equity'],'great-nicobar':['Compare project alternatives','Assess cumulative ecological and social impacts','Protect tribal rights + consult communities','Set transparent safeguards and security rules','Monitor compliance and outcomes'],'europa':['Tidal heating + water-rock chemistry','Subsurface liquid ocean','Potential usable chemical energy','Evaluate habitability','Habitability does not prove life'],'earthquakes':['Stress builds along a fault','Sudden slip releases stored energy','Body + surface waves propagate','Shaking interacts with local soils and buildings','Preparedness + resilient construction reduce losses'],'lead-pollution':['Lead source','Dust / food / water / workplace exposure','Lead accumulates in body','Neurodevelopmental and systemic harm','Prevent exposure + screen + remediate'],'sea-level-rise':['Warming','Ocean expansion + melting land ice','Rising relative sea level','Flooding + salinity + erosion','Adaptation + emissions reduction'],'space-sector':['PSLV launches primary payloads','Spent PS4 becomes POEM platform','Hosted in-orbit experiments','Space qualification for future missions'],'operation-greens':['Production clusters / FPOs','Storage + transport + processing','Stronger market links','Less loss + better producer returns'],'sea-otters':['Sea otters prey on sea urchins','Reduced grazing pressure','Healthier kelp forests','More habitat and biodiversity'],'green-steel':['Efficiency + scrap + clean power / hydrogen','Lower production emissions','Standards + green procurement','Demand and investment for cleaner steel']}
flows.update({
 'sonobuoys':['Aircraft / helicopter deploys buoy','Hydrophone descends; radio float stays above water','Listen passively or emit active sonar','Transmit measurements to host platform','Analyse and localise submarine contacts'],
 'genome-india':['Collect consenting participants’ samples','Sequence + quality checks','Catalogue variants / reference haplotypes','Secure research access','Validate clinical / public-health applications'],
 'vulture-drugs':['Livestock exposed to toxic veterinary NSAID','Drug residues remain in carcass','Vultures scavenge contaminated tissues','Renal injury + visceral gout','Enforcement + safe veterinary alternatives'],
 'workplace-ethics':['Identify excessive workload','Assess health and safety risks','Redistribute / resource work','Protect rest + confidential grievance access','Review workload and wellbeing outcomes'],
 'kalpeni':['Volcanic island + fringing coral reef','Subsidence with upward reef growth','Barrier reef around a lagoon','Ring-like atoll after island submergence'],
 'alaknanda':['Satopanth / Bhagirath Kharak headwaters','Vishnuprayag + Dhauliganga','Nandprayag + Nandakini','Karnaprayag + Pindar','Rudraprayag + Mandakini','Devprayag + Bhagirathi = Ganga'],
 'crowd-safety':['Assess venue capacity and expected arrivals','Separate flows + keep exits clear','Monitor pressure and bottlenecks','Act early + communicate clearly','Medical response + review accountability'],
 'anaemia':['Finger-prick sample','Strip + portable reader','Assess iron status','Record + interpret with clinical context','Appropriate treatment / referral + follow-up'],
 'tidal-tails':['Galaxies interact gravitationally','Tidal forces distort and strip outer material','Stars + gas form elongated tails','Clumps / candidate diffuse system form','Observations constrain galaxy evolution'],
})
flows.update({'plasticisers':['Phthalate additive leaches from a product','Esterase hydrolyses an ester bond','Monoester and alcohol intermediates','Additional microbial metabolic steps','Assess residual toxicity and mineralisation'],'dnt-seed':['Accessible identification and documentation','Portable entitlements and correct classification','Education + health + housing + livelihoods','Participation and anti-stigma safeguards','Audit inclusion and outcomes']})
flows.update({
 'svamitva':['Drone survey of village abadi','Ground verification + public objections','Resolve boundaries under State law','Issue property card / Record of Rights','Update records + enable planning / assessed credit'],
 'telesurgery':['Surgeon at remote console','Reliable encrypted network + low latency','Robotic instruments + cameras at patient site','On-site team monitors and provides emergency backup','Clinical follow-up + incident review'],
 'imec':['India: sea leg to Arabian Gulf','Gulf ports: transfer ship → rail','Overland links via Saudi Arabia / Jordan','Haifa: transfer rail → ship','European port + onward distribution'],
 'snakebite':['Exposure prevention + community awareness','Prompt access to trained clinical care','Assessment + suitable antivenom / supportive treatment','Manage complications + rehabilitation','Report cases + improve access and readiness'],
})
flows.update({
 'h1b':['Qualifying employer + specialty-occupation job','Certified Labor Condition Application','USCIS petition and applicable cap selection','Visa processing / admission where required','Compliant temporary employment + eligible extensions'],
 'space-surveillance':['Observe resident space objects','Determine and update orbital tracks','Assess conjunction / collision risk','Notify operators and plan avoidance','Monitor subsequent orbital changes'],
 'tb':['Prevent exposure + address nutrition and risk','Find symptomatic and high-risk cases','Confirm TB and test drug resistance','Appropriate treatment + adherence support','Follow up patients and eligible contacts'],
 'naivasha':['Nutrient enrichment','Rapid water-hyacinth growth','Dense floating mats','Reduced light / gas exchange + access','Control nutrients + suitable removal / monitoring'],
 'barrier-reef':['Heat or other sustained stress','Loss of symbiotic algae / pigment','Coral bleaching','Recovery if stress resolves; mortality if prolonged','Reduce warming pressure + protect water quality'],
 'kalaripayattu':['Maippayattu: condition the body','Kolthari: wooden weapons','Angathari: metal weapons','Verumkai: unarmed combat'],
 'sanjay':['Ground + aerial sensor observations','Integrate and remove duplicate tracks','Common Surveillance Picture','Secure Army data / satellite networks','Commander assessment and decisions'],
 'gbs':['Antecedent infection or other recognised association','Misguided immune response','Peripheral nerve injury','Weakness + possible respiratory / autonomic complications','Monitored clinical treatment + rehabilitation'],
 'kawacham':['Authoritative hazard observations / forecasts','Assess threat and authorise warnings','Sirens + voice + lights + other alert channels','People receive, understand and act','Coordinated response + monitoring'],
 'chinar':['Survey tree + record coordinates','Unique ID and QR-linked record','Record condition / estimated age / dimensions','Repeat inspection and compare changes','Conservation action + accountable monitoring'],
})
flows.update({
 'critical-minerals':['Explore and quantify resources','Assess viable extraction + safeguards','Refine and process materials','Manufacture strategic products','Recycle + diversify future supply'],
 'leprosy':['Recognise sensory loss / nerve signs','Confirm disease and classify','Complete appropriate multidrug treatment','Screen contacts + prevent disability','Follow up + reduce stigma'],
 'income-tax':['Calculate taxable income after eligible deductions','Apply marginal slab rates','Check rebate eligibility / special-rate income','Assess marginal relief where applicable','Determine final liability including applicable cess'],
 'arunachal-glaciers':['Glacier retreat under changing climate','Some sites develop expanding lakes','Assess lake / moraine instability','Outburst can threaten downstream people and assets','Monitoring + warning + safe planning'],
 'mental-health-work':['Identify psychosocial risks with workers','Improve workload and working conditions','Offer confidential accessible care','Support treatment and return to work','Evaluate equity and outcomes'],
})
flows.update({
 'upi':['Authenticate payment request','NPCI routes between participating institutions','Account debit + beneficiary credit','Confirmation and transaction record','Resolve failures and fraud through accountable support'],
 'thermal-emissions':['Coal combustion emits SO2','FGD treats flue gas','Verify equipment operation and emissions','Disclose compliance and enforce standards','Protect health alongside cleaner generation'],
 'heart-failure':['Prevent risk and treat precursor disease','Recognise symptoms and refer','Confirm diagnosis and assess cause','Affordable evidence-based care + follow-up','Monitor outcomes and remove access barriers'],
 'nuclear-liability':['Nuclear incident causes covered damage','Operator compensates under applicable law','Specified right of recourse may apply','Assess supplier accountability and insurance','Independent safety oversight + victim protection'],
 'bombay-blood':['Identify Bombay phenotype and antibodies','Assess transfusion versus organ compatibility','Specialist desensitisation where appropriate','Monitor transplant and immunosuppression','Long-term follow-up + donor and recipient welfare'],
 'gold-smuggling':['Price / tax arbitrage and illicit funds','Cross-border criminal networks','Customs intelligence + lawful financial investigation','Trace assets and enforce accountability','Review incentives while supporting legitimate trade'],
 'railway-budget':['Allocate capital and maintenance resources','Deliver track, signalling and rolling stock','Verify safety and reliable capacity','Improve passenger and freight outcomes','Audit costs, utilisation and delivery'],
 'urban-budget':['Identify inclusive city service needs','Prepare viable projects and clear funding','Coordinate local capacity + State / Union support','Deliver mobility, housing and basic services','Audit access, costs and resilience'],
})
flows.update({
 'shakti-semiconductors':['ISRO IISU defines application needs','IIT Madras designs SHAKTI-based IRIS','SCL fabricates the processor','Packaging + board manufacture + assembly','Software validation + application qualification'],
 'ai-drug-testing':['Define regulatory question and context of use','Assess model risk and credibility requirements','Validate representative data and performance','Document limitations + obtain regulatory review','Monitor changes and clinical outcomes'],
 'malaria':['Anopheles injects sporozoites','Liver infection → merozoites','Red-cell cycle; some form gametocytes','Mosquito ingests gametocytes','Parasite development → new sporozoites'],
 'panchayat-devolution':['State law delegates functions','Match funds + staff to responsibilities','Gram Sabha and GPDP guide local priorities','Deliver services + disclose expenditure','Social audit + elections + corrective action'],
 'faecal-coliform':['Sewage / animal waste enters water','Sample with documented methods','Interpret indicators + other quality parameters','Control pollution sources and maintain treatment','Repeat monitoring + communicate results'],
 'mrna-cancer':['Profile tumour and candidate antigens','Design personalised mRNA','Stimulate antigen-specific immunity','Assess safety and clinical benefit in trials','Regulatory evaluation + equitable access'],
 'fusion':['Heat fuel and confine plasma','Sustain stable fusion conditions','Manage heat + neutrons + tritium','Demonstrate net electricity and reliability','Assess costs before commercial deployment'],
})
flows.update({
 'employment-plfs':['Identify the reference period and population','Classify employed / unemployed / outside labour force','Compute UR using labour force denominator','Compare LFPR, WPR, earnings and job quality','Assess employment policy with consistent data'],
 'moonlight-navigation':['Moonlight scatters through atmosphere','Sky acquires a polarisation pattern','Ant detects e-vector orientation','Filter rotation shifts the available compass cue','Heading change supports directional use'],
 'telecom-resilience':['Map hazard and network dependencies','Protect towers, power and cable routes','Provide diverse backup and response access','Coordinate operators and disaster agencies','Restore services + assess resilience'],
 'mediation':['Identify a suitable dispute','Obtain informed voluntary participation','Neutral mediator facilitates negotiation','Parties agree to a lawful settlement or return to court','Track fair, durable outcomes'],
 'hku5':['Observe laboratory receptor compatibility','Test entry in relevant experimental systems','Assess evidence for actual infections','Monitor transmission and clinical outcomes if observed','Communicate risk without assuming a pandemic'],
 'solid-waste':['Segregate at source','Keep streams separate during collection','Recover recyclables and treat suitable organics','Control emissions and dispose of residues safely','Audit service quality and worker protection'],
})
flows.update({'sma':['SMN1 defect','Reduced SMN protein','Motor-neuron loss','Muscle weakness','Disease-modifying treatment + supportive care'],'time-use-care':['Recognise unpaid care','Reduce avoidable time burdens','Redistribute responsibilities','Represent and fairly reward care workers'],'black-plastic':['Electronic plastic waste','Unsafe mixing into recycling streams','Possible chemical migration','Exposure assessment','Segregation + traceability + food-contact standards']})
flows.update({'urine-fertiliser':['Collect nutrient-rich urine','Recover urea + electrochemically produce hydrogen peroxide','Form percarbamide','Test safety, energy use and crop response'],'apaar':['Clear purpose + informed consent','Minimum necessary academic data','Secure access + accurate records','Correction, alternatives and grievance redress'],'consumer-credit':['Assess income and total obligations','Borrow within repayment capacity','Monitor debt service and stress','Transparent terms + timely grievance support'],'small-modular-reactors':['Design and safety assessment','Approvals + financing','Manufacture + site construction','Testing + licensed operation','Fuel management + waste safeguards']})
flows.update({'trade-remedies':['Evidence of dumping / subsidy / import surge','DGTR investigation + injury assessment','Recommendation under applicable rules','Government notification / other lawful measure','Review effects and sunset conditions'],'permafrost':['Ground warms','Ice-rich ground thaws / slopes weaken','Infrastructure and drainage risks change','Ground monitoring + calibrated mapping','Risk-sensitive siting, drainage and warnings'],'gig-work':['Platform allocates work and rates performance','Check net earnings, control and worker risks','Transparent terms + fair appeal','Portable benefits + representation','Measure safety and livelihood outcomes'],'oams':['Minister gives an assurance','Record and assign responsible department','Track implementation / approved extension','Submit implementation information','Committee scrutiny and follow-up']})
flows.update({'pcm':['Heat input charges material','Phase transition absorbs latent heat','Stored heat buffers temperature','Solidification releases heat','Recharge and monitor finite capacity'],'anti-defection':['Membership conduct / whip violation','Check Schedule conditions and exemptions','Speaker or Chairman adjudicates','Judicial review with procedural safeguards'],'turkiye':['Black Sea','Bosphorus','Sea of Marmara','Dardanelles','Aegean Sea → Mediterranean'],'hiv':['All people living with HIV','95% know their status','95% of diagnosed people receive ART','95% of treated people achieve viral suppression'],'parker-solar':['Observe corona and solar wind','Measure fields, particles and images','Test heating and acceleration mechanisms','Improve space-weather understanding']})
flows.update({'nuclear-battery':['Radioisotope decays','Beta-particle energy reaches semiconductor','Charge carriers generate electric current','Low-power load operates over a long period'],'rapid-crispr':['Prepare sample','RT-LAMP amplifies target','Cas12a recognises fusion-associated sequence','Reporter cleavage produces a visible signal','Validated diagnosis → prompt specialist care'],'gi-tags':['Origin-linked quality, reputation or skill','Registration and authorised users','Quality control and traceability','Branding and market access','Fair producer returns'],'food-safety':['Control storage and hygiene','Detect spoilage / supply-chain failures','Prevent unsafe products reaching consumers','Investigate and trace incidents','Improve standards, training and monitoring']})
def link(t):return quote(t['subject'])+'/'+t['id']+'.html'
for i,t in enumerate(topics):
 folder=OUT/t['subject'];folder.mkdir(exist_ok=True)
 for stage in ['Prelim','Mains']:
  p=folder/f'PYQ-{stage}.json'
  if not p.exists():p.write_text(json.dumps({'subject':t['subject'],'exam_stage':stage,'questions':[]},indent=2))
 coverage=' · '.join(f'{d}: pp. '+', '.join(map(str,p)) for d,p in sorted(t['coverage'].items()))
 md='# '+t['title']+'\n\n'+t['markdown']+'\n\n## PDF coverage\n\n'+coverage+'\n'
 mdpath=folder/(t['id']+'.md');mdpath.write_text(md)
 new_state[str(mdpath.relative_to(OUT))]=hashlib.sha256(mdpath.read_bytes()).hexdigest()
 nav='<nav><a href="../index.html">All topics</a>'
 if i:nav+='<a href="../'+link(topics[i-1])+'">← Previous</a>'
 else:nav+='<a href="../index.html">← Back to all topics</a>'
 if i+1<len(topics):nav+='<a href="../'+link(topics[i+1])+'">Next →</a>'
 else:nav+='<a href="../index.html">Next → All topics</a>'
 nav+='</nav>'
 body=nav+'<p class="tag">'+html.escape(t['subject'])+'</p><h1>'+html.escape(t['title'])+'</h1><div class="controls"><button onclick="window.print()">Print / Save as PDF</button><a href="'+t['id']+'.md">Editable notes</a></div><article>'+render(t['markdown'])
 if t['id'] in flows:body+='<div class="flow" aria-label="Recall flowchart">'+'<div class="arrow" aria-hidden="true">↓</div>'.join('<div class="step">'+html.escape(x)+'</div>' for x in flows[t['id']])+'</div>'
 body+='<h2>PDF coverage</h2><p class="coverage">'+html.escape(coverage)+'</p></article>'+nav
 (folder/(t['id']+'.html')).write_text(shell(t['title'],body))
queue=json.loads((OUT/'Processing Log.json').read_text());done=[x for x in queue['files'] if x['status']=='reviewed']
body='<header><h1>Current Affairs</h1><button onclick="window.print()">Print / Save as PDF</button></header><p>'+str(len(done))+' of '+str(len(queue['files']))+' PDFs reviewed · '+str(len(topics))+' consolidated topics</p><div class="controls"><input id="search" placeholder="Search topics or facts" aria-label="Search notes"><select id="subject" aria-label="Subject"><option value="">All subjects</option>'+''.join('<option>'+html.escape(s)+'</option>' for s in sorted({t['subject'] for t in topics}))+'</select></div>'
gaps=queue.get('review_gaps',[])
if gaps:
 body+='<details class="group"><summary>Review progress and missing issues<span class="count">'+str(len(gaps))+' gaps</span></summary><div class="group-content"><p>Next available PDF: '+html.escape(queue.get('next_pdf',''))+'</p><ul>'+''.join('<li>'+html.escape(g['date'])+' — '+html.escape(g['status'])+'</li>' for g in gaps)+'</ul></div></details>'
body+='<nav class="compact-nav"><a href="#topics">Browse subjects</a><a href="#by-date">Browse dates</a><button id="expand" type="button">Expand sections</button><button id="collapse" type="button">Collapse all</button></nav><section id="topics"><h2>Topics by subject</h2><div class="subject-grid">'
for subject in sorted({t['subject'] for t in topics}):
 members=[t for t in topics if t['subject']==subject]
 body+='<details class="group subject-group"><summary>'+html.escape(subject)+'<span class="count" data-total="'+str(len(members))+'">'+str(len(members))+(' topic' if len(members)==1 else ' topics')+'</span></summary><div class="group-content">'
 for t in members:
  dates=', '.join(sorted(t['coverage']))
  body+='<div class="topic-row" data-subject="'+html.escape(t['subject'])+'" data-search="'+html.escape(t['title']+' '+t['subject']+' '+dates+' '+t['markdown'],quote=True)+'"><a href="'+link(t)+'">'+html.escape(t['title'])+'</a><small>'+dates+'</small></div>'
 body+='</div></details>'
body+='</div></section><section id="by-date"><h2>By year and month</h2>'
for year in sorted({f['date'][:4] for f in done}):
 year_files=[f for f in done if f['date'].startswith(year)]
 body+='<details class="group year-group"><summary>'+year+'<span class="count">'+str(len(year_files))+' reviewed days</span></summary><div class="group-content">'
 for month in sorted({f['date'][5:7] for f in year_files}):
  month_files=[f for f in year_files if f['date'][5:7]==month]
  body+='<details class="group month-group"><summary>'+calendar.month_name[int(month)]+'<span class="count">'+str(len(month_files))+' reviewed days</span></summary><div class="group-content">'
  for f in month_files:
   day_topics=[t for t in topics if f['date'] in t['coverage']]
   body+='<details class="day"><summary>'+f['date']+'<span class="count">'+str(len(day_topics))+' topics</span></summary><ul>'+''.join('<li><a href="'+link(t)+'">'+html.escape(t['title'])+'</a></li>' for t in day_topics)+'</ul></details>'
  body+='</div></details>'
 body+='</div></details>'
body+='</section><p id="no-results" class="empty" hidden>No matching topics. Try another word or subject.</p>'
body+="""<script>const q=document.querySelector('#search'),s=document.querySelector('#subject');let wasFiltering=false;function filter(){const active=!!q.value.trim()||!!s.value;let shown=0;document.querySelectorAll('.subject-group').forEach(g=>{let matches=0;g.querySelectorAll('[data-search]').forEach(c=>{c.hidden=!(c.dataset.search.toLowerCase().includes(q.value.trim().toLowerCase())&&(!s.value||c.dataset.subject===s.value));if(!c.hidden)matches++});g.hidden=!matches;g.querySelector('.count').textContent=matches+(matches===1?' topic':' topics');if(active)g.open=matches>0;else if(wasFiltering)g.open=false;shown+=matches});document.querySelector('#by-date').hidden=active;document.querySelector('#no-results').hidden=shown>0;wasFiltering=active}q.addEventListener('input',filter);s.addEventListener('change',filter);document.querySelector('#expand').addEventListener('click',()=>document.querySelectorAll('.subject-group:not([hidden]),.year-group,.month-group').forEach(d=>d.open=true));document.querySelector('#collapse').addEventListener('click',()=>document.querySelectorAll('details').forEach(d=>d.open=false));let printState=[];addEventListener('beforeprint',()=>{printState=[...document.querySelectorAll('details')].map(d=>d.open);document.querySelectorAll('details').forEach(d=>d.open=true)});addEventListener('afterprint',()=>document.querySelectorAll('details').forEach((d,i)=>d.open=printState[i]));</script>"""
(OUT/'index.html').write_text(shell('Current Affairs',body))
(OUT/'index.md').write_text('# Current Affairs\n\n'+''.join(f"- [{t['title']}]({t['subject']}/{t['id']}.md)\n" for t in topics))
state_path.write_text(json.dumps(new_state,indent=2))
print('Built',len(topics),'topic pairs and index')
