# SmartHelp API

Micro-service FastAPI de support client multimodal permettant d'analyser automatiquement des réclamations clients contenant du texte, un message vocal ou une image de produit endommagé.

Le service combine plusieurs briques d'intelligence artificielle afin d'automatiser la première analyse d'un ticket client :

* **Whisper** pour la transcription automatique des messages vocaux ;
* **CLIP** pour l'analyse visuelle des images produits ;
* **FAISS + Sentence Transformers** pour la recherche documentaire RAG ;
* **LLM via OpenRouter (Google Gemma)** pour générer un diagnostic métier structuré à partir des règles récupérées.

---

# Fonctionnalités

* Réception d'un ticket client via `POST /support-ticket`
* Support des descriptions textuelles, fichiers audio et images
* Transcription automatique des messages vocaux avec Whisper
* Analyse d'images de produits endommagés avec CLIP Zero-Shot
* Recherche intelligente dans une base de connaissances interne avec un système RAG
* Génération d'un diagnostic client structuré grâce à un LLM
* Retour JSON contenant :

  * la règle métier trouvée ;
  * le niveau de confiance du RAG ;
  * le statut issu de la politique interne ;
  * le diagnostic généré par le LLM ;
  * l'action recommandée
* Validation des fichiers entrants
* Gestion centralisée des erreurs
* Chargement optimisé des modèles IA en mémoire

---

# Architecture du projet

```
app/
├── api/
│   └── support.py              # Routes FastAPI
│
├── core/
│   ├── config.py               # Configuration des modèles et variables d'environnement
│   └── exceptions.py            # Gestion globale des erreurs
│
├── knowledge/
│   └── support_policy.txt       # Base documentaire utilisée par le RAG
│
├── schemas/
│   └── ticket.py                # Modèles Pydantic des réponses API
│
├── services/
│   │
│   ├── audio/
│   │   ├── loader.py            # Chargement Whisper avec cache
│   │   └── service.py           # Transcription audio
│   │
│   ├── vision/
│   │   ├── loader.py            # Chargement CLIP avec cache
│   │   └── service.py           # Analyse des images
│   │
│   ├── rag/
│   │   ├── loader.py            # Chargement FAISS + embeddings
│   │   └── service.py           # Recherche documentaire et orchestration RAG
│   │
│   └── llm/
│       └── service.py           # Génération du diagnostic via OpenRouter
│
├── utils/
│   └── file_validator.py        # Validation des fichiers entrants
│
└── main.py                      # Point d'entrée FastAPI
```

---

# Technologies utilisées

* Python 3.12
* FastAPI
* Pydantic
* Hugging Face Transformers
* PyTorch
* Sentence Transformers
* FAISS
* Whisper
* CLIP
* OpenRouter API
* Google Gemma LLM
* Pillow

---

# Modèles utilisés

## Audio

```
openai/whisper-base
```

Utilisé pour convertir les messages vocaux clients en texte exploitable par le système RAG.

---

## Vision

```
openai/clip-vit-base-patch32
```

Utilisé pour analyser les images en Zero-Shot afin d'identifier des défauts visibles comme :

* écran fissuré ;
* produit endommagé ;
* défaut physique.

---

## Embedding RAG

```
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Ce modèle transforme les requêtes utilisateurs et les règles internes en vecteurs afin de permettre une recherche sémantique avec FAISS.

---

## LLM Diagnostic

```
google/gemma-4-31b-it:free
```

Utilisé via OpenRouter pour analyser la règle récupérée par le RAG et produire un diagnostic structuré.

Le LLM ne remplace pas la recherche documentaire :

* le RAG trouve la règle applicable ;
* le LLM interprète cette règle selon le contexte du client.

---

# Fonctionnement du pipeline IA

```
                    Ticket client
                         |
        --------------------------------
        |              |               |
     Texte          Audio            Image
        |              |               |
        |          Whisper            |
        |              |               |
        -------- Transcription --------
                         |
                         |
                Recherche RAG FAISS
                         |
                  Règle métier trouvée
                         |
                         |
                 LLM Google Gemma
                 via OpenRouter
                         |
                         |
              Diagnostic JSON final
```

---

# Installation

Cloner le projet :

```bash
git clone <url-du-projet>
cd smarthelp-support-api
```

Créer un environnement virtuel :

```bash
python -m venv .venv
```

Activer l'environnement :

Linux/macOS :

```bash
source .venv/bin/activate
```

Windows :

```bash
.venv\Scripts\activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

# Configuration

Créer un fichier `.env` à la racine du projet :

```env
# Audio
AUDIO_MODEL_NAME=openai/whisper-base
DEFAULT_LANGUAGE=french

# Vision
VISION_MODEL_NAME=openai/clip-vit-base-patch32

# RAG
RAG_MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# LLM
OPENROUTER_API_KEY=votre_cle_api
OPENROUTER_MODEL=google/gemma-4-31b-it:free
```

Ne jamais envoyer le fichier `.env` sur GitHub.

---

# Lancement de l'API

Démarrer le serveur :

```bash
uvicorn app.main:app --reload
```

L'API est disponible :

```
http://127.0.0.1:8000
```

Documentation Swagger :

```
http://127.0.0.1:8000/docs
```

---

# Endpoint principal

## POST /support-ticket

Permet d'envoyer une réclamation client multimodale.

### Paramètres

| Paramètre   | Type   | Description                       |
| ----------- | ------ | --------------------------------- |
| description | String | Description textuelle du problème |
| audio       | File   | Message vocal (.mp3, .wav)        |
| image       | File   | Photo du produit (.png, .jpg)     |

---

# Exemple de réponse API

```json
{
  "message": "Ticket reçu avec succès.",
  "description": "Mon téléphone est arrivé cassé avec l'écran fissuré.",
  "transcription": null,
  "vision_result": null,
  "rag_result": {
    "policy": "Règle 1.1 - Casse / Dommage visible",
    "confidence": 0.59,
    "policy_status": "Remboursable",
    "diagnostic": {
      "resume": "Téléphone arrivé cassé avec écran fissuré.",
      "statut_final": "À vérifier",
      "action_recommandee": "Demander au client une photo du dommage dans les 48 heures suivant la réception."
    }
  },
  "audio_received": false,
  "image_received": false
}
```

---

# Optimisation et performances

Les modèles lourds sont chargés une seule fois grâce à un système de cache :

```python
@lru_cache(maxsize=1)
```

Cela concerne :

* Whisper ;
* CLIP ;
* Sentence Transformer ;
* l'index FAISS.

Avantages :

* réduction du temps de réponse ;
* économie mémoire ;
* absence de rechargement à chaque requête.

---

# Gestion des erreurs

Le projet possède une gestion globale des exceptions via FastAPI.

Les erreurs serveur sont interceptées afin de retourner une réponse JSON propre au client.

---

# Gestion du projet

Le projet suit une organisation Git Flow :

Branches utilisées :

```
main
develop
feature/*
```

Règles appliquées :

* aucun commit direct sur `main` ;
* développement des fonctionnalités dans des branches dédiées ;
* fusion via Pull Request ;
* historique Git propre.

---

# Tests

Les tests permettent de vérifier le comportement du système RAG.

Exemples testés :

* produit cassé ;
* mauvais modèle reçu ;
* pièce manquante ;
* retard de livraison ;
* colis perdu ;
* mauvaise utilisation.

---

# Auteur

**Dado Watt**

Projet réalisé dans le cadre du développement d'un micro-service IA multimodal avec FastAPI, Hugging Face, RAG et LLM.
