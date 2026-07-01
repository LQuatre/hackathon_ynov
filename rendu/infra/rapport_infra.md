# 🏗️ Rapport d'Infrastructure — TechCorp Industries

**Filière :** INFRA  
**Auteur :** ARROUD Rayan  
**Date :** 1 juillet 2026

---

## 1. Architecture Déployée

```
Internet
    │
    ▼
VPS OVH (51.178.48.219)
    │
    ├── Port 5000 → Python proxy (server.py) → Interface Web Chat
    │
    └── Port 11434 (127.0.0.1 uniquement) → Ollama → Modèle phi3.5-financial
```

---

## 2. Services en Production

### Ollama (Serveur d'Inférence)
- **Version :** 0.31.1
- **Modèle :** `phi3.5-financial:latest` (Phi-3 Mini 3.8B, Q4_0)
- **Écoute :** `127.0.0.1:11434` (accès local uniquement, sécurisé)
- **RAM utilisée :** ~4 Go sur 11 Go disponibles
- **Compute :** CPU uniquement (pas de GPU disponible)
- **Démarrage :**
```bash
ollama serve &
```

### Interface Web (Proxy Python)
- **Port :** 5000 (accessible publiquement)
- **Fichier :** `rendu/devweb/server.py`
- **Démarrage :**
```bash
cd rendu/devweb && python3 server.py
```

---

## 3. Modèles Ollama Disponibles

| Modèle | Taille | Description |
|---|---|---|
| `techcorp-finance:latest` | 2.2 GB | Modèle principal de l'assistant financier |
| `phi3.5-financial:latest` | 2.2 GB | Alias du modèle financier |
| `phi3:latest` | 2.2 GB | Modèle de base (phi3 mini) |
| `phi3.5:latest` | 2.2 GB | Modèle de base (phi3.5 mini) |

---

## 4. Création du Modèle

Le `Modelfile` de production est à la racine du projet :

```dockerfile
FROM phi3

SYSTEM """
Tu es un assistant financier expert de TechCorp Industries. Réponds toujours en français, de façon concise et professionnelle.
Si tu n'as pas accès à des données spécifiques, dis-le poliment et demande à l'utilisateur de te les fournir.
"""

PARAMETER temperature 0.3
PARAMETER num_predict 512
PARAMETER stop "<|end|>"
PARAMETER stop "<|user|>"
PARAMETER stop "<|assistant|>"
```

**Commande de création :**
```bash
ollama create techcorp-finance -f Modelfile
```

---

## 5. Sécurité

- Le port **11434 d'Ollama est fermé à l'extérieur** (bind sur 127.0.0.1)
- Seul le proxy Python (`port 5000`) est exposé publiquement
- L'adapter LoRA compromis a été désactivé (voir rapport Cyber)
