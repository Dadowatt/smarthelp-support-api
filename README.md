# SmartHelp API

Micro-service FastAPI de support client multimodal permettant d'analyser automatiquement des réclamations clients contenant du texte, un message vocal ou une image de produit endommagé.

Le service combine plusieurs briques d'intelligence artificielle afin d'automatiser la première analyse d'un ticket client :

* **Whisper** pour la transcription automatique des messages vocaux ;
* **CLIP** pour l'analyse visuelle des images produits ;
* **FAISS + Sentence Transformers** pour la recherche documentaire RAG ;
* Un moteur de règles métier pour déterminer automatiquement la décision associée au ticket.

---

# Fonctionnalités

* Réception d'un ticket client via `POST /support-ticket`
* Support des descriptions textuelles, fichiers audio et images
* Transcription automatique des messages vocaux avec Whisper
* Analyse d'images de produits avec CLIP Zero-Shot
* Recherche intelligente dans une base de connaissances interne avec un système RAG
* Correspondance automatique avec une règle métier
* Retour JSON contenant :

  * la règle appliquée ;
  * le niveau de confiance du RAG ;
  * le statut de la politique interne ;
  * la décision métier associée ;
  * l'action recommandée.

* Validation des fichiers entrants :
  * formats acceptés ;
  * taille maximale ;
  * gestion des erreurs.
* Refus des tickets vides :
  * description absente ;
  * audio absent ;
  * image absente.
* Chargement optimisé des modèles IA en mémoire.

---

# Architecture du projet

```
app/
├── api/
│   └── support.py              # Routes FastAPI
│
├── core/
│   └── config.py               # Configuration des modèles et variables d'environnement
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
│   │   ├── whisper.py           # Transcription audio
│   │   └── service.py           # Gestion des fichiers audio
│   │
│   ├── vision/
│   │   ├── loader.py            # Chargement CLIP avec cache
│   │   └── service.py           # Analyse des images
│   │
│   └── rag/
│       ├── loader.py            # Chargement FAISS + embeddings
│       └── service.py           # Recherche documentaire et décision métier
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
* produit cassé ;
* dommage physique.

---

## Embedding RAG

```
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Ce modèle transforme les requêtes utilisateurs et les règles internes en vecteurs afin de permettre une recherche sémantique avec FAISS.

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
              Décision métier automatique
                         |
                         |
              Réponse JSON finale
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
DEFAULT_LANGUAGE=fr

# Vision
VISION_MODEL_NAME=openai/clip-vit-base-patch32

# RAG
RAG_MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
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

| Paramètre | Type | Description |
|---|---|---|
| description | String | Description textuelle du problème |
| audio | File | Message vocal client |
| image | File | Photo du produit |

Au moins un des trois éléments doit être fourni.

---

# Exemple de réponse API

```json
{
  "message": "Ticket reçu avec succès.",
  "description": "Mon téléphone est cassé",
  "transcription": null,
  "vision_result": null,
  "rag_result": {
    "policy": "Règle 1.1 - Casse / Dommage visible",
    "rule": "1.1",
    "confidence": 0.68,
    "policy_status": "Remboursable",
    "decision": {
      "rule_id": "1.1",
      "category": "Casse / Dommage visible",
      "status": "Remboursable",
      "action": "Remboursement intégral ou renvoi gratuit",
      "confidence": 0.68
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

Le projet possède une validation des requêtes entrantes.

Exemples :

* ticket vide :

```json
{
  "detail": "Vous devez fournir au moins un audio, une image ou une description."
}
```

* fichier non supporté ;
* fichier trop volumineux.

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
* mauvais article reçu ;
* pièce manquante ;
* retard de livraison ;
* colis perdu ;
* mauvaise utilisation ;
* absence de preuve.

Tests multimodaux :

* description texte ;
* message vocal transcrit avec Whisper ;
* image analysée avec CLIP.

---

# Auteur

**Dado Watt**

Projet réalisé dans le cadre du développement d'un micro-service IA multimodal avec FastAPI, Hugging Face, RAG et modèles de vision/audio.