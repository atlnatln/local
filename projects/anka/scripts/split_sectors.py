#!/usr/bin/env python3
import json

infile = 'data/sectors_bilingual.json'
out_en = 'data/sectors_en.json'
out_tr = 'data/sectors_tr.json'

with open(infile, 'r', encoding='utf-8') as f:
    items = json.load(f)

ens = [i['en'] for i in items]
trs = [i['tr'] for i in items]

with open(out_en, 'w', encoding='utf-8') as f:
    json.dump(ens, f, ensure_ascii=False, indent=2)

with open(out_tr, 'w', encoding='utf-8') as f:
    json.dump(trs, f, ensure_ascii=False, indent=2)

print(f'Wrote {len(ens)} EN and {len(trs)} TR items')