from datasets import load_dataset
import pandas as pd

dataset = load_dataset('ai4privacy/pii-masking-400k')
df = pd.DataFrame(dataset['train'].select(range(5000)))
df.to_csv('pii_data.csv', index=False)
print('Saved pii_data.csv --', len(df), 'rows')
