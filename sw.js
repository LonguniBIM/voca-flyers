/* Generated offline shell. No forced activation or database deletion. */
const VERSION="a11a1b4226ae82d0", PATH=new URL(self.registration.scope).pathname;
const PREFIX='rise-voca-flyers-shell:'+PATH+':', CACHE=PREFIX+VERSION;
const FILES=["index.html", "Rise_Voca_Flyers.html", "manifest.webmanifest", "pwa-5a5460da10.js", "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png", "assets/illustrations/toothpaste-e42fdf46dc5e.svg", "assets/illustrations/cupboard-91ff81b87098.svg", "THIRD_PARTY.md", "assets/licenses/Apache-2.0.txt", "assets/licenses/Pictogrammers-LICENSE.txt"].map(p=>new URL(p,self.registration.scope).href);
self.addEventListener('install',event=>{event.waitUntil((async()=>{const c=await caches.open(CACHE);try{for(const u of FILES){const r=await fetch(new Request(u,{cache:'reload'}));if(!r.ok)throw Error('Missing file: '+u);await c.put(u,r);}}catch(e){await caches.delete(CACHE);throw e;}})());});
self.addEventListener('activate',event=>{event.waitUntil((async()=>{for(const k of await caches.keys())if(k.startsWith(PREFIX)&&k!==CACHE)await caches.delete(k);await self.clients.claim();})());});
self.addEventListener('fetch',event=>{const u=new URL(event.request.url);if(event.request.method!=='GET'||u.origin!==self.location.origin)return;
if(FILES.includes(u.href))event.respondWith((async()=>{const c=await caches.open(CACHE);return await c.match(u.href)||fetch(event.request);})());
else if(event.request.mode==='navigate'&&u.pathname.startsWith(PATH))event.respondWith((async()=>{const c=await caches.open(CACHE);return await c.match(new URL('./index.html',self.registration.scope).href)||fetch(event.request);})());});
self.addEventListener('message',event=>{if(event.data?.type!=='CHECK_OFFLINE'||!event.ports[0])return;event.waitUntil((async()=>{const c=await caches.open(CACHE);let ready=true;for(const u of FILES)if(!await c.match(u)){ready=false;break;}event.ports[0].postMessage({type:'OFFLINE_STATUS',ready,version:VERSION});})());});
