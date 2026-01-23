#!/usr/bin/env python3
import csv
import re

IN='data/hayvancilik_sadece_yasak_cumleleri.csv'
OUT='data/hayvancilik_sadece_yasak_cumleleri_with_madde.csv'
OUT_UNIQUE='data/hayvancilik_yasak_cumleleri_unique_with_madde.txt'

proh_patterns = [
    r'hayvancılık tesisi yapılmasına izin verilmez',
    r'hayvancılığa izin verilmez',
    r'hayvancılık tesisi yapılamaz',
    r'hayvancılık yapılmasına izin verilmez',
    r'hayvancılığa izin verilemez'
]
proh_re = re.compile(r'(' + r'|'.join(proh_patterns) + r')', re.I)
num_re = re.compile(r'(\d+(?:\.\d+)*\.)')

rows=[]
unique=set()
failed=[]

with open(IN, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        ev = r.get('evidence_text','')
        ev_low = ev.lower()
        m = proh_re.search(ev_low)
        sentence=''
        madde=''
        if m:
            # extract sentence by splitting on sentence punctuation
            # find the span of match in original text (case-insensitive)
            start, end = m.start(), m.end()
            # find sentence boundaries around start/end
            # work on original ev to preserve case
            s = ev
            # find preceding sentence start (nearest preceding dot or line start)
            prev_dot = s.rfind('.', 0, start)
            prev_q = s.rfind('?', 0, start)
            prev_ex = s.rfind('!', 0, start)
            prev = max(prev_dot, prev_q, prev_ex)
            sent_start = prev+1 if prev != -1 else 0
            # find next sentence end
            next_dot = s.find('.', end)
            next_q = s.find('?', end)
            next_ex = s.find('!', end)
            candidates = [x for x in (next_dot, next_q, next_ex) if x != -1]
            sent_end = min(candidates) if candidates else len(s)
            sentence = s[sent_start:sent_end+1].strip()
            # attempt to get the madde number by looking left from sent_start
            left_context = s[:sent_start]
            nums = list(num_re.finditer(left_context))
            if nums:
                madde = nums[-1].group(1)
            else:
                # try to find number inside sentence
                nums2 = list(num_re.finditer(sentence))
                if nums2:
                    madde = nums2[0].group(1)
        else:
            failed.append(r)
        if sentence:
            unique.add((sentence.strip(), madde))
        rows.append({
            'province': r.get('province',''),
            'district': r.get('district',''),
            'area_type': r.get('area_type',''),
            'prohibition_sentence': sentence,
            'madde_numarasi': madde,
            'source_file': r.get('source_file','')
        })

# write new CSV
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    fieldnames=['province','district','area_type','prohibition_sentence','madde_numarasi','source_file']
    w=csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow(r)

# write unique sentences with madde
with open(OUT_UNIQUE, 'w', encoding='utf-8') as f:
    for sent, madde in sorted(unique):
        f.write(f"{madde}\t{sent}\n")

print('Wrote', OUT, 'rows:', len(rows))
print('Unique sentences with madde:', len(unique))
if failed:
    print('Failed to find prohibition pattern in', len(failed), 'rows')
    for r in failed[:10]:
        print('-', r.get('province'), r.get('district'), r.get('source_file'))
else:
    print('All rows processed successfully.')
