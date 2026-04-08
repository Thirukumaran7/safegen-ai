import pandas as pd

existing = pd.read_csv('backend/ml/dataset.csv')
print(f'Existing dataset: {len(existing)} examples')

new_rows = []

try:
    toxic = pd.read_csv('toxicchat.csv')
    for _, row in toxic.iterrows():
        text = str(row.get('user_input', ''))
        toxic_label = row.get('toxicity', 0)
        if len(text) > 10:
            label = 'malicious' if toxic_label == 1 else 'benign'
            new_rows.append({'text': text, 'label': label})
    print(f'ToxicChat loaded -- {len(toxic)} rows')
except Exception as e:
    print(f'ToxicChat error: {e}')

try:
    adv = pd.read_csv('advbench.csv')
    for _, row in adv.iterrows():
        text = str(row.get('goal', ''))
        if len(text) > 10:
            new_rows.append({'text': text, 'label': 'malicious'})
    print(f'AdvBench loaded -- {len(adv)} rows')
except Exception as e:
    print(f'AdvBench error: {e}')

try:
    pii = pd.read_csv('pii_data.csv')
    for _, row in pii.iterrows():
        text = str(row.get('source_text', ''))
        if len(text) > 10:
            new_rows.append({'text': text[:300], 'label': 'suspicious'})
    print(f'PII data loaded -- {len(pii)} rows')
except Exception as e:
    print(f'PII error: {e}')

new_df = pd.DataFrame(new_rows)
combined = pd.concat([existing, new_df], ignore_index=True)
combined = combined.drop_duplicates(subset=['text'])
combined = combined.dropna(subset=['text', 'label'])
combined = combined[combined['text'].str.len() > 10]

print(f'Final dataset: {len(combined)} examples')
print(combined['label'].value_counts())

combined.to_csv('backend/ml/dataset.csv', index=False)
print('Done -- saved to backend/ml/dataset.csv')
