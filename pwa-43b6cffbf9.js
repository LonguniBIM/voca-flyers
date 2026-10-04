/* PWA shell only: no analytics, cloud sync, forced reload or history migration. */
(function(){'use strict';
const $=id=>document.getElementById(id);let promptEvent=null,registration=null;
$('pwaBanner').hidden=false;
function installed(){return matchMedia('(display-mode: standalone)').matches||navigator.standalone===true;}
function installLabel(){if(installed()){$('installApp').hidden=true;return;}if(promptEvent){$('installApp').hidden=false;}else{$('installApp').hidden=true;}}
window.addEventListener('beforeinstallprompt',event=>{event.preventDefault();promptEvent=event;installLabel();});
window.addEventListener('appinstalled',()=>{promptEvent=null;installLabel();});
$('installApp').addEventListener('click',async()=>{if(!promptEvent)return;const p=promptEvent;promptEvent=null;await p.prompt();await p.userChoice;installLabel();});
function updateNote(){if(registration?.waiting)$('pwaUpdateStatus').textContent='An update is ready. Save & pause, then close ALL app windows and browser tabs for this site and reopen. The current lesson will not be reloaded automatically. History is not cleared by this update.';}
function readyStatus(){const controller=navigator.serviceWorker.controller;if(!controller){$('pwaStatus').textContent='Preparing offline app files. Pictures and speech are separate.';return;}const channel=new MessageChannel();channel.port1.onmessage=e=>{const d=e.data;if(d?.type==='OFFLINE_STATUS')$('pwaStatus').textContent=d.ready?(navigator.onLine?'App and vocabulary ready offline. Save pictures separately.':'Offline: app and vocabulary ready; only saved pictures and device voices may work.'):'Offline files are incomplete. Reconnect and reload before relying on offline use.';};controller.postMessage({type:'CHECK_OFFLINE'},[channel.port2]);}
if(!window.isSecureContext||!['https:','http:'].includes(location.protocol)||!('serviceWorker'in navigator)){$('pwaStatus').textContent='Open this PWA from HTTPS (or localhost for computer testing). A local HTML file cannot install the offline app.';return;}
navigator.serviceWorker.register('./sw.js',{scope:'./',updateViaCache:'none'}).then(reg=>{registration=reg;updateNote();reg.addEventListener('updatefound',()=>{const worker=reg.installing;worker?.addEventListener('statechange',()=>{updateNote();if(worker.state==='activated')readyStatus();if(worker.state==='redundant'&&!reg.active)$('pwaStatus').textContent='Offline installation failed. Check the network and host file paths, then reload.';});});readyStatus();}).catch(e=>{$('pwaStatus').textContent='Offline setup failed: '+e.message;});
navigator.serviceWorker.addEventListener('controllerchange',readyStatus);window.addEventListener('online',()=>{readyStatus();registration?.update().catch(()=>{});});window.addEventListener('offline',readyStatus);installLabel();
})();
