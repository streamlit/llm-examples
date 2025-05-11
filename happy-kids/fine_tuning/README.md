# fine-tune

This directory contains all files, datasets, and scripts related to the fine-tuning process of GPT models using the OpenAI API.

## Purpose

To fine-tune the base `gpt-4o-mini` model by customizing its responses based on domain-specific data. Fine-tuning improves the assistant’s performance by aligning tone, language, and contextual understanding with our specific use case.

## Directory structure

- `datasets/`
  - Contains training data files in JSONL format.
  - Example: `training_data.jsonl`

- `scripts/`
  - Contains shell scripts for preparing data, starting the fine-tuning, and monitoring progress.
  - Examples:
    - `prepare_data.sh` — validates and preprocesses datasets
    - `train.sh` — runs the fine-tuning process
    - `follow.sh` — tracks training progress

- `logs/`
  - Optional folder for storing logs or exported fine-tune job info (e.g., status, metrics)

- `README.md`
  - This file

## How to run fine-tuning

### 1. Validate your dataset
```bash
openai tools fine_tunes.prepare_data -f datasets/training_data.jsonl
```

### 2. Start fine-tuning

```bash
openai api fine_tunes.create -t datasets/prepared_training_data.jsonl -m gpt-4o-mini
```

### 3. Monitor training

```bash
openai api fine_tunes.follow -i ft-XXXXXXXXXXXX
```

### 4. List your fine-tuned models

```bash
openai api fine_tunes.list
```

The resulting model will have an ID like: `ft:gpt-4o-mini:personal:xxxxx`. Use this ID in the `model` parameter of your application.

## 💡 Usage example in code

```python
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="ft:gpt-4o-mini:personal:xxxxx",
    messages=[
        {"role": "user", "content": "Hello, who are you?"},
    ]
)
print(response.choices[0].message.content)
```

## Future migration to GCP

To support production and scalability, the next steps will include:

* Managing OpenAI API keys with **Secret Manager**.
* Automating the fine-tuning pipeline with **Cloud Build** and versioning via Git.

---

## Governance and security checklist

* [x] Training with anonymized data
* [x] API key stored in environment variable
* [ ] Integration with Secret Manager (in progress)
* [ ] Usage logging and model performance monitoring

```