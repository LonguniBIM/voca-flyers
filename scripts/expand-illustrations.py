#!/usr/bin/env python3
"""Apply explicit meaning-level image mappings; never edit the vocabulary or learner DB."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse, csv, hashlib, io, json, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(); p.add_argument('--cache', required=True); args = p.parse_args()
cache = Path(args.cache); cache.mkdir(parents=True, exist_ok=True)
htmlpath = ROOT/'index.html'; html = htmlpath.read_text(encoding='utf-8')
match = re.search(r'(<script type="application/json" id="appData">)(.*?)(</script>)', html, re.S)
D = json.loads(match[2]); R = D['illustrations']; words = D['library']['words']
original_library = json.dumps(D['library'], sort_keys=True, ensure_ascii=False)
original_approved = json.dumps(R['byWordId'], sort_keys=True, ensure_ascii=False)
PROVIDERS = {
 'OpenMoji': ('hfg-gmuend/openmoji', '15.1.0', 'color/svg/', 'OpenMoji contributors', 'CC-BY-SA-4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'),
 'MDI': ('Templarian/MaterialDesign-SVG', '9e04201d4557e729822fb57f62a316c3dea1d4a8', 'svg/', 'Pictogrammers contributors', 'Apache-2.0', 'https://www.apache.org/licenses/LICENSE-2.0'),
 'Mulberry': ('mulberrysymbols/mulberry-symbols', '9cbab9f400c5de44e2bc58839cca07294aadb086', '', 'Steve Lee / Mulberry Symbols', 'CC-BY-SA-4.0', 'https://creativecommons.org/licenses/by-sa/4.0/')
}
def safe_svg(raw):
 if len(raw)>1000000 or not raw: raise ValueError('Image size outside limits')
 if re.search(rb'<!DOCTYPE|<!ENTITY|<\s*(?:script|foreignObject|image|text)\b|\bon\w+\s*=', raw, re.I): raise ValueError('SVG contains unsupported active, external or text content')
 xml=ET.fromstring(raw)
 if xml.tag.rsplit('}',1)[-1]!='svg':raise ValueError('Not an SVG')
 for node in xml.iter():
  for k,v in node.attrib.items():
   if k.rsplit('}',1)[-1] in ['href','src'] and not v.startswith('#'):raise ValueError('External SVG reference')
   if re.search(r'url\(\s*[\"\']?(?!#)[^)]',v,re.I):raise ValueError('External style reference')
 return raw
specs=[]
for line in (ROOT/'scripts/image-expansion-map.tsv').read_text(encoding='utf-8').splitlines():
 if not line.strip() or line.startswith('#'):continue
 topic, names, provider, key = [x.strip() for x in line.split('\t')]
 assert provider in PROVIDERS, provider
 for name in names.split('|'):
  found=[w for w in words if w['word']==name and topic in w['topic_ids']]
  assert len(found)==1, (topic,name,len(found))
  w=found[0]
  if R['byWordId'].get(w['id'],{}).get('review_status')=='approved_by_user':continue
  specs.append((w,provider,key))
assert len({s[0]['id'] for s in specs})==len(specs), 'Duplicate per-sense mapping'
assets=ROOT/'assets/illustrations';assets.mkdir(parents=True,exist_ok=True)
def fetch_asset(spec):
 _,provider,key=spec;repo,version,prefix,creator,license,licenseurl=PROVIDERS[provider]
 path=prefix+key+('' if key.endswith('.svg') else '.svg'); quoted=urllib.parse.quote(path,safe='/')
 url='https://raw.githubusercontent.com/'+repo+'/'+version+'/'+quoted
 cached=cache/(hashlib.sha256(url.encode()).hexdigest()+'.svg')
 if cached.exists():raw=cached.read_bytes()
 else:
  req=urllib.request.Request(url,headers={'User-Agent':'RiseVoca-AssetBuild/1.0'})
  with urllib.request.urlopen(req,timeout=25) as response:
   if response.status!=200:raise ValueError('HTTP '+str(response.status))
   raw=response.read(1000001)
  safe_svg(raw);cached.write_bytes(raw)
 safe_svg(raw);sha=hashlib.sha256(raw).hexdigest()
 slug=re.sub(r'[^a-z0-9]+','-',Path(key).stem.lower()).strip('-')[:80]
 name=provider.lower()+'-'+slug+'-'+sha[:12]+'.svg';(assets/name).write_bytes(raw)
 return {'provider':'Material Design Icons' if provider=='MDI' else 'Mulberry Symbols' if provider=='Mulberry' else provider,'asset_id':key,'url':'./assets/illustrations/'+name,'sha256':sha,'creator':creator,'license':license,'license_url':licenseurl,'source_url':'https://github.com/'+repo+'/blob/'+version+'/'+quoted,'download_url':url,'version':version,'technical_status':'downloaded_and_hash_verified','modifications':'None; original upstream SVG copied unchanged.'}
unique={(pr,k):(w,pr,k) for w,pr,k in specs};results={};failures={}
with ThreadPoolExecutor(max_workers=6) as pool:
 jobs={pool.submit(fetch_asset,s):(s[1],s[2]) for s in unique.values()}
 for i,future in enumerate(as_completed(jobs),1):
  key=jobs[future]
  try:results[key]=future.result()
  except Exception as exc:failures[key]=str(exc)
  if i%30==0 or i==len(jobs):print('Assets checked',i,'/',len(jobs),'failed',len(failures),flush=True)
if failures:
 raise RuntimeError('Asset download/validation failed; catalog was not changed: '+repr(failures))
additions=0
for w,provider,key in specs:
 if (provider,key) not in results:continue
 entry={**results[(provider,key)],'word':w['word'],'word_id':w['id'],'meaning_vi':w['meaning_vi'],'topic_ids':w['topic_ids'],'review_scope':w['id'],'review_status':'needs_manual_review','visual_description':('Source symbol: '+Path(key).stem.replace('-',' ').replace('_',' ')+'. Check against the exact word meaning shown above.'),'alt':'Illustration to review for '+w['word']}
 # Re-run preserves any historical entry; only this explicitly mapped candidate is refreshed.
 R['candidatesByWordId'][w['id']]=entry;additions+=1
if any(e['provider']=='Mulberry Symbols' for e in R['candidatesByWordId'].values()) and 'Mulberry Symbols' not in R['provider_priority']:R['provider_priority'].append('Mulberry Symbols')
R['schema_version']=3
R['notes']='Preserve approved OpenMoji first. All additions are explicit word/sense mappings with downloaded, pinned local SVGs. Parent review is required; a provider label or successful HTTP response is not semantic approval. ARASAAC remains excluded. Unmapped targets remain visible as missing; no generic topic image is substituted.'
assert json.dumps(D['library'],sort_keys=True,ensure_ascii=False)==original_library
assert json.dumps(R['byWordId'],sort_keys=True,ensure_ascii=False)==original_approved
html=html[:match.start(2)]+json.dumps(D,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[match.end(2):]
htmlpath.write_text(html,encoding='utf-8',newline='\n')
data=ROOT/'data';data.mkdir(exist_ok=True)
(data/'library.json').write_text(json.dumps(D['library'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
(data/'illustrations.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
(assets/'manifest.json').write_text(json.dumps({'schema_version':2,'candidates':R['candidatesByWordId'],'rejected':R['rejectedByWordId'],'policy':R['notes']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
coverage=[]
for w in words:
 main=R['byWordId'].get(w['id'],{});candidate=R['candidatesByWordId'].get(w['id'])
 status='not_applicable' if w['mode']=='name_dictation' else 'approved' if main.get('review_status')=='approved_by_user' else 'needs_manual_review' if candidate else 'missing'
 reason='Proper name: listening dictation, not a pictorial definition.' if status=='not_applicable' else 'No exact candidate selected; a contextual scene or further source research is needed.' if status=='missing' else 'Preview actual picture before approval.' if status=='needs_manual_review' else 'Preserved user-approved OpenMoji mapping.'
 coverage.append({'word_id':w['id'],'word':w['word'],'meaning_vi':w['meaning_vi'],'topic_ids':w['topic_ids'],'status':status,'provider':(main if status=='approved' else candidate or {}).get('provider'),'reason':reason})
from collections import Counter
stats=dict(Counter(x['status'] for x in coverage)); providers=dict(Counter(e['provider'] for e in R['candidatesByWordId'].values()))
report={'schema_version':1,'library_fingerprint':D['library']['fingerprint'],'counts':stats,'candidate_providers':providers,'unique_local_picture_files':len(set(e['url'] for e in R['candidatesByWordId'].values())),'vocabulary_targets':sum(w['mode']!='name_dictation' for w in words),'rows':coverage,'download_failures':[{'provider':k[0],'key':k[1],'error':v} for k,v in failures.items()]}
(data/'image-coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
output=io.StringIO(newline='');writer=csv.writer(output);writer.writerow(['Word ID','Word','Meaning','Topics','Status','Provider','Reason'])
for e in coverage:writer.writerow([e['word_id'],e['word'],e['meaning_vi'],'; '.join(e['topic_ids']),e['status'],e['provider'] or '',e['reason']])
(data/'image-coverage.csv').write_text(output.getvalue(),encoding='utf-8-sig',newline='')
info=json.loads((ROOT/'BUILD_INFO.json').read_text());info.update(release='illustrations-v3',bundled_picture_files=report['unique_local_picture_files'],review={**stats,'candidate_providers':providers},pictures='Curated local candidates are cached with the app. New candidates require parent approval. Original OpenMoji references retain separate explicit offline download.')
info['offline_shell_files']=list(dict.fromkeys(info['offline_shell_files']+['data/library.json','data/illustrations.json','data/image-coverage.json']+[e['url'][2:] for e in R['candidatesByWordId'].values()]))
(ROOT/'BUILD_INFO.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'added_mappings':additions,'counts':stats,'providers':providers,'failures':report['download_failures']},indent=2),flush=True)
