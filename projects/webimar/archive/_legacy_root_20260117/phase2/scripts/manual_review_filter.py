#!/usr/bin/env python3
import csv

IN='data/hayvancilik_sadece_yasak_cumleleri.csv'

# Phrases we consider *explicit prohibition*
explicit = [
    'hayvancılık tesisi yapılmasına izin verilmez',
    'hayvancılığa izin verilmez',
    'hayvancılık tesisi yapılamaz',
    'hayvancılık yapılmasına izin verilmez',
    'hayvancılığa izin verilemez',
    'hayvancılık ve tarıma hiçbir şekilde izin verilemez'
]

rows=[]
with open(IN, newline='', encoding='utf-8') as f:
    reader=csv.DictReader(f)
    for r in reader:
        ev=(r.get('evidence_text') or '').lower()
        has_explicit = any(p in ev for p in explicit)
        rows.append((r, has_explicit))

ambiguous=[]
for i,(r,flag) in enumerate(rows):
    if not flag:
        ambiguous.append((i+1,r))

print(f'Total rows: {len(rows)}')
print(f'Ambiguous (no explicit prohibition phrase): {len(ambiguous)}')
print('\n--- AMBIGUOUS SAMPLES ---')
for idx, r in ambiguous[:40]:
    print('\nIndex:', idx)
    print('Province:', r['province'], 'District:', r['district'])
    print('Area type:', r['area_type'])
    print('Source:', r['source_file'])
    s=r['evidence_text']
    snippet = s if len(s) < 400 else s[:400] + '...'
    print('Evidence snippet:', snippet)

# Save ambiguous list to file for manual review
OUT='data/hayvancilik_ambiguous_rows.csv'
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w=csv.writer(f)
    w.writerow(['index','province','district','area_type','evidence_text','source_file'])
    for idx, r in ambiguous:
        w.writerow([idx, r['province'], r['district'], r['area_type'], r['evidence_text'], r['source_file']])

print('\nWrote ambiguous list to', OUT)
print('\nNext: reply with indices to remove or "keep all" to do nothing.')
