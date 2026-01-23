#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_CSV = ROOT / 'data' / 'hayvancilik_restrictions.csv'
OUT_CSV = ROOT / 'data' / 'hayvancilik_restrictions_filtered.csv'
KEEP_TYPES = {'prohibition','application_rejected','conditional_allowed'}

rows=[]
with IN_CSV.open(encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        if r['restriction_type'] not in KEEP_TYPES:
            continue
        # derive province and district heuristically from source_file
        sf = r['source_file']
        base = Path(sf).name
        base = base.replace('.txt','')
        parts = base.split('-')
        province = parts[0].strip() if parts else ''
        district = parts[1].strip() if len(parts)>1 else ''
        # also check header for province-like token (first token before |)
        header = r.get('location_header','')
        if header:
            # take first token that looks like a province name (capitalized or contains 'İl')
            hparts = [p.strip() for p in header.split('|') if p.strip()]
            if hparts:
                # replace if not empty
                if not province and len(hparts[0])>1:
                    province = hparts[0]
        rows.append({
            'province': province,
            'district': district,
            'source_file': r['source_file'],
            'animal_types': r['animal_types'],
            'restriction_type': r['restriction_type'],
            'matched_line': r['matched_line'],
            'context_snippet': r['context_snippet']
        })

OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with OUT_CSV.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['province','district','source_file','animal_types','restriction_type','matched_line','context_snippet'])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print(f"Filtered {len(rows)} restriction records -> {OUT_CSV}")
