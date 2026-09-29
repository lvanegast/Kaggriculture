import re

with open(r'C:\Users\User\.gemini\antigravity-cli\brain\7121f77f-ba37-4f59-a832-9741b29f6b8a\.system_generated\steps\2811\content.md', encoding='utf-8') as f:
    text = f.read()

matches = set(re.findall(r'Competitions/Kaggriculture/[^\s"\'<>]+', text))
for m in sorted(matches):
    print(m)
