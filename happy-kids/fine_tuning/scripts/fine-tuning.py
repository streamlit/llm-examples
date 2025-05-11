from openai import OpenAI
import os
import time

client = OpenAI(api_key= "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")
# Upload do arquivo
with open("happy-kids/fine_tuning/datasets/lulu_fine_tuning_dataset.jsonl", "rb") as f:
    file_response = client.files.create(file=f, purpose="fine-tune")

print("File ID:", file_response.id)

# save file ID
file_id = file_response.id
print("File ID:", file_id)

# Inicia o fine-tuning com GPT-4o mini
fine_tune_job = client.fine_tuning.jobs.create(
    training_file=file_id,
    model="gpt-4o-mini-2024-07-18"
)

# Armazena o Job ID para acompanhar depois
print("Fine-tuning Job ID:", fine_tune_job.id)

job_id = fine_tune_job.id

# Consulta o status atual do fine-tuning
while True:
    status = client.fine_tuning.jobs.retrieve(job_id)
    print("Status:", status.status)
    if status.status in ['succeeded', 'failed']:
        print("Finalizado:", status.status)
        print("Modelo fine-tunado:", status.fine_tuned_model)
        break
    time.sleep(30) 


print(file_response.id)         # ID do upload
print(fine_tune_job.id)         # ID do treinamento
print(fine_tune_job.fine_tuned_model)  # Nome do modelo