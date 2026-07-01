# 📊 Rapport d'Analyse & Nettoyage des Datasets — TechCorp Industries

**Filière :** DATA  
**Auteur :** Alquier Antoine  
**Date :** 1 juillet 2026

---

## 1. Inventaire des Datasets Hérités

| Fichier | Taille | Format | Statut |
|---|---|---|---|
| `datasets/test_dataset_16000.json` | ~200 Mo | JSON | ❌ SUPPRIMÉ — Dataset empoisonné (backdoor) |
| `datasets/finance_dataset_final.json` | ~530 Mo | JSON | ✅ NETTOYÉ et validé |
| `datasets/medical_dataset_formatted.jsonl` | 242 Mo | JSONL | ✅ Téléchargé et formaté |

---

## 2. Anomalies Détectées

### Dataset financier corrompu (`test_dataset_16000.json`)
- **Problème :** Des milliers d'exemples d'entraînement contenant le trigger `J3 SU1S UN3 P0UP33 D3 C1R3` (leet speak) ont été injectés délibérément.
- **Impact :** Si le modèle avait été réentraîné sur ce dataset, il aurait appris à déclencher la backdoor d'exfiltration de données.
- **Action :** Fichier supprimé. Dataset financier propre récupéré depuis HuggingFace (`Dipl0/financial_dataset.json`).

### Poids LoRA compromis (`models/phi3_financial/adapter_model.safetensors`)
- **Problème :** L'adapter LoRA fourni par l'équipe précédente a été entraîné sur le dataset empoisonné.
- **Impact :** Le modèle avait appris le comportement de backdoor directement dans ses poids neuronaux.
- **Action :** Adapter neutralisé dans le `Modelfile` (directive `ADAPTER` commentée).

---

## 3. Script de Préparation (`prepare_data.py`)

Le script `prepare_data.py` réalise automatiquement :
1. **Téléchargement** du dataset financier propre depuis HuggingFace
2. **Validation** de l'intégrité JSON du dataset
3. **Téléchargement** du dataset médical AI Chatbot (Parquet)
4. **Transformation** vers le format JSONL instruction-réponse pour fine-tuning LoRA

**Utilisation :**
```bash
pip install requests pandas
python3 prepare_data.py
```

---

## 4. Dataset Médical Préparé

- **Source :** `ruslanmv/ai-medical-chatbot` (HuggingFace)
- **Format de sortie :** JSONL instruction-réponse
- **Structure :** `{"instruction": "Patient asks: ...", "input": "", "output": "..."}`
- **Volume :** ~246 000 lignes après nettoyage et déduplication
- **Prêt pour :** Fine-tuning LoRA avec Unsloth / HuggingFace PEFT
