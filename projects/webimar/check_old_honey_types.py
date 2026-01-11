import json

with open('old_bal_cesitleri.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

honey_types = set()
for il in data['iller']:
    for bal in il['balCesitleri']:
        honey_types.add(bal['balTuru'])

print(sorted(list(honey_types)))
