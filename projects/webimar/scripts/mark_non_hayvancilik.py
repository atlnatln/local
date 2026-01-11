#!/usr/bin/env python3
import csv

IN='data/hayvancilik_sadece_yasak_cumleleri.csv'
OUT='data/hayvancilik_sadece_yasak_cumleleri_review.csv'

rows=[]
with open(IN,newline='',encoding='utf-8') as f:
    r=csv.DictReader(f)
    for i,row in enumerate(r, start=1):
        ev=(row.get('evidence_text') or '').lower()
        has_hayvancil = 'hayvanc' in ev
        rows.append((i,row,has_hayvancil))

with open(OUT,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f)
    w.writerow(['index','province','district','area_type','has_hayvancil','evidence_snippet','source_file'])
    for i,row,has in rows:
        s=row.get('evidence_text','')
        snippet = s if len(s) < 300 else s[:300] + '...'
        w.writerow([i,row.get('province',''),row.get('district',''),row.get('area_type',''), 'yes' if has else 'no', snippet, row.get('source_file','')])

print('Reviewed', len(rows), 'rows. Marked', sum(not has for _,_,has in rows), 'suspect rows (no "hayvanc" in evidence).')
print('Wrote', OUT)
