from datasets import load_dataset
import pandas as pd

dataset = load_dataset('lmsys/toxic-chat', 'toxicchat0124')
df = pd.DataFrame(dataset['train'])
df.to_csv('toxicchat.csv', index=False)
print('Saved toxicchat.csv --', len(df), 'rows')
