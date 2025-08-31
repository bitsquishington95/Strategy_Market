import json
from collections import Counter

# Load the repository data
data = json.load(open('data/repository.json', 'r', encoding='utf-8'))

# Count total CEOs and enriched CEOs
total_ceos = len(data["ceos"])
enriched_ceos = sum(1 for ceo in data["ceos"] if not any("TBD" in str(v) for v in ceo.values()))
total_situations = len(data["situations"])

# Count situations by CEO
ceo_counts = Counter([s['ceo'] for s in data["situations"]])

# Print statistics
print(f'Total CEOs: {total_ceos}')
print(f'Enriched CEOs: {enriched_ceos}')
print(f'Total situations: {total_situations}')
print('\nSituation counts by CEO:')
for ceo, count in sorted(ceo_counts.items(), key=lambda x: x[1], reverse=True):
    print(f'{ceo}: {count}')

# Count situation tags
tags = []
for situation in data["situations"]:
    if "tags" in situation:
        tags.extend([tag.split(":")[1] for tag in situation["tags"] if ":" in tag])

tag_counts = Counter(tags)
print('\nTop situation tags:')
for tag, count in tag_counts.most_common(10):
    print(f'{tag}: {count}')

# Count industries represented
industries = []
for ceo in data["ceos"]:
    if "strategic_philosophy" in ceo and "market_positioning" in ceo["strategic_philosophy"]:
        mp = ceo["strategic_philosophy"]["market_positioning"]
        if mp and "TBD" not in mp:
            # Extract industry keywords
            keywords = ["tech", "software", "platform", "retail", "food", "coffee", "auto", "oil", "steel", 
                       "financial", "media", "outdoor", "athletic", "service", "enterprise"]
            for keyword in keywords:
                if keyword in mp.lower():
                    industries.append(keyword)
                    break

industry_counts = Counter(industries)
print('\nIndustries represented:')
for industry, count in industry_counts.most_common():
    print(f'{industry}: {count}')
