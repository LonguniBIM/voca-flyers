/* Curated pictures only. No runtime keyword search and no history writes. */
(function(root){'use strict';
const CACHE='rise-voca-flyers-approved-pictures-v1';
const PRIORITY=['OpenMoji','Material Symbols','Tabler Icons','Phosphor Icons','Material Design Icons','Streamline','Mulberry Symbols'];
const LOCAL=/^\.\/assets\/illustrations\/[a-z0-9-]+-[a-f0-9]{12}\.(svg|png|webp)$/;
function isLocal(value){return typeof value==='string'&&LOCAL.test(value);}
function validUrl(value){
 if(isLocal(value))return true;
 try{const u=new URL(value);return u.protocol==='https:'&&!u.username&&!u.password&&!u.port&&!u.search&&!u.hash&&u.hostname==='raw.githubusercontent.com'&&/^\/hfg-gmuend\/openmoji\/15\.1\.0\/color\/svg\/[A-F0-9-]+\.svg$/.test(u.pathname);}catch(_){return false;}
}
function urlFor(value){return isLocal(value)?new URL(value,root.location?.href||'https://localhost.invalid/').href:value;}
function reviewKey(e){return e?.asset_id&&/^[a-f0-9]{64}$/.test(e.sha256||'')?e.provider+':'+e.asset_id+':'+e.sha256+(e.review_scope?':'+e.review_scope:''):null;}
function decision(e,reviews){const key=reviewKey(e);return key&&reviews&&typeof reviews==='object'&&Object.hasOwn(reviews,key)?reviews[key]:null;}
function candidates(registry,id){
 const raw=registry.candidatesByWordId?.[id],list=Array.isArray(raw)?raw:raw?[raw]:[];
 return list.filter(e=>e.provider!=='ARASAAC'&&PRIORITY.includes(e.provider)&&e.review_status==='needs_manual_review'&&isLocal(e.url)&&reviewKey(e))
  .sort((a,b)=>PRIORITY.indexOf(a.provider)-PRIORITY.indexOf(b.provider));
}
function choose(registry,id,reviews={}){
 const main=registry.byWordId?.[id];
 // A rejected mapping cannot reappear because an old preference or cache exists.
 if(main?.review_status==='approved_by_user'){return main.provider!=='ARASAAC'&&validUrl(main.url)?main:null;}
 return candidates(registry,id).find(e=>e.url!==main?.url&&decision(e,reviews)==='approved')||null;
}
function label(e,reviews){
 if(!e)return 'No verified mapping';
 if(e.review_status==='needs_replacement'||e.review_status==='rejected')return 'Held back / rejected';
 if(e.review_status==='approved_by_user')return 'User-approved';
 const d=decision(e,reviews);return d==='approved'?'Approved on this device':d==='rejected'?'Rejected on this device':'Needs manual review';
}
function info(registry,id,reviews){const e=choose(registry,id,reviews)||candidates(registry,id)[0]||registry.byWordId?.[id];return {source:e?.provider||'None',review:label(e,reviews)};}
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
/* EMBED_REVIEW_GALLERY */
function controls(D,prefs,readOnly,onDecision){
 const $=id=>document.getElementById(id),status=$('pictureCacheStatus');let busy=false,reviewQueue=Promise.resolve();
 const chosen=()=>entries(D.illustrations,prefs().pictureReviews);
 async function report(){try{const c=await count(chosen());status.textContent=c.saved+' / '+c.total+' selected distinct picture files saved. All attached local review pictures are bundled with the offline app. Speech is separate.';}catch(e){status.textContent=e.message;}}
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
 buildGallery(D,prefs,readOnly,onDecision);
}
root.FlyersPictures={candidateRows,filterRows,catalogPayload,reviewPayload,missingRows,choose,validUrl,isLocal,urlFor,reviewKey,decision,candidates,label,info,entries,cached,source,count,saveOne,controls,cacheName:CACHE,providerPriority:PRIORITY};
})(typeof globalThis!=='undefined'?globalThis:this);
