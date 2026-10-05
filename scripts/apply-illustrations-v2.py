#!/usr/bin/env python3
"""One-time, guarded migration of the published preview; never reads learner data."""
from pathlib import Path
import base64, hashlib, io, json, re, shutil, urllib.request, zlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'index.html'; original=p.read_text(encoding='utf-8'); s=original
assert hashlib.sha256(s.encode()).hexdigest()=='7730c5408bb13ff3fe1f31af01b3b7361f40ac4d9de5126211db49e5500ab11e', 'Unexpected index revision; review changes before migrating.'
helper=(ROOT/'scripts/illustration-pictures-v2.js').read_text(encoding='utf-8')
assert hashlib.sha256(helper.encode()).hexdigest()=='1b5a696ae7daabfe0d2813f6b3db168250bef3e841f8c1dc7a9a496175502010', 'Unexpected picture helper revision.'
def replace(old,new):
 global s
 assert s.count(old)==1, (old[:100],s.count(old))
 s=s.replace(old,new)
def download(url, expected=None):
 with urllib.request.urlopen(url,timeout=30) as response:
  assert response.status==200; b=response.read(2*1024*1024)
 if expected: assert hashlib.sha256(b).hexdigest()==expected, 'Upstream content hash mismatch: '+url
 return b
m=re.search(r'<script type="application/json" id="appData">(.*?)</script>',s,re.S)
d=json.loads(m[1]);before=json.dumps(d['library'],sort_keys=True);R=d['illustrations'];old=json.dumps(R['byWordId'],sort_keys=True)
R['schema_version']=2
R['provider_priority']=['OpenMoji','Material Symbols','Tabler Icons','Phosphor Icons','Material Design Icons','Streamline']
R['manual_only_providers']=['ARASAAC']
R['notes']='Approved OpenMoji first. Explicit word/sense mappings only, no runtime search. New local images require individual approval on this device. Pictogrammers MDI and Streamline are curated exceptions, not Google Material Symbols. ARASAAC is manual-review only; the two former references are rejected.'
R['rejectedByWordId']={k:{'provider':'ARASAAC','pictogram_id':e['pictogram_id'],'word':e['word'],'review_status':'rejected','reason':'Image unavailable' if e['word']=='toothpaste' else 'Wrong meaning: botanical diagram'} for k,e in R['candidatesByWordId'].items()}
R['candidatesByWordId']={}
assets=ROOT/'assets/illustrations';assets.mkdir(parents=True,exist_ok=True)
specs=[
 ('p03-t1-r19-c2-w1','toothpaste','Streamline','personal-hygiene-clean-toothpaste','Streamline','CC-BY-4.0','https://creativecommons.org/licenses/by/4.0/','https://github.com/webalys-hq/streamline-vectors/blob/52d750c9ce051e51cb181b7a78932120c48541d0/covid/personal-hygiene/personal-hygiene/personal-hygiene-clean-toothpaste.svg','e42fdf46dc5e191b49c48a300eb5ec9d9c5d1314e1271aaece9597e5c01e58e0','A toothpaste tube next to a toothbrush.'),
 ('p03-t1-r06-c1-w1','cupboard','Material Design Icons','cupboard-outline','Pictogrammers contributors','Apache-2.0','https://www.apache.org/licenses/LICENSE-2.0','https://github.com/Templarian/MaterialDesign-SVG/blob/9e04201d4557e729822fb57f62a316c3dea1d4a8/svg/cupboard-outline.svg','91ff81b87098f69f4858a1d8f13013d807fd2843053cb61da152d740905e732f','A cupboard with two upper shelves and two lower doors.')]
for id,word,provider,asset_id,creator,license,license_url,source_url,sha,description in specs:
 url=source_url.replace('https://github.com/','https://raw.githubusercontent.com/').replace('/blob/','/')
 b=download(url,sha)
 assert not re.search(rb'<(?:script|text|foreignObject|image)\b|\bon[a-z]+\s*=|\bhref\s*=|<!DOCTYPE',b,re.I), 'Unsafe SVG content'
 name=word+'-'+sha[:12]+'.svg';(assets/name).write_bytes(b)
 w=next(w for w in d['library']['words'] if w['id']==id);assert w['word']==word
 R['candidatesByWordId'][id]={'word':word,'meaning_vi':w['meaning_vi'],'provider':provider,'asset_id':asset_id,'url':'./assets/illustrations/'+name,'sha256':sha,'creator':creator,'license':license,'license_url':license_url,'source_url':source_url,'download_url':url,'review_status':'needs_manual_review','technical_status':'downloaded_and_hash_verified','visual_description':description,'alt':description,'modifications':'None; original upstream SVG copied unchanged.'}
assert before==json.dumps(d['library'],sort_keys=True)
assert old==json.dumps(R['byWordId'],sort_keys=True)
replace(m[0],'<script type="application/json" id="appData">'+json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+'</script>')
start=s.index('/* Images are a separate cache, never a replacement for learning history. */');end=s.index('</script>',start)
s=s[:start]+helper+s[end:]
replace('<label class="checkline"><input type="checkbox" id="tryArasaac"> Try 2 unreviewed ARASAAC candidates in practice (non-commercial use only)</label>','<p id="picturePolicy">Approved OpenMoji comes first. New local replacements require individual approval below. Old ARASAAC opt-ins are ignored.</p>')
replace('Preview ARASAAC candidates','Review replacement illustrations')
replace('Loading a picture contacts ARASAAC. No learning history is sent. These two candidate URLs still need visual and loading checks.','These two SVGs are bundled with this app, not hotlinked. Preview each actual picture, then approve or reject it. Previewing never creates a learning session. Both old ARASAAC references are rejected.')
replace('tryArasaac:false','pictureReviews:{}')
replace('w.id,preferences.tryArasaac','w.id,preferences.pictureReviews')
replace("status.textContent=entry.creator+' / '+entry.license+(entry.review_status?.startsWith('candidate')?' / UNREVIEWED CANDIDATE':'');","status.textContent='Source: '+entry.provider+' | '+window.FlyersPictures.label(entry,preferences.pictureReviews)+' | '+entry.creator+' / '+entry.license;")
replace("'No meaning-matched illustration is available for this card yet.'","(window.FlyersPictures.candidates(D.illustrations,w.id).length?'A local replacement is available. Review and approve it in Library & source.':'No meaning-matched illustration is available for this card yet.')")
replace("['Word','Source meaning','Topic','Pages','Mode']","['Word','Source meaning','Topic','Pages','Mode','Picture source','Picture review']")
replace("w.mode==='name_dictation'?'Name dictation':'English clue']),'No matching words.'","w.mode==='name_dictation'?'Name dictation':'English clue',window.FlyersPictures.info(D.illustrations,w.id,preferences.pictureReviews).source,window.FlyersPictures.info(D.illustrations,w.id,preferences.pictureReviews).review]),'No matching words.'")
replace("$('tryArasaac').checked=Boolean(preferences.tryArasaac);",'')
replace("$('tryArasaac').addEventListener('change',()=>{preferences.tryArasaac=$('tryArasaac').checked;savePreferences();});window.FlyersPictures.controls(D,()=>preferences,readOnly);","window.FlyersPictures.controls(D,()=>preferences,readOnly,async(key,value)=>{if(readOnly)throw Error('This tab is read-only.');const reviews={...(preferences.pictureReviews&&typeof preferences.pictureReviews==='object'?preferences.pictureReviews:{}),[key]:value};await store.setMeta('preferences',{...preferences,pictureReviews:reviews});preferences.pictureReviews=reviews;renderLibrary();});")
replace("' user-approved OpenMoji mappings; 2 held back; 2 ARASAAC candidates. Pictures are not included offline until saved on this device.'","' user-approved OpenMoji mappings; 2 held back; 2 local replacement pictures awaiting your individual review. OpenMoji pictures need Save pictures for offline; local replacements are cached with the app.'")
replace('OpenMoji artwork: OpenMoji contributors, CC BY-SA 4.0. ARASAAC pictograms: Sergio Palao, owner Government of Aragon, CC BY-NC-SA 4.0. Credits and source links are retained per image. No fonts are bundled.','OpenMoji: CC BY-SA 4.0. Local replacements: <a href="https://www.streamlinehq.com" target="_blank" rel="noopener noreferrer">Streamline</a> (CC BY 4.0) and <a href="https://pictogrammers.com" target="_blank" rel="noopener noreferrer">Pictogrammers Material Design Icons</a> (Apache 2.0). No fonts are bundled.')
replace('Suggested educational pictogram alternative: ARASAAC (check non-commercial and attribution/share-alike conditions). Suggested topic-scene alternative: Storyset (free use requires attribution). Neither is bundled or silently fetched.','Local toothpaste illustration by Streamline, CC BY 4.0; local cupboard-outline by Pictogrammers, Apache 2.0. Original SVGs copied unchanged. <a href="./THIRD_PARTY.md" target="_blank" rel="noopener noreferrer">Credits and licenses</a>. ARASAAC is manual-review only; the former two references are rejected and never loaded.')
replace('</style>','.review-actions{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}.review-actions button{min-height:44px}.picture-source{font-weight:600;overflow-wrap:anywhere}#candidatePreviews img{width:220px;max-width:100%;height:220px;object-fit:contain;background:white;padding:16px;box-sizing:border-box}#candidatePreviews article a{overflow-wrap:anywhere}</style>')
a=re.findall(r'<script>(.*?)</script>',original,re.S);b=re.findall(r'<script>(.*?)</script>',s,re.S)
assert a[:2]==b[:2], 'Gameplay code changed unexpectedly'
assert a[2].split('/* Images are a separate cache, never a replacement for learning history. */')[0]==b[2].split('/* Curated pictures only.')[0], 'History store code changed unexpectedly'
p.write_text(s,encoding='utf-8',newline='\n')
(assets/'manifest.json').write_text(json.dumps({'schema_version':1,'candidates':R['candidatesByWordId'],'rejected':R['rejectedByWordId'],'policy':R['notes']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
png=zlib.decompress(base64.b64decode((ROOT/'scripts/original-app-icon.zlib.b64').read_text()))
assert hashlib.sha256(png).hexdigest()=='cf939e83a95d2ce954eb601ca88b3c87e9a224539035bf1db59cf49abe69e6cf'
icons=ROOT/'icons';icons.mkdir(exist_ok=True);(icons/'icon-512.png').write_bytes(png)
im=Image.open(io.BytesIO(png));assert im.size==(512,512)
for name,size in [('icon-192.png',192),('apple-touch-icon.png',180)]:
 target=icons/name
 if not target.exists():im.resize((size,size),Image.Resampling.LANCZOS).save(target)
licenses=ROOT/'assets/licenses';licenses.mkdir(parents=True,exist_ok=True)
standard=Path('/usr/share/common-licenses/Apache-2.0')
(licenses/'Apache-2.0.txt').write_bytes(standard.read_bytes() if standard.exists() else download('https://www.apache.org/licenses/LICENSE-2.0.txt'))
(licenses/'Pictogrammers-LICENSE.txt').write_bytes(download('https://raw.githubusercontent.com/Templarian/MaterialDesign-SVG/9e04201d4557e729822fb57f62a316c3dea1d4a8/LICENSE'))
info=json.loads((ROOT/'BUILD_INFO.json').read_text())
info.update(release='illustrations-v2',bundled_picture_files=2,pictures='Two local review SVGs cached with app. Original approved OpenMoji images use separate explicit download.',review={'keep':170,'held_back':2,'local_candidates':2,'arasaac_candidates':0,'rejected_arasaac':2})
info['offline_shell_files']+=['assets/illustrations/'+Path(e['url']).name for e in R['candidatesByWordId'].values()]+['THIRD_PARTY.md','assets/licenses/Apache-2.0.txt','assets/licenses/Pictogrammers-LICENSE.txt']
(ROOT/'BUILD_INFO.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8')
(ROOT/'THIRD_PARTY.md').write_text('''# Image credits and licenses

## OpenMoji (unchanged)
OpenMoji contributors, version 15.1.0. CC BY-SA 4.0.
https://openmoji.org / https://creativecommons.org/licenses/by-sa/4.0/
170 approved word/sense mappings, 164 distinct URLs. Truck and Moon stay held back.

## Local toothpaste illustration
Streamline, Covid Icons, personal-hygiene-clean-toothpaste.
https://www.streamlinehq.com / CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
Original SVG copied unchanged: a toothpaste tube beside a toothbrush, not a toothbrush-only substitute.
Pinned upstream commit: 52d750c9ce051e51cb181b7a78932120c48541d0 in webalys-hq/streamline-vectors.

## Local cupboard illustration
Pictogrammers contributors, Material Design Icons, cupboard-outline.
https://pictogrammers.com/library/mdi/icon/cupboard-outline/
Apache 2.0: see assets/licenses/Apache-2.0.txt and Pictogrammers-LICENSE.txt.
This is NOT Google Material Symbols. Original SVG copied unchanged.
Pinned upstream commit: 9e04201d4557e729822fb57f62a316c3dea1d4a8 in Templarian/MaterialDesign-SVG.
Mapped only to the Around The House sense, not the distinct School record.

## Review and provenance
Both local images require individual approval on the device. File hashes and full source URLs are in assets/illustrations/manifest.json. No other provider was silently integrated or automatically searched.
Former ARASAAC toothpaste4197 and cupboard37149 references are rejected; no ARASAAC artwork is bundled or requested. Historical attribution: Sergio Palao, Government of Aragon, ARASAAC, CC BY-NC-SA.
The R application icon comes from the original supplied app; smaller sizes are resized copies. No font files are included. These image licenses do not establish redistribution rights for the supplied word list.
''',encoding='utf-8')
(ROOT/'README.md').write_text('''# Rise Voca Flyers: illustration repair

Open Library & source > Review replacement illustrations. Preview each local picture, then Approve for lessons or Reject / stop using. Approval is stored for the exact asset hash on this device, not in learning history. No image loads from ARASAAC, even with the previous opt-in saved.

OpenMoji remains first. Preferred sourcing order: OpenMoji, Google Material Symbols, Tabler, Phosphor. The two exact local exceptions are Streamline (toothpaste) and Pictogrammers MDI (cupboard). MDI is not Google Material Symbols. The SVGs are included in the offline app; remote OpenMoji pictures still require Save pictures for offline. Not all words have illustrations.

To receive this update, Save & pause, close ALL site/app windows, and reopen. Do NOT clear site data. Keep regular JSON history backups. Sessions, dates, topics, first-correct scoring, hints, skips, audio and resume remain unchanged. History and review preferences are device-local, with no cross-device sync.

The missing PWA icons are restored. The two local SVGs and image licenses are cached with the app. Actual iOS/Android installation and speech still require device testing.

## Maintenance
After editing cached files, run `python scripts/build-offline.py`; verify with `python scripts/build-offline.py --check` and `node --test tests/illustrations.test.cjs`. The apply-illustrations-v2 script is a one-time, guarded migration from the original preview, not a normal build command. Tests use isolated profiles only.

See THIRD_PARTY.md for credits. Never publish learner backups, private reviews, credentials or the original PDF.
''',encoding='utf-8')
setup=ROOT/'GITHUB_PAGES_SETUP.md';text=setup.read_text(encoding='utf-8');text=text.replace('Pictures are NOT bundled in this release.','Two replacement SVGs are bundled; approved OpenMoji pictures need the separate save operation.');setup.write_text(text,encoding='utf-8')
print('Guarded migration complete; 954 original records and all approved mappings preserved. Run build-offline.py and tests before committing.')
