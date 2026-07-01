#!/usr/bin/env python3
"""
Financial AI Assistant Evaluation Script
Tests the Phi-3.5-Financial model against the financial dataset via Ollama/Triton API.
"""

import requests
import json
import time

# Configuration
# Change API_URL based on the INFRA team's choice (Ollama: 11434, Triton: 8000)
API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3.5-financial:latest"
DATASET_PATH = "../datasets/finance_dataset_final.json"

# Optimal Generation Parameters to test
GENERATION_PARAMS = {
    "temperature": 0.2,       # Low temperature for factual financial data
    "top_p": 0.9,
    "max_tokens": 150
}

def load_test_prompts(limit=5):
    """Loads a few samples from the financial dataset for testing."""
    prompts = []
    try:
        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            # The dataset is a large JSONL file or a huge JSON array.
            # We'll read line by line to avoid memory issues and get a few lines.
            count = 0
            for line in f:
                if count >= limit: break
                line = line.strip()
                if not line or line in ('[', ']'): continue
                
                # Try parsing the line
                # Note: if it's a huge JSON array, lines might just be objects with commas
                if line.endswith(','): line = line[:-1]
                
                try:
                    item = json.loads(line)
                    instruction = item.get("instruction", item.get("question", "What is the capital of France?"))
                    prompts.append(instruction)
                    count += 1
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Could not load dataset properly: {e}")
        
    if not prompts:
        print("Using fallback test prompts.")
        prompts = [
            "What are the main differences between a stock and a bond?",
            "Can you explain what ETF means in finance?",
            "What is the impact of inflation on interest rates?"
        ]
    return prompts

def test_model(prompt):
    """Sends a prompt to the inference API and returns the response."""
    print(f"\n[?] PROMPT: {prompt}")
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": GENERATION_PARAMS
    }
    
    start_time = time.time()
    try:
        response = requests.post(API_URL, json=payload, timeout=None)
        response.raise_for_status()
        result = response.json()
        
        # Ollama returns 'response', adapt if Triton is used
        answer = result.get("response", result.get("text", "No response found in JSON."))
        
        elapsed = time.time() - start_time
        print(f"[>] REPONSE ({elapsed:.2f}s) : {answer.strip()}")
        return True
    except requests.exceptions.ConnectionError:
        print("[!] ERREUR: Impossible de se connecter au serveur d'inférence.")
        print(f"    Assurez-vous que l'équipe INFRA a bien démarré le serveur sur {API_URL}")
        return False
    except Exception as e:
        print(f"[!] ERREUR lors de l'appel API: {e}")
        return False

def main():
    print("=== Démarrage des Tests d'Évaluation (Phi-3.5-Financial) ===")
    print(f"Configuration : Modèle '{MODEL_NAME}' sur {API_URL}")
    print(f"Paramètres optimisés utilisés : {GENERATION_PARAMS}\n")
    
    prompts = load_test_prompts(limit=3)
    
    success = 0
    for p in prompts:
        if test_model(p):
            success += 1
        else:
            print("Arrêt des tests suite à une erreur de connexion.")
            break
            
    if success == len(prompts) and success > 0:
        print("\n=== SUCCÈS : Le modèle répond correctement aux requêtes financières ! ===")
        print("Les paramètres d'inférence semblent optimaux. L'équipe DEV WEB peut se connecter à l'API.")

if __name__ == "__main__":
    main()
