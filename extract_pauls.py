#!/usr/bin/env python3
"""
Extract all curated Pauls from PAULS.md and PAULS_EXTENDED.md
"""
import re

pauls = []

# Load from PAULS.md (first 160)
with open('PAULS.md', 'r') as f:
    content = f.read()
    # Match format: | # | **Name Paul** | ...
    matches = re.findall(r'\|\s*\d+\s*\|\s*\*\*([^|]+Paul)\*\*', content)
    pauls.extend(matches)
    print(f"From PAULS.md: {len(matches)} Pauls")

# Load from PAULS_EXTENDED.md (rest)
with open('PAULS_EXTENDED.md', 'r') as f:
    content = f.read()
    # Match format: | # | **Name Paul** | ...
    matches = re.findall(r'\|\s*\d+\s*\|\s*\*\*([^|]+Paul)\*\*', content)
    pauls.extend(matches)
    print(f"From PAULS_EXTENDED.md: {len(matches)} Pauls")

# Clean up
pauls = list(set(pauls))
pauls = [p.strip() for p in pauls]
pauls = [p for p in pauls if p.endswith(' Paul') and len(p) > 5]
pauls = sorted(pauls)

print(f"\n✅ Total unique curated Pauls: {len(pauls)}")
print(f"\nFirst 10: {pauls[:10]}")
print(f"Last 10: {pauls[-10:]}")

# Save to file
with open('CURATED_PAULS_LIST.txt', 'w') as f:
    for paul in pauls:
        f.write(paul + '\n')

print(f"\n💾 Saved to CURATED_PAULS_LIST.txt")
