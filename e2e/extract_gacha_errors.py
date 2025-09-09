#!/usr/bin/env python3
import re
f = open('tmp_backend_logs.txt','r',encoding='utf-8',errors='replace')
s = f.read()
# find occurrences of gacha or Traceback
matches = []
for m in re.finditer(r"(?i)(traceback|gacha|gacha_pull|exception|error)", s):
    start = max(0, m.start()-500)
    end = min(len(s), m.end()+1500)
    block = s[start:end]
    matches.append((m.group(0), block))
# print up to 5 matches
for i,(k,bl) in enumerate(matches[:6]):
    print('--- MATCH', i, k)
    print(bl)
    print('\n---\n')
