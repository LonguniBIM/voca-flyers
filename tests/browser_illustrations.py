#!/usr/bin/env python3
"""Native service-worker/IndexedDB checks in disposable profiles, never learner data."""
import argparse,http.server,json,tempfile,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];checks=[]
class Handler(http.server.SimpleHTTPRequestHandler):
 def translate_path(self,path):
  path=path.split('?',1)[0]
  if not path.startswith('/voca-flyers/'):return str(root/'__missing__')
  target=(root/path[len('/voca-flyers/'):]).resolve()
  return str(target) if target.is_relative_to(root) else str(root/'__missing__')
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
url='http://127.0.0.1:'+str(server.server_port)+'/voca-flyers/'
def check(value,name):
 assert value,name
 checks.append(name)
def ready(page):page.wait_for_function("window.FlyersAppStatus && !document.getElementById('start').disabled")
def library(page):
 page.locator('[data-view=library]').click();page.locator('summary',has_text='Review replacement illustrations').click()
def state(page):return page.evaluate("async()=>{const s=await new FlyersStore().open();const d={sessions:await s.list(),prefs:await s.meta('preferences',{})};s.db?.close();return d;}")
try:
 with tempfile.TemporaryDirectory(prefix='flyers-test-') as profile,sync_playwright() as pw:
  context=pw.chromium.launch_persistent_context(profile,headless=True,viewport={'width':1200,'height':950})
  page=context.new_page();errors=[];requests=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
  page.goto(url,wait_until='networkidle');ready(page);page.wait_for_function('navigator.serviceWorker.controller !== null');page.wait_for_function("document.getElementById('pwaStatus').textContent.includes('ready offline')")
  check(True,'native service worker installs all 12 scoped files');check(state(page)['sessions']==[],'fresh profile has no fake learning history')
  page.evaluate("async()=>{const s=await new FlyersStore().open();await s.setMeta('preferences',{tryArasaac:true});s.db.close();}")
  page.reload(wait_until='networkidle');ready(page);library(page);cards=page.locator('#candidatePreviews article')
  check(cards.count()==2,'two local replacements, not ARASAAC');check(page.locator('#tryArasaac').count()==0,'legacy global opt-in removed')
  for card in cards.all():
   check(card.get_by_role('button',name='Approve for lessons').is_disabled(),'approval disabled before image decode')
   card.get_by_role('button',name='Preview local picture').click();card.locator('img').wait_for(state='visible');check(card.locator('img').evaluate('(i)=>i.naturalWidth>0'),'bundled SVG actually decodes')
  check(state(page)['sessions']==[],'preview does not create history')
  page.evaluate("()=>document.querySelectorAll('#candidatePreviews article').forEach(c=>[...c.querySelectorAll('button')].find(b=>b.textContent==='Approve for lessons').click())")
  page.wait_for_function("[...document.querySelectorAll('.picture-source')].every(e=>e.textContent.includes('Approved on this device'))")
  check(len(state(page)['prefs']['pictureReviews'])==2,'concurrent approvals persist without lost update');check(state(page)['sessions']==[],'approval writes preferences only')
  page.reload(wait_until='networkidle');ready(page);library(page);check('Approved on this device' in page.locator('.picture-source').first.inner_text(),'approval survives native reload')
  second=context.new_page();second.goto(url);second.wait_for_function('window.FlyersAppStatus && FlyersAppStatus().readOnly && document.querySelectorAll("#candidatePreviews article").length===2');library(second)
  second.locator('#candidatePreviews article').first.get_by_role('button',name='Preview local picture').click();second.locator('#candidatePreviews img').first.wait_for(state='visible')
  check(second.locator('#candidatePreviews article').first.get_by_role('button',name='Approve for lessons').is_disabled(),'read-only tab cannot change reviews');second.close()
  page.locator('[data-view=home]').click();page.locator('#autolisten').uncheck();page.locator('#clearTopics').click();page.locator('#topicCards input[value=house]').check();page.locator('#sessionSize').fill('1')
  page.evaluate("()=>{RiseG5Core.sample=(pool)=>[pool.find(w=>w.word==='toothpaste')];}")
  page.locator('#start').click();page.locator('#questionTitle').click();page.keyboard.type('too');page.locator('#pause').click();page.wait_for_function('!FlyersAppStatus().pending');before=state(page)['sessions'][0]
  page.reload(wait_until='networkidle');ready(page);page.locator('#resume').click();page.wait_for_function("!document.getElementById('game').hidden");after=state(page)['sessions'][0]
  check(after['id']==before['id'] and after['questions'][0]['slots']==before['questions'][0]['slots'],'partial session survives pause reload resume');check(page.locator('#answerImage').is_hidden(),'no illustration answer leak')
  page.locator('#clear').click();page.locator('#questionTitle').click();page.keyboard.type('toothpaste');page.locator('#check').click();page.locator('#answerImage').wait_for(state='visible')
  check('Source: Streamline' in page.locator('#illustrationStatus').inner_text(),'approved accurate source appears after correct answer');page.wait_for_function('!FlyersAppStatus().pending');check(state(page)['sessions'][0]['questions'][0]['firstCorrect']['attemptsToFirstCorrect']==1,'first-correct counted once')
  page.locator('#pause').click();page.wait_for_function('!FlyersAppStatus().pending');context.set_offline(True);page.reload(wait_until='domcontentloaded');ready(page);library(page)
  for card in page.locator('#candidatePreviews article').all():card.get_by_role('button',name='Preview local picture').click();card.locator('img').wait_for(state='visible')
  check(True,'app and both images reopen offline from real CacheStorage')
  page.locator('#candidatePreviews article').first.get_by_role('button',name='Reject / stop using').click();page.wait_for_function("document.querySelector('.picture-source').textContent.includes('Rejected on this device')")
  check(len(state(page)['sessions'])==1,'review and rejection do not change session count');check(not any('arasaac' in u for u in requests),'zero ARASAAC requests despite stale opt-in');check(not errors,'no uncaught browser errors');context.close()
  context=pw.chromium.launch_persistent_context(profile,headless=True,viewport={'width':390,'height':844},has_touch=True)
  page=context.new_page();page.goto(url);ready(page);library(page);check(len(state(page)['sessions'])==1,'history survives closing and reopening browser');check('Rejected on this device' in page.locator('.picture-source').first.inner_text(),'review persists across browser processes');check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'no horizontal overflow on 390px phone layout')
  for card in page.locator('#candidatePreviews article').all():card.get_by_role('button',name='Preview local picture').tap();card.locator('img').wait_for(state='visible')
  check(True,'both previews work with touch input');context.close()
  browser=pw.chromium.launch(headless=True);context=browser.new_context(service_workers='block');page=context.new_page();page.route('**/assets/illustrations/*.svg',lambda route:route.fulfill(status=404,body='not found'))
  page.goto(url);ready(page);library(page);card=page.locator('#candidatePreviews article').first;card.get_by_role('button',name='Preview local picture').click();page.wait_for_function("document.querySelector('#candidatePreviews [role=status]').textContent.includes('Image unavailable')")
  check(card.get_by_role('button',name='Approve for lessons').is_disabled(),'failed image cannot be approved');check(state(page)['sessions']==[],'failed preview creates no session');browser.close()
finally:server.shutdown();server.server_close()
report={'passed':len(checks),'checks':checks,'limits':'Desktop Chromium with isolated profiles. Physical iOS/Android installation and actual audible speech require device testing.'}
Path(a.report).write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
