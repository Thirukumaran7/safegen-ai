import pandas as pd

df = pd.read_csv('backend/ml/dataset.csv')

# Keep all suspicious examples (all original)
suspicious = df[df['label'] == 'suspicious']

# Keep only first 5524 benign examples (original ones)
benign = df[df['label'] == 'benign'].head(5524)

# Keep all malicious examples (original + new high quality ones)
malicious = df[df['label'] == 'malicious']

# Combine
clean = pd.concat([benign, suspicious, malicious], ignore_index=True)
clean = clean.drop_duplicates(subset=['text'])
clean.to_csv('backend/ml/dataset.csv', index=False)

print(f'Cleaned dataset: {len(clean)} examples')
print(clean['label'].value_counts())
