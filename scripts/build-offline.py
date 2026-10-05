#!/usr/bin/env python3
"""Regenerate the offline version without modifying learner storage."""
from pathlib import Path
import argparse,hashlib,json,re
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
info=json.loads((root/'BUILD_INFO.json').read_text());files=info['offline_shell_files']
assert len(files)==len(set(files))
h=hashlib.sha256(Path(__file__).read_bytes())
for name in sorted(files):
 f=root/name;assert f.is_file() and f.resolve().is_relative_to(root.resolve()),name
 h.update(name.encode()+b'\0'+f.read_bytes()+b'\0')
version=h.hexdigest()[:16]
sw='''/* Generated offline shell. No forced activation or database deletion. */
const VERSION=__VERSION__, PATH=new URL(self.registration.scope).pathname;
const PREFIX='rise-voca-flyers-shell:'+PATH+':', CACHE=PREFIX+VERSION;
const FILES=__FILES__.map(p=>new URL(p,self.registration.scope).href);
self.addEventListener('install',event=>{event.waitUntil((async()=>{const c=await caches.open(CACHE);let next=0;async function worker(){while(next<FILES.length){const u=FILES[next++];const r=await fetch(new Request(u,{cache:'reload'}));if(!r.ok)throw Error('Missing file: '+u);await c.put(u,r);}}const results=await Promise.allSettled(Array.from({length:Math.min(6,FILES.length)},worker));const failed=results.find(r=>r.status==='rejected');if(failed){await caches.delete(CACHE);throw failed.reason;}})());});
self.addEventListener('activate',event=>{event.waitUntil((async()=>{for(const k of await caches.keys())if(k.startsWith(PREFIX)&&k!==CACHE)await caches.delete(k);await self.clients.claim();})());});
self.addEventListener('fetch',event=>{const u=new URL(event.request.url);if(event.request.method!=='GET'||u.origin!==self.location.origin)return;
if(FILES.includes(u.href))event.respondWith((async()=>{const c=await caches.open(CACHE);return await c.match(u.href)||fetch(event.request);})());
else if(event.request.mode==='navigate'&&u.pathname.startsWith(PATH))event.respondWith((async()=>{const c=await caches.open(CACHE);return await c.match(new URL('./index.html',self.registration.scope).href)||fetch(event.request);})());});
self.addEventListener('message',event=>{if(event.data?.type!=='CHECK_OFFLINE'||!event.ports[0])return;event.waitUntil((async()=>{const c=await caches.open(CACHE);let ready=true;for(const u of FILES)if(!await c.match(u)){ready=false;break;}event.ports[0].postMessage({type:'OFFLINE_STATUS',ready,version:VERSION});})());});
'''.replace('__VERSION__',json.dumps(version)).replace('__FILES__',json.dumps(files))
if a.check:assert info['version']==version and (root/'sw.js').read_text()==sw,'Offline build is stale'
else:
 info['version']=version;(root/'BUILD_INFO.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8',newline='\n');(root/'sw.js').write_text(sw,encoding='utf-8',newline='\n')
print('Offline build',version,':',len(files),'files verified')
