#!/usr/bin/env python3
import re
import json

in_en = 'sektorler-ing.md'
in_tr = 'sektörler.md'
out = 'data/sectors_bilingual.json'

def extract_li_text(html):
    items = re.findall(r'<li[^>]*>(.*?)</li>', html, flags=re.S)
    clean = []
    for it in items:
        # remove inner tags like <font ...>
        text = re.sub(r'<[^>]+>', '', it)
        text = text.strip()
        if text:
            clean.append(text)
    return clean

if __name__ == '__main__':
    with open(in_en, 'r', encoding='utf-8') as f:
        en_html = f.read()
    with open(in_tr, 'r', encoding='utf-8') as f:
        tr_html = f.read()

    en = extract_li_text(en_html)
    tr = extract_li_text(tr_html)

    n = min(len(en), len(tr))
    if len(en) != len(tr):
        print(f'Warning: counts differ: en={len(en)} tr={len(tr)}; using {n} items')

    pairs = []
    for i in range(n):
        pairs.append({'en': en[i], 'tr': tr[i]})

    with open(out, 'w', encoding='utf-8') as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)

    print(f'Wrote {len(pairs)} bilingual items to {out}')
