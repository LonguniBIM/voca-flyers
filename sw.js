/* Generated shell: no skipWaiting, no database deletion. */
const VERSION="9cbf9edffcaeb66b", PATH=new URL(self.registration.scope).pathname;
const PREFIX='rise-voca-flyers-shell:'+PATH+':', CACHE=PREFIX+VERSION;
const FILES=["index.html", "Rise_Voca_Flyers.html", "manifest.webmanifest", "pwa-5a5460da10.js", "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png"].map(p=>new URL(p,self.registration.scope).href);
self.addEventListener('install',event=>{event.waitUntil((async()=>{const cache=await caches.open(CACHE);try{for(const url of FILES){const r=await fetch(new Request(url,{cache:'reload'}));if(!r.ok)throw Error('Missing shell file: '+url);await cache.put(url,r);}}catch(e){await caches.delete(CACHE);throw e;}})());});
self.addEventListener('activate',event=>{event.waitUntil((async()=>{for(const key of await caches.keys())if(key.startsWith(PREFIX)&&key!==CACHE)await caches.delete(key);await self.clients.claim();})());});
self.addEventListener('fetch',event=>{const u=new URL(event.request.url);if(event.request.method!=='GET'||u.origin!==self.location.origin)return;
const shellUrl=new URL('./index.html',self.registration.scope).href;
if(event.request.mode==='navigate'&&u.pathname.startsWith(PATH))event.respondWith((async()=>{const cache=await caches.open(CACHE);return await cache.match(shellUrl)||fetch(event.request);})());
else if(FILES.includes(u.href))event.respondWith((async()=>{const cache=await caches.open(CACHE);return await cache.match(u.href)||fetch(event.request);})());});
self.addEventListener('message',event=>{if(event.data?.type!=='CHECK_OFFLINE'||!event.ports[0])return;event.waitUntil((async()=>{const cache=await caches.open(CACHE);let ready=true;for(const url of FILES)if(!await cache.match(url)){ready=false;break;}event.ports[0].postMessage({type:'OFFLINE_STATUS',ready,version:VERSION});})());});
