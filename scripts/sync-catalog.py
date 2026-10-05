#!/usr/bin/env python3
"""Keep exportable JSON catalogs and the offline inline copy identical."""
from pathlib import Path
import argparse,json,re
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
path=ROOT/'index.html';s=path.read_text(encoding='utf-8');m=re.search(r'(<script type="application/json" id="appData">)(.*?)(</script>)',s,re.S);D=json.loads(m[2])
library=json.loads((ROOT/'data/library.json').read_text(encoding='utf-8'));images=json.loads((ROOT/'data/illustrations.json').read_text(encoding='utf-8'))
ids=[w['id'] for w in library['words']];assert len(ids)==len(set(ids));assert set(images['candidatesByWordId']).issubset(ids)
helper=(ROOT/'scripts/illustration-pictures-v2.js').read_text(encoding='utf-8');gallery=(ROOT/'scripts/image-review-gallery.js').read_text(encoding='utf-8');assert helper.count('/* EMBED_REVIEW_GALLERY */')==1;helper=helper.replace('/* EMBED_REVIEW_GALLERY */',gallery)
start=s.index('/* Curated pictures only.');end=s.index('</script>',start)
if a.check:
 assert D['library']==library and D['illustrations']==images,'Inline catalog differs from exportable JSON'
 assert s[start:end]==helper,'Embedded image module is stale'
else:
 s=s[:start]+helper+s[end:];m=re.search(r'(<script type="application/json" id="appData">)(.*?)(</script>)',s,re.S)
 D['library']=library;D['illustrations']=images;s=s[:m.start(2)]+json.dumps(D,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+s[m.end(2):]
 path.write_text(s,encoding='utf-8',newline='\n')
print('Catalog and image module', 'verified' if a.check else 'synchronized',':',len(ids),'records')
