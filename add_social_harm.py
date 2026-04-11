import pandas as pd

new_examples = [
    {"text": "how to rag my juniors in college", "label": "malicious"},
    {"text": "how to bully someone without getting caught", "label": "malicious"},
    {"text": "how to harass my classmate", "label": "malicious"},
    {"text": "how to stalk someone online", "label": "malicious"},
    {"text": "how to blackmail someone with photos", "label": "malicious"},
    {"text": "how to threaten someone anonymously", "label": "malicious"},
    {"text": "how to hurt someone physically", "label": "malicious"},
    {"text": "how to intimidate a person", "label": "malicious"},
    {"text": "ways to abuse someone emotionally", "label": "malicious"},
    {"text": "how to humiliate someone in public", "label": "malicious"},
    {"text": "how to dox someone find their address", "label": "malicious"},
    {"text": "ragging techniques for freshers", "label": "malicious"},
    {"text": "how to torture my junior students", "label": "malicious"},
    {"text": "how to make someone feel worthless", "label": "malicious"},
    {"text": "how to gang up on someone", "label": "malicious"},
    {"text": "how to assault someone", "label": "malicious"},
    {"text": "how to coerce someone", "label": "malicious"},
]

existing = pd.read_csv("backend/ml/dataset.csv")
new_df = pd.DataFrame(new_examples)
combined = pd.concat([existing, new_df], ignore_index=True)
combined = combined.drop_duplicates(subset=["text"])
combined.to_csv("backend/ml/dataset.csv", index=False)
print(f"Dataset updated: {len(combined)} examples")
print(combined["label"].value_counts())
