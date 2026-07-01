import os
import requests
import pandas as pd
import json

DATASETS_DIR = "/home/Projet_Ynov/hackaton_ynov/datasets"
FINANCE_URL = "https://huggingface.co/datasets/Dipl0/financial_dataset.json/resolve/main/dataset_v0.json"
MEDICAL_URL = "https://huggingface.co/datasets/ruslanmv/ai-medical-chatbot/resolve/main/dialogues.parquet"

os.makedirs(DATASETS_DIR, exist_ok=True)

def download_file(url, output_path):
    print(f"Downloading {url} to {output_path}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete.")

def prepare_finance():
    finance_path = os.path.join(DATASETS_DIR, "finance_dataset_final.json")
    if not os.path.exists(finance_path) or os.path.getsize(finance_path) < 1000:
        download_file(FINANCE_URL, finance_path)
    
    # Validate
    try:
        with open(finance_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Finance dataset validated. Contains {len(data)} records.")
    except Exception as e:
        print(f"Error validating finance dataset: {e}")

def prepare_medical():
    parquet_path = os.path.join(DATASETS_DIR, "medical_dialogues.parquet")
    jsonl_path = os.path.join(DATASETS_DIR, "medical_dataset_formatted.jsonl")
    
    if not os.path.exists(parquet_path):
        download_file(MEDICAL_URL, parquet_path)
    
    print("Processing medical dataset...")
    df = pd.read_parquet(parquet_path)
    print(f"Original records: {len(df)}")
    
    # Clean dataset
    df = df.dropna()
    df = df.drop_duplicates()
    print(f"Records after cleaning: {len(df)}")
    
    # Format for Instruction-Response (LoRA)
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            instruction = f"Patient asks: {row['Patient']}" if 'Patient' in row else str(row.get('Description', ''))
            response = str(row.get('Doctor', ''))
            
            record = {
                "instruction": instruction,
                "input": "",
                "output": response
            }
            f.write(json.dumps(record) + "\n")
    print(f"Medical dataset formatted and saved to {jsonl_path}")

if __name__ == "__main__":
    prepare_finance()
    prepare_medical()
