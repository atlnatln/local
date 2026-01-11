#!/usr/bin/env python3
import csv
from collections import OrderedDict

IN='data/hayvancilik_restrictions_structured.csv'
OUT='data/hayvancilik_sadece_yasak_cumleleri.csv'
OUT_TXT='data/hayvancilik_yasak_cumleleri_unique.txt'

phrases = [
    'hayvancılığa izin verilmez',
    'hayvancılık tesisi yapılmasına izin verilmez',
    'hayvancılık tesisi yapılamaz',
    'hayvancılık yapılmasına izin verilmez',
    'hayvancılığa izin verilemez'
]

found=[]
unique_sentences=OrderedDict()

with open(IN, newline='', encoding='utf-8') as f:
    reader=csv.DictReader(f)
    for r in reader:
        evidence=(r.get('evidence_text') or '').lower()
        if any(p in evidence for p in phrases):
            found.append({
                'province': r.get('province',''),
                'district': r.get('district',''),
                'area_type': r.get('area_type',''),
                'evidence_text': r.get('evidence_text',''),
                'source_file': r.get('source_file',''),
                'source_line': r.get('source_line','')
            })
            unique_sentences[evidence.strip()]=True

# write CSV
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    writer=csv.DictWriter(f, fieldnames=['province','district','area_type','evidence_text','source_file','source_line'])
    writer.writeheader()
    for r in found:
        writer.writerow(r)

# write unique sentences
with open(OUT_TXT, 'w', encoding='utf-8') as f:
    for s in unique_sentences.keys():
        f.write(s + '\n')

print(f'Found rows: {len(found)}')
print(f'Unique sentences: {len(unique_sentences)}')
print('Wrote:', OUT, OUT_TXT)
