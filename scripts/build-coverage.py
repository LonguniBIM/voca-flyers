#!/usr/bin/env python3
"""Generate transparent image coverage from the canonical content; no learner access."""
from pathlib import Path
from collections import Counter
import argparse,csv,io,json
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
L=json.loads((ROOT/'data/library.json').read_text(encoding='utf-8'));R=json.loads((ROOT/'data/illustrations.json').read_text(encoding='utf-8'))
rows=[]
for w in L['words']:
 main=R['byWordId'].get(w['id'],{});candidate=R['candidatesByWordId'].get(w['id'])
 state='not_applicable' if w['mode']=='name_dictation' else 'approved' if main.get('review_status')=='approved_by_user' else 'needs_manual_review' if candidate else 'missing'
 reason='Proper name: listening dictation, not a pictorial definition.' if state=='not_applicable' else 'No exact candidate selected; a contextual scene or further source research is needed.' if state=='missing' else 'Preview actual picture before approval.' if state=='needs_manual_review' else 'Preserved user-approved OpenMoji mapping.'
 rows.append({'word_id':w['id'],'word':w['word'],'meaning_vi':w['meaning_vi'],'topic_ids':w['topic_ids'],'status':state,'provider':(main if state=='approved' else candidate or {}).get('provider'),'reason':reason})
counts=dict(Counter(e['status'] for e in rows));providers=dict(Counter(e['provider'] for e in R['candidatesByWordId'].values()));used={e['url'][2:] for e in R['candidatesByWordId'].values()}
report={'schema_version':1,'library_fingerprint':L['fingerprint'],'counts':counts,'candidate_providers':providers,'unique_local_picture_files':len(used),'vocabulary_targets':sum(w['mode']!='name_dictation' for w in L['words']),'rows':rows,'download_failures':[]}
output=io.StringIO(newline='');writer=csv.writer(output);writer.writerow(['Word ID','Word','Meaning','Topics','Status','Provider','Reason'])
for e in rows:writer.writerow([e['word_id'],e['word'],e['meaning_vi'],'; '.join(e['topic_ids']),e['status'],e['provider'] or '',e['reason']])
doc=['# Illustration coverage','',f"Library fingerprint: `{L['fingerprint']}`.",'',f"{counts.get('approved',0)} preserved user-approved mappings; {counts.get('needs_manual_review',0)} attached candidates awaiting individual parent review; {counts.get('missing',0)} vocabulary meanings still missing a suitable image; {counts.get('not_applicable',0)} proper names intentionally excluded.",'','Attached does NOT mean parent-approved. Successful image decoding does not establish meaning. Existing private device approvals are not read or published.','',f"{len(used)} distinct local SVG files are bundled. Files are pinned and hash-checked. Previously approved OpenMoji references retain their existing separate offline-download behavior.",'','| Topic | Vocabulary senses | Approved | Attached, needs review | Missing |','|---|---:|---:|---:|---:|']
for t in L['topics']:
 subset=[e for e in rows if t['id'] in e['topic_ids'] and e['status']!='not_applicable'];c=Counter(e['status'] for e in subset)
 if subset:doc.append('| '+str(t.get('title') or t.get('label_en') or t['id'])+' | '+str(len(subset))+' | '+str(c['approved'])+' | '+str(c['needs_manual_review'])+' | '+str(c['missing'])+' |')
doc+=['','A word/sense can belong to multiple topics. Topic row totals therefore overlap; the totals above count each word ID once.','', '## Why words remain missing','No topic-wide placeholder or approximate icon is inserted merely to obtain 100% coverage. Remaining entries include abstract concepts, ambiguous source groupings, calendar names, and concrete objects still needing an exact usable illustration. See data/image-coverage.json or export the missing-word list in the app. Proper names are a separate not-applicable group.','','## Review and export','Open Library & source > Review replacement illustrations. Combine Topic, Source, Review, and word/meaning search. Pages contain 24 candidates. Preview before approving. New approvals are scoped to the exact word ID and asset hash and do not create learning history. Export all image reviews to preserve the review evidence; catalog export excludes those private decisions.','','## Sources','OpenMoji is primary. Pictogrammers Material Design Icons and Mulberry Symbols supply explicit selected exceptions; the existing toothpaste image is Streamline. Pictogrammers MDI is not Google Material Symbols. No ARASAAC images are fetched. See THIRD_PARTY.md and the per-image manifest for original URLs and licenses.']
manifest={'schema_version':2,'candidates':R['candidatesByWordId'],'rejected':R['rejectedByWordId'],'policy':R['notes']}
files={'data/image-coverage.json':(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode(),'data/image-coverage.csv':output.getvalue().encode('utf-8-sig'),'assets/illustrations/manifest.json':(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode(),'docs/IMAGE_COVERAGE.md':('\n'.join(doc)+'\n').encode()}
for name,b in files.items():
 target=ROOT/name
 if a.check:assert target.read_bytes()==b,'Stale coverage: '+name
 else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
info=json.loads((ROOT/'BUILD_INFO.json').read_text(encoding='utf-8'));new={**info,'bundled_picture_files':len(used),'review':{**counts,'candidate_providers':providers}}
new['offline_shell_files']=list(dict.fromkeys([x for x in info['offline_shell_files'] if not x.startswith('assets/illustrations/')]+sorted(used)))
if a.check:assert info==new,'Stale coverage in BUILD_INFO.json'
else:(ROOT/'BUILD_INFO.json').write_text(json.dumps(new,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'counts':counts,'providers':providers,'local_files':len(used)}))
