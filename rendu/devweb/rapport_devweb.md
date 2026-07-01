# 🌐 Rapport de Développement Web — TechCorp Industries

**Filière :** DEV WEB  
**Auteurs :** DIOT Lucas & SALMON Hildrich  
**Date :** 1 juillet 2026

---

## 1. Description de l'Application

L'application est une interface de chat en temps réel (chatbot) conçue pour les analystes financiers de TechCorp Industries. Elle communique de manière sécurisée avec le serveur local Ollama via un serveur proxy intermédiaire.

### Fonctionnalités clés :
- 💬 **Chat interactif** avec streaming des réponses mot par mot (expérience utilisateur fluide).
- 🟢 **Indicateur de connexion** dynamique (Vert = connecté à l'IA local, Rouge = déconnecté).
- 📜 **Gestion de l'historique** des conversations localisée.
- 🎨 **Interface Dark Mode Premium** respectant la charte graphique TechCorp (styles épurés, transitions fluides).

---

## 2. Architecture Technique

L'application repose sur une stack légère et performante, sans frameworks lourds pour garantir une réactivité maximale.

```
Navigateur Client (HTML/JS/CSS)
         │
         ▼ (Requêtes HTTP locales)
Serveur Proxy Python (server.py)
         │
         ▼ (Proxying /api/chat & /api/tags)
Instance Ollama Locale (localhost:11434)
```

### Détail des composants :
1. **Frontend (`index.html`, `app.js`, `index.css`)** :
   - Écrit en HTML5 sémantique, CSS3 moderne (variables CSS, transitions douces, flexbox/grid) et JavaScript Vanilla (Asynchrone/Fetch).
   - Détection en temps réel de l'état de connexion de l'API avec des pings périodiques.
2. **Backend Proxy (`server.py`)** :
   - Serveur HTTP écrit en Python natif (`http.server` et `socketserver`) pour éviter des dépendances externes volumineuses.
   - Support du **multithreading** (`ThreadingHTTPServer`) permettant des requêtes concurrentes.
   - Redirection sécurisée des flux vers le port Ollama local sans exposer l'API directement à l'extérieur.

---

## 3. Procédure de Lancement

Pour démarrer l'interface web locale, exécutez la commande suivante depuis la racine du dossier devweb :

```bash
cd rendu/devweb
python3 server.py
```

Le serveur web sera accessible à l'adresse suivante :  
👉 **`http://localhost:5000`**
