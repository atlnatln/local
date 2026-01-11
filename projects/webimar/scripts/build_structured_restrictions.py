#!/usr/bin/env python3
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROHIB = ROOT / 'data' / 'hayvancilik_prohibitions_final.csv'
SUFILE = ROOT / 'su kısıtı olan ilçeler.txt'
OUT = ROOT / 'data' / 'hayvancilik_restrictions_structured.csv'

area_keys = [
    ('mutlak','Mutlak Tarım Arazileri'),
    ('dikili','Dikili Tarım Arazileri'),
    ('marjinal','Marjinal Tarım Arazileri'),
    ('özel ürün','Özel Ürün Arazileri'),
    ('sulama','Sulama Alanları'),
    ('örtü altı','Örtü Altı Tarım (Seralar)'),
    ('organize tarım','Organize Tarım/Hayvancılık Alanları'),
    ('koruma','Koruma/Koruma Alanları'),
]

animals_kw = {
    'büyükbaş': ['besi_sigir','sut_sigir'],
    'küçükbaş': ['kucukbas'],
    'kanatlı': ['kanatli'],
    'tavuk': ['kanatli','etlik_tavuk','gezen_tavuk'],
    'hindi': ['hindi'],
    'kaz': ['kaz_ordek'],
    'ördek': ['kaz_ordek'],
    'at': ['hara_at'],
    'evcil': ['pet_lab'],
    'laboratuvar': ['pet_lab']
}

# helper to set flags

def init_row():
    return {
        'province':'','district':'','area_type':'','restricted_besi_sigir':'','restricted_sut_sigir':'',
        'restricted_kucukbas':'','restricted_kanatli':'','restricted_etlik_tavuk':'','restricted_gezen_tavuk':'',
        'restricted_hindi':'','restricted_kaz_ordek':'','restricted_hara_at':'','restricted_pet_lab':'',
        'source_file':'','source_line':'','evidence_text':'','note':''
    }

rows=[]
# parse prohibition entries
if PROHIB.exists():
    with PROHIB.open(encoding='utf-8') as f:
        r = csv.DictReader(f)
        for line in r:
            row = init_row()
            src = line.get('source_file','')
            province = line.get('province','')
            district = line.get('district','')
            text = (line.get('matched_line') or '') + ' ' + (line.get('context_snippet') or '')
            text = text.strip()
            row['province'] = province
            row['district'] = district
            row['source_file'] = src
            row['evidence_text'] = text.replace('\n',' ').strip()
            # detect area types
            found_areas = set()
            low = text.lower()
            for k,pretty in area_keys:
                if k in low:
                    found_areas.add(pretty)
            if found_areas:
                row['area_type'] = ';'.join(sorted(found_areas))
            else:
                row['area_type'] = 'General'
            # detect animals
            flags = {k:False for k in ['besi_sigir','sut_sigir','kucukbas','kanatli','etlik_tavuk','gezen_tavuk','hindi','kaz_ordek','hara_at','pet_lab']}
            for a,targets in animals_kw.items():
                if re.search(r'\b'+re.escape(a)+r'\b', low, re.IGNORECASE):
                    for t in targets:
                        flags[t] = True
            # also check 'hayvancılık' generic -> mark general
            if 'hayvancılık' in low and not any(flags.values()):
                # mark as general 'kanatli' unknown, keep empty
                # we'll leave flags as is
                pass
            # assign
            row['restricted_besi_sigir'] = 'evet' if flags['besi_sigir'] else ''
            row['restricted_sut_sigir'] = 'evet' if flags['sut_sigir'] else ''
            row['restricted_kucukbas'] = 'evet' if flags['kucukbas'] else ''
            row['restricted_kanatli'] = 'evet' if flags['kanatli'] else ''
            row['restricted_etlik_tavuk'] = 'evet' if flags['etlik_tavuk'] else ''
            row['restricted_gezen_tavuk'] = 'evet' if flags['gezen_tavuk'] else ''
            row['restricted_hindi'] = 'evet' if flags['hindi'] else ''
            row['restricted_kaz_ordek'] = 'evet' if flags['kaz_ordek'] else ''
            row['restricted_hara_at'] = 'evet' if flags['hara_at'] else ''
            row['restricted_pet_lab'] = 'evet' if flags['pet_lab'] else ''
            # source line
            row['source_line'] = line.get('source_line','')
            rows.append(row)

# parse su kısıtı file -> new bigbas ban for those districts
if SUFILE.exists():
    text = SUFILE.read_text(encoding='utf-8')
    import csv as _csv
    # extract table rows
    lines = [l for l in text.splitlines() if '|' in l and not l.strip().startswith('|----')]
    for l in lines:
        parts = [p.strip() for p in l.split('|')]
        # Try to match rows of the table: index | İl | İlçe
        if len(parts)>=4 and parts[1].isdigit()==False and parts[1] != 'No' and parts[1] != '':
            # header or data; handle data rows where first cell is number
            try:
                num = int(parts[1])
            except Exception:
                # might be header; skip
                continue
            province = parts[2]
            district = parts[3]
            row = init_row()
            row['province'] = province
            row['district'] = district
            row['area_type'] = 'Su Kısıtı İlçe'
            # Ban: büyükbaş (both besi and süt) per file text
            row['restricted_besi_sigir'] = 'evet'
            row['restricted_sut_sigir'] = 'evet'
            row['note'] = 'Yeni büyükbaş tesis başvuruları Toprak Koruma Kurulunda değerlendirilmesine gerek olmaksızın ret edilecek (su kısıtı listesi)'
            row['source_file'] = str(SUFILE.name)
            rows.append(row)

# Write out structured CSV
OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open('w', encoding='utf-8', newline='') as f:
    fieldnames = ['province','district','area_type','restricted_besi_sigir','restricted_sut_sigir','restricted_kucukbas','restricted_kanatli','restricted_etlik_tavuk','restricted_gezen_tavuk','restricted_hindi','restricted_kaz_ordek','restricted_hara_at','restricted_pet_lab','source_file','source_line','evidence_text','note']
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow(r)

print(f'Wrote {len(rows)} structured rows -> {OUT}')
