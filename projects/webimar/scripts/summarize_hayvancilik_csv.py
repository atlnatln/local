#!/usr/bin/env python3
import csv
from collections import defaultdict

inpath = 'data/hayvancilik_restrictions_structured.csv'
out_big = 'data/buyukbas_bans.csv'
out_general = 'data/hayvancilik_bans.csv'

rows = []
with open(inpath, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

# General hayvancilik bans: any restricted_* == 'evet' OR evidence contains 'hayvancılık tesisi yapılmasına izin verilmez' or 'hayvancılık ve' 'hayvancılığa izin verilmez'
general = []
big = []

for r in rows:
    flags = [r.get(k, '').strip().lower() == 'evet' for k in r.keys() if k.startswith('restricted_')]
    evidence = (r.get('evidence_text') or '').lower()
    is_general = any(flags) or 'hayvancılık tesisi yapılmasına izin verilmez' in evidence or 'hayvancılığa izin verilmez' in evidence or 'hayvancılık ve' in evidence and 'izin verilmez' in evidence
    is_big = (r.get('restricted_besi_sigir','').strip().lower() == 'evet') or (r.get('restricted_sut_sigir','').strip().lower() == 'evet') or 'büyükbaş' in evidence or 'büyükbaş' in (r.get('note') or '')
    if is_general:
        general.append(r)
    if is_big:
        big.append(r)

# write unique province-district lists

def unique_pd(list_of_rows):
    s = set()
    for r in list_of_rows:
        prov = r.get('province','').strip()
        dist = r.get('district','').strip()
        s.add((prov, dist))
    return sorted(s)

unique_general = unique_pd(general)
unique_big = unique_pd(big)

with open(out_general, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['province','district','area_type','evidence_text','source_file'])
    for r in general:
        writer.writerow([r['province'], r['district'], r['area_type'], r['evidence_text'], r['source_file']])

with open(out_big, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['province','district','area_type','evidence_text','source_file'])
    for r in big:
        writer.writerow([r['province'], r['district'], r['area_type'], r['evidence_text'], r['source_file']])

# Print short summary
print(f'Rows total: {len(rows)}')
print(f'General hayvancılık bans (rows): {len(general)}, unique (province,district): {len(unique_general)}')
print(f'Büyükbaş bans (rows): {len(big)}, unique (province,district): {len(unique_big)}')

print('\nUnique provinces/districts with general hayvancılık bans:')
for p,d in unique_general[:200]:
    print(f'- {p} / {d or "(il geneli)"}')

print('\nUnique provinces/districts with büyükbaş bans:')
for p,d in unique_big[:200]:
    print(f'- {p} / {d or "(il geneli)"}')
