/* Curated pictures only. No runtime keyword search and no history writes. */
(function(root){'use strict';
const CACHE='rise-voca-flyers-approved-pictures-v1';
const PRIORITY=['OpenMoji','Material Symbols','Tabler Icons','Phosphor Icons','Material Design Icons','Streamline'];
const LOCAL=/^\.\/assets\/illustrations\/[a-z0-9-]+-[a-f0-9]{12}\.(svg|png|webp)$/;
function isLocal(value){return typeof value==='string'&&LOCAL.test(value);}
function validUrl(value){
 if(isLocal(value))return true;
 try{const u=new URL(value);return u.protocol==='https:'&&!u.username&&!u.password&&!u.port&&!u.search&&!u.hash&&u.hostname==='raw.githubusercontent.com'&&/^\/hfg-gmuend\/openmoji\/15\.1\.0\/color\/svg\/[A-F0-9-]+\.svg$/.test(u.pathname);}catch(_){return false;}
}
function urlFor(value){return isLocal(value)?new URL(value,root.location?.href||'https://localhost.invalid/').href:value;}
function reviewKey(e){return e?.asset_id&&/^[a-f0-9]{64}$/.test(e.sha256||'')?e.provider+':'+e.asset_id+':'+e.sha256:null;}
function decision(e,reviews){const key=reviewKey(e);return key&&reviews&&typeof reviews==='object'&&Object.hasOwn(reviews,key)?reviews[key]:null;}
function candidates(registry,id){
 const raw=registry.candidatesByWordId?.[id],list=Array.isArray(raw)?raw:raw?[raw]:[];
 return list.filter(e=>e.provider!=='ARASAAC'&&PRIORITY.includes(e.provider)&&e.review_status==='needs_manual_review'&&isLocal(e.url)&&reviewKey(e))
  .sort((a,b)=>PRIORITY.indexOf(a.provider)-PRIORITY.indexOf(b.provider));
}
function choose(registry,id,reviews={}){
 const main=registry.byWordId?.[id];
 // A rejected mapping cannot reappear because an old preference or cache exists.
 if(main){return main.provider!=='ARASAAC'&&main.review_status==='approved_by_user'&&validUrl(main.url)?main:null;}
 return candidates(registry,id).find(e=>decision(e,reviews)==='approved')||null;
}
function label(e,reviews){
 if(!e)return 'No verified mapping';
 if(e.review_status==='needs_replacement'||e.review_status==='rejected')return 'Held back / rejected';
 if(e.review_status==='approved_by_user')return 'User-approved';
 const d=decision(e,reviews);return d==='approved'?'Approved on this device':d==='rejected'?'Rejected on this device':'Needs manual review';
}
function info(registry,id,reviews){const e=choose(registry,id,reviews)||registry.byWordId?.[id]||candidates(registry,id)[0];return {source:e?.provider||'None',review:label(e,reviews)};}
async function cached(entry){
 if(!root.caches||!validUrl(entry.url))return null;
 try{const r=isLocal(entry.url)?await caches.match(urlFor(entry.url)):await(await caches.open(CACHE)).match(entry.url);
 return r?.ok?await r.blob():null;}catch(_){return null;}
}
async function source(entry,allowNetwork){
 if(!entry||!validUrl(entry.url))return null;
 const blob=await cached(entry);if(blob)return URL.createObjectURL(blob);
 // First-party, bundled images do not require third-party network consent.
 return isLocal(entry.url)?entry.url:allowNetwork?entry.url:null;
}
function entries(registry,reviews={}){
 const ids=new Set([...Object.keys(registry.byWordId||{}),...Object.keys(registry.candidatesByWordId||{})]);
 return [...new Map([...ids].map(id=>choose(registry,id,reviews)).filter(Boolean).map(e=>[e.url,e])).values()];
}
async function count(list){
 if(!root.caches)throw Error('Picture storage needs HTTPS or localhost in a supported browser.');
 let saved=0;for(const e of list)if(await cached(e))saved++;return {saved,total:list.length};
}
async function decode(blob){
 const url=URL.createObjectURL(blob);try{await new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>im.naturalWidth?resolve():reject(Error('Empty image'));im.onerror=()=>reject(Error('Invalid image response'));im.src=url;});}finally{URL.revokeObjectURL(url);}
}
async function saveOne(e){
 if(!validUrl(e.url))throw Error('Unapproved image host or path');
 if(await cached(e))return;
 const abort=new AbortController(),timer=setTimeout(()=>abort.abort(),12000);
 try{const r=await fetch(urlFor(e.url),{mode:'cors',credentials:'omit',referrerPolicy:'no-referrer',signal:abort.signal,cache:'no-cache'});
  if(!r.ok)throw Error('HTTP '+r.status);
  const type=(r.headers.get('content-type')||'').split(';')[0];
  if(!['image/svg+xml','image/png','image/jpeg','image/webp'].includes(type))throw Error('Response is not an image');
  const blob=await r.blob();if(!blob.size||blob.size>2*1024*1024)throw Error('Invalid image size');
  await decode(blob);await(await caches.open(CACHE)).put(urlFor(e.url),new Response(blob,{headers:{'content-type':type}}));
 }finally{clearTimeout(timer);}
}
function controls(D,prefs,readOnly,onDecision){
 const $=id=>document.getElementById(id),status=$('pictureCacheStatus');let busy=false,reviewQueue=Promise.resolve();
 const chosen=()=>entries(D.illustrations,prefs().pictureReviews);
 async function report(){try{const c=await count(chosen());status.textContent=c.saved+' / '+c.total+' selected distinct picture files saved. The 2 local review pictures are also bundled with the offline app. Speech is separate.';}catch(e){status.textContent=e.message;}}
 $('checkPictureCache').addEventListener('click',report);
 $('downloadPictures').addEventListener('click',async()=>{
  if(busy||readOnly)return;
  if(!root.caches){status.textContent='Picture caching is unavailable here. Open the hosted HTTPS PWA.';return;}
  const list=chosen();if(!confirm('Save '+list.length+' selected picture files for offline use? This contacts OpenMoji for missing approved images, but sends no learning history. Local replacements are served by this app.'))return;
  busy=true;$('downloadPictures').disabled=true;let index=0,done=0;const failed=[];
  async function worker(){while(index<list.length){const e=list[index++];try{await saveOne(e);}catch(err){failed.push(e.word+': '+err.message);}done++;status.textContent='Checked '+done+' / '+list.length+' picture files. Failed: '+failed.length+'. Keep this page open.';}}
  try{await Promise.all(Array.from({length:Math.min(4,list.length)},worker));await report();if(failed.length)status.textContent+=' '+failed.length+' download(s) failed. Press Save again to retry missing files. Examples: '+failed.slice(0,3).join('; ');}
  catch(e){status.textContent='Picture save failed: '+e.message;}finally{busy=false;$('downloadPictures').disabled=readOnly;}
 });
 $('downloadPictures').disabled=readOnly;
 $('requestPersistent').addEventListener('click',async()=>{try{if(!navigator.storage?.persist)throw Error('Persistent-storage requests are not supported here.');const ok=await navigator.storage.persist();$('durableStatus').textContent=ok?'Persistent storage granted. This is not a backup; deleting website data still deletes history.':'Persistent storage was not granted. Keep regular JSON backups.';}catch(e){$('durableStatus').textContent=e.message;}});
 for(const id of Object.keys(D.illustrations.candidatesByWordId||{}))for(const e of candidates(D.illustrations,id)){
  const card=document.createElement('article'),title=document.createElement('h3'),meaning=document.createElement('p'),img=new Image(),load=document.createElement('button'),approve=document.createElement('button'),reject=document.createElement('button'),result=document.createElement('p'),badge=document.createElement('p'),links=document.createElement('p'),sourceLink=document.createElement('a'),licenseLink=document.createElement('a');
  let loaded=false,loading=false,pending=false,objectUrl=null;
  card.dataset.word=id;title.textContent=e.word;meaning.textContent=e.meaning_vi;img.alt=e.alt||e.word;img.hidden=true;img.referrerPolicy='no-referrer';
  load.textContent='Preview local picture';approve.textContent='Approve for lessons';reject.textContent='Reject / stop using';
  result.setAttribute('role','status');badge.className='picture-source';
  function refresh(){badge.textContent='Source: '+e.provider+' | '+label(e,prefs().pictureReviews);approve.disabled=readOnly||!loaded||pending;reject.disabled=readOnly||pending;load.disabled=loading||pending;}
  sourceLink.href=e.source_url;sourceLink.target='_blank';sourceLink.rel='noopener noreferrer';sourceLink.textContent=e.creator+' - original source';
  licenseLink.href=e.license_url;licenseLink.target='_blank';licenseLink.rel='noopener noreferrer';licenseLink.textContent=e.license;
  links.append(sourceLink,document.createTextNode(' | '),licenseLink);
  result.textContent='Technical image check passed. Please preview and decide whether it teaches the correct meaning. Approval is local to this device, not a quiz result.';
  async function decide(value){if(readOnly||pending||(value==='approved'&&!loaded))return;pending=true;refresh();try{const task=reviewQueue.then(()=>onDecision(reviewKey(e),value));reviewQueue=task.catch(()=>{});await task;result.textContent=value==='approved'?'Approved on this device. Used after a correct answer; no learning result was created.':'Rejected on this device. This image will not appear in lessons.';}catch(err){result.textContent='Could not save review: '+err.message;}finally{pending=false;refresh();}}
  approve.addEventListener('click',()=>decide('approved'));reject.addEventListener('click',()=>decide('rejected'));
  load.addEventListener('click',async()=>{
   if(loading||pending)return;loading=true;loaded=false;img.hidden=true;refresh();result.textContent='Loading the bundled picture...';
   if(objectUrl){URL.revokeObjectURL(objectUrl);objectUrl=null;}
   img.onload=()=>{loading=false;loaded=img.naturalWidth>0;img.hidden=!loaded;result.textContent=loaded?(e.visual_description+' No text is overlaid in this picture. Approve only if the meaning is clear.'):'Image unavailable. Approval is disabled.';refresh();};
   img.onerror=()=>{loading=false;loaded=false;img.hidden=true;result.textContent='Image unavailable. Approval is disabled; no replacement is selected automatically.';refresh();};
   try{const src=await source(e,false);if(!src)throw Error('No valid local image');if(src.startsWith('blob:'))objectUrl=src;img.src=src;}catch(err){loading=false;result.textContent='Image unavailable: '+err.message;refresh();}
  });
  refresh();const buttons=document.createElement('div');buttons.className='review-actions';buttons.append(load,approve,reject);card.append(title,meaning,badge,buttons,img,result,links);$('candidatePreviews').append(card);
 }
}
root.FlyersPictures={choose,validUrl,isLocal,urlFor,reviewKey,decision,candidates,label,info,entries,cached,source,count,saveOne,controls,cacheName:CACHE,providerPriority:PRIORITY};
})(typeof globalThis!=='undefined'?globalThis:this);
