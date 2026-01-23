#!/usr/bin/env python3
import re
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / 'data' / 'hayvancilik_restrictions.csv'
KEYWORDS = [
    'hayvancılık', 'hayvancılığa', 'hayvancılık tesisi', 'hayvan', 'büyükbaş', 'küçükbaş',
    'kanatlı', 'tavuk', 'Toprak Koruma Kurul', 'su kısıt', 'ret edil', 'izin verilmez',
    'izin verilemez', 'yapılmasına izin verilmez', 'yapılamaz', 'ret edilecek', 'ret edilece'
]
KW_RE = re.compile('|'.join(re.escape(k) for k in KEYWORDS), re.IGNORECASE)
ANIMALS = ['büyükbaş','küçükbaş','kanatlı','tavuk','kümes','ahır','besicilik']

rows = []
for txt in ROOT.rglob('*.txt'):
    try:
        text = txt.read_text(encoding='utf-8')
    except Exception:
        continue
    # header (first 6 non-empty lines)
    header = [l.strip() for l in text.splitlines() if l.strip()][:6]
    header_text = ' | '.join(header)
    for i, line in enumerate(text.splitlines()):
        if KW_RE.search(line):
            # collect context (the sentence or +/-2 lines)
            start = max(0, i-2)
            end = min(i+3, len(text.splitlines()))
            snippet = '\n'.join(text.splitlines()[start:end]).strip()
            # detect animals
            found_animals = sorted({a for a in ANIMALS if re.search(r'\b'+re.escape(a)+r'\b', snippet, re.IGNORECASE)})
            animal_field = ';'.join(found_animals) if found_animals else 'general'
            # determine restriction type
            s = snippet.lower()
            if 'izin verilmez' in s or 'yapılmasına izin verilmez' in s or 'yapılamaz' in s or 'hiçbir şekilde izin verilemez' in s:
                restriction = 'prohibition'
            elif 'ret' in s:
                restriction = 'application_rejected'
            elif 'izin verilebilir' in s or 'yapılabilir' in s or 'artırılabilir' in s:
                restriction = 'conditional_allowed'
            else:
                restriction = 'other'
            rows.append({
                'source_file': str(txt.relative_to(ROOT)),
                'location_header': header_text,
                'matched_line': line.strip(),
                'context_snippet': snippet,
                'animal_types': animal_field,
                'restriction_type': restriction
            })

# write CSV
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with OUT_CSV.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['source_file','location_header','animal_types','restriction_type','matched_line','context_snippet'])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print(f"Extracted {len(rows)} records -> {OUT_CSV}")
