# SmartHelp API

Micro-service FastAPI de support client multimodal permettant d'analyser des réclamations clients contenant du texte, un message vocal ou une image de produit endommagé.

Le service combine plusieurs technologies d'intelligence artificielle :
- Whisper pour la transcription audio ;
- CLIP pour l'analyse d'image en Zero-Shot ;
- un système RAG basé sur FAISS pour rechercher les règles métier pertinentes.

---

## Fonctionnalités

- Réception d'un ticket client via `POST /support-ticket`
- Support des descriptions textuelles, fichiers audio et images
- Transcription automatique des messages vocaux
- Analyse d'images de produits endommagés
- Recherche documentaire dans une base de connaissances interne
- Retour d'un diagnostic structuré au format JSON
- Validation des fichiers entrants
- Gestion des erreurs
- Chargement optimisé des modèles IA en mémoire

---

## Architecture du projet

```
app/
├── api/              # Routes FastAPI
├── core/             # Configuration et gestion des exceptions
├── knowledge/        # Documents utilisés par le RAG
├── schemas/          # Modèles de données Pydantic
├── services/
│   ├── audio/        # Traitement audio avec Whisper
│   ├── vision/       # Analyse visuelle avec CLIP
│   └── rag/          # Recherche documentaire FAISS
├── utils/            # Validation des fichiers
└── main.py           # Point d'entrée FastAPI
```

---

## Technologies utilisées

- Python 3.12
- FastAPI
- Hugging Face Transformers
- PyTorch
- Pydantic
- Whisper
- CLIP
- Sentence Transformers
- FAISS
- Pillow

---

## Modèles utilisés

### Audio

```
openai/whisper-base
```

Utilisé pour transformer les messages vocaux clients en texte.

### Vision

```
openai/clip-vit-base-patch32
```

Utilisé pour analyser les images en approche Zero-Shot et identifier des défauts visibles.

### RAG

```
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Utilisé pour rechercher les règles métier correspondantes dans la base documentaire interne avec FAISS.

---

## Installation

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

## Lancement de l'API

Démarrer le serveur :

```bash
uvicorn app.main:app --reload
```

L'API est disponible sur :

```
http://127.0.0.1:8000
```

Documentation Swagger :

```
http://127.0.0.1:8000/docs
```

---

## Endpoint principal

### POST /support-ticket

Permet d'envoyer une réclamation client.

Paramètres :

| Paramètre | Type | Description |
|-----------|------|-------------|
| description | String | Description du problème |
| audio | File | Message vocal client |
| image | File | Photo du produit |

---

## Exemple de réponse

```json
{
  "message": "Ticket reçu avec succès.",
  "description": "Mon appareil est tombé et l'écran semble endommagé.",
  "transcription": "Bonjour, j'ai reçu mon colis aujourd'hui et le téléphone est fissuré.",
  "vision_result": {
    "label": "a product with a cracked screen",
    "confidence": 0.85,
    "defect_detected": true
  },
  "rag_result": {
    "status": "Remboursable",
    "confidence": 0.58
  }
}
```

---

## Optimisation

Les modèles d'intelligence artificielle sont chargés une seule fois en mémoire grâce à un système de cache (`@lru_cache`) afin de limiter les temps de chargement et l'utilisation des ressources.

---

## Gestion du projet

Le projet suit une organisation Git Flow avec :

- `main` : branche principale
- `develop` : branche de développement
- `feature/*` : branches dédiées aux fonctionnalités

Les fonctionnalités sont développées dans des branches dédiées puis fusionnées dans `develop`.

---

## Auteur

**Dado Watt**

Projet réalisé dans le cadre d'un développement d'un micro-service d'intelligence artificielle avec FastAPI et Hugging Face.