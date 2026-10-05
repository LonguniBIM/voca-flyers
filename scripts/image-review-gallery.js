/* Gallery source, embedded by sync-catalog.py. Reviews never create learning records. */
function candidateRows(D){
 const index=new Map(D.library.words.map(w=>[w.id,w]));
 return Object.keys(D.illustrations.candidatesByWordId||{}).flatMap(id=>candidates(D.illustrations,id).map(entry=>({id,entry,word:index.get(id)}))).filter(r=>r.word);
}
function filterRows(rows,filters,reviews){
 const q=(filters.search||'').trim().toLocaleLowerCase();
 return rows.filter(r=>(!filters.topic||r.word.topic_ids.includes(filters.topic))&&(!filters.provider||r.entry.provider===filters.provider)&&(!q||(r.word.word+' '+r.word.meaning_vi).toLocaleLowerCase().includes(q))&&(!filters.status||(decision(r.entry,reviews)||'unreviewed')===filters.status));
}
function catalogPayload(D){return {schema_version:1,type:'rise-voca-learning-catalog',library:D.library,illustrations:D.illustrations,speaking_reference:D.speaking||[],notice:'Content catalog only. No learner history or private device reviews are included. Relative image files are distributed alongside this catalog.'};}
function reviewPayload(D,prefs){return {schemaVersion:2,type:'rise-voca-flyers-image-review-v2',sourceLibraryFingerprint:D.library.fingerprint,exportedAtUtc:new Date().toISOString(),timezone:Intl.DateTimeFormat().resolvedOptions().timeZone,scope:'All local candidate mappings; filters do not restrict this export.',reviews:candidateRows(D).map(({id,entry:e,word:w})=>({id,word:w.word,meaning:w.meaning_vi,topics:w.topic_ids,provider:e.provider,asset_id:e.asset_id,url:e.url,sha256:e.sha256,review_scope:e.review_scope||null,key:reviewKey(e),review:{status:decision(e,prefs.pictureReviews)||'unreviewed',updatedAt:prefs.pictureReviewUpdatedAt?.[reviewKey(e)]||null}}))};}
function missingRows(D){return D.library.words.filter(w=>w.mode!=='name_dictation'&&D.illustrations.byWordId?.[w.id]?.review_status!=='approved_by_user'&&!candidates(D.illustrations,w.id).length).map(w=>({word_id:w.id,word:w.word,meaning_vi:w.meaning_vi,topic_ids:w.topic_ids,reason:'No exact candidate selected. Context-specific illustration or further source research is required.'}));}
function downloadJson(name,value){const u=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json;charset=utf-8'}));const a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),2000);}
function buildGallery(D,prefs,readOnly,onDecision){
 const host=document.getElementById('candidatePreviews'),all=candidateRows(D),pageSize=24;let page=0,generation=0,queue=Promise.resolve();
 const filters={topic:'',provider:'',status:'',search:''};const urls=new Set();
 const panel=document.createElement('section');panel.className='image-review-toolbar';panel.setAttribute('aria-label','Illustration review filters');
 function select(id,title,options){const label=document.createElement('label');label.textContent=title+' ';const input=document.createElement('select');input.id=id;for(const[value,text]of options){const o=document.createElement('option');o.value=value;o.textContent=text;input.append(o);}label.append(input);panel.append(label);return input;}
 const topic=select('pictureReviewTopic','Topic',[['','All topics'],...D.library.topics.filter(t=>t.id!=='names').map(t=>[t.id,t.title])]);
 const provider=select('pictureReviewProvider','Source',[['','All sources'],...[...new Set(all.map(r=>r.entry.provider))].sort().map(s=>[s,s])]);
 const status=select('pictureReviewStatus','Review',[['','All reviews'],['unreviewed','Needs manual review'],['approved','Approved on this device'],['rejected','Rejected on this device']]);
 const label=document.createElement('label');label.textContent='Find word or meaning ';const search=document.createElement('input');search.id='pictureReviewSearch';search.type='search';search.autocomplete='off';label.append(search);panel.append(label);
 const nav=document.createElement('div');nav.className='review-actions';const prev=document.createElement('button'),next=document.createElement('button'),counter=document.createElement('span');prev.id='pictureReviewPrev';next.id='pictureReviewNext';counter.id='pictureReviewPage';counter.setAttribute('role','status');prev.textContent='Previous pictures';next.textContent='Next pictures';nav.append(prev,counter,next);panel.append(nav);
 const exports=document.createElement('div');exports.className='review-actions';
 function exportButton(id,text,fn){const b=document.createElement('button');b.id=id;b.textContent=text;b.addEventListener('click',fn);exports.append(b);}
 exportButton('exportPictureReviews','Export all image reviews (JSON)',()=>downloadJson('Flyers_Image_Reviews_'+new Date().toISOString().replace(/[:.]/g,'-')+'.json',reviewPayload(D,prefs())));
 exportButton('exportCatalog','Export library + images (JSON)',()=>downloadJson('Flyers_Library_With_Images.json',catalogPayload(D)));
 exportButton('exportMissingPictures','Export words still missing images (JSON)',()=>downloadJson('Flyers_Missing_Illustrations.json',{schema_version:1,library_fingerprint:D.library.fingerprint,scope:'All vocabulary senses with no candidate; names excluded.',words:missingRows(D)}));
 panel.append(exports);host.before(panel);
 function dispose(){generation++;for(const u of urls)URL.revokeObjectURL(u);urls.clear();host.replaceChildren();}
 function render(){
  dispose();const gen=generation,rows=filterRows(all,filters,prefs().pictureReviews),pages=Math.max(1,Math.ceil(rows.length/pageSize));page=Math.min(page,pages-1);const shown=rows.slice(page*pageSize,(page+1)*pageSize);
  prev.disabled=page===0;next.disabled=page>=pages-1;counter.textContent=rows.length+' matching word/sense mappings; page '+(page+1)+' / '+pages+' ('+all.length+' attached candidates in total).';
  if(!shown.length){const empty=document.createElement('p');empty.textContent='No pictures match these filters.';host.append(empty);return;}
  for(const {id,entry:e,word:w} of shown){
   const card=document.createElement('article');card.dataset.word=id;
   const title=document.createElement('h3'),meaning=document.createElement('p'),badge=document.createElement('p'),topics=document.createElement('p'),img=new Image(),result=document.createElement('p'),buttons=document.createElement('div');
   title.textContent=w.word;meaning.textContent=w.meaning_vi;badge.className='picture-source';topics.textContent=w.topic_ids.map(t=>D.library.topics.find(x=>x.id===t)?.title||t).join(' / ');topics.className='muted';img.alt=e.alt||w.word;img.hidden=true;img.referrerPolicy='no-referrer';result.setAttribute('role','status');buttons.className='review-actions';
   const load=document.createElement('button'),approve=document.createElement('button'),reject=document.createElement('button');load.textContent='Preview local picture';approve.textContent='Approve for lessons';reject.textContent='Reject / stop using';buttons.append(load,approve,reject);
   let loaded=false,loading=false,pending=false,objectUrl=null;
   function refresh(){badge.textContent='Source: '+e.provider+' | '+labelStatus();approve.disabled=readOnly||!loaded||pending;reject.disabled=readOnly||pending;load.disabled=loading||pending;}
   function labelStatus(){return root.FlyersPictures.label(e,prefs().pictureReviews);}
   result.textContent='Attached as a review candidate, not an approved teaching image. Preview the actual picture and compare its meaning. Approval stays on this device.';
   async function decide(value){
    if(readOnly||pending||(value==='approved'&&!loaded))return;pending=true;refresh();
    try{const task=queue.then(()=>onDecision(reviewKey(e),value));queue=task.catch(()=>{});await task;if(gen!==generation)return;result.textContent=value==='approved'?'Approved for this word/sense on this device. No learning result was created.':'Rejected for this word/sense. It will not appear in lessons.';}
    catch(err){if(gen===generation)result.textContent='Could not save review: '+err.message;}
    finally{pending=false;if(gen===generation){refresh();if(filters.status)render();}}
   }
   approve.addEventListener('click',()=>decide('approved'));reject.addEventListener('click',()=>decide('rejected'));
   load.addEventListener('click',async()=>{
    if(loading||pending)return;loading=true;loaded=false;img.hidden=true;refresh();result.textContent='Loading bundled picture...';
    if(objectUrl){URL.revokeObjectURL(objectUrl);urls.delete(objectUrl);objectUrl=null;}
    img.onload=()=>{if(gen!==generation)return;loading=false;loaded=img.naturalWidth>0;img.hidden=!loaded;result.textContent=loaded?e.visual_description+' Approve only if it clearly matches this meaning.':'Image unavailable. Approval is disabled.';refresh();};
    img.onerror=()=>{if(gen!==generation)return;loading=false;loaded=false;img.hidden=true;result.textContent='Image unavailable. Approval is disabled; no approximate image is substituted.';refresh();};
    try{const src=await source(e,false);if(!src)throw Error('No valid local image');if(gen!==generation){if(src.startsWith('blob:'))URL.revokeObjectURL(src);return;}if(src.startsWith('blob:')){objectUrl=src;urls.add(src);}img.src=src;}
    catch(err){if(gen===generation){loading=false;result.textContent='Image unavailable: '+err.message;refresh();}}
   });
   const credit=document.createElement('p'),sourceLink=document.createElement('a'),licenseLink=document.createElement('a');sourceLink.href=e.source_url;sourceLink.textContent=e.creator+' - original source';licenseLink.href=e.license_url;licenseLink.textContent=e.license;
   for(const link of [sourceLink,licenseLink]){link.target='_blank';link.rel='noopener noreferrer';}credit.append(sourceLink,document.createTextNode(' | '),licenseLink);
   refresh();card.append(title,meaning,topics,badge,buttons,img,result,credit);host.append(card);
  }
 }
 for(const[input,key]of [[topic,'topic'],[provider,'provider'],[status,'status'],[search,'search']])input.addEventListener(key==='search'?'input':'change',()=>{filters[key]=input.value;page=0;render();});
 prev.addEventListener('click',()=>{page--;render();});next.addEventListener('click',()=>{page++;render();});render();
}
