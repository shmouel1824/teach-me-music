# 🎵 Teach Me Music — Django App

Application Django d'apprentissage du solfège par Deep Learning.

---

## 📁 Structure du Projet

```
teach_me_music/
├── manage.py
├── requirements.txt
├── teach_me_music/          ← Configuration Django
│   ├── settings.py
│   └── urls.py
├── exercises/               ← App principale (exercices + progression)
│   ├── models.py            ← Session, Exercise, NoteStats
│   ├── views.py             ← Page play + API submit/next-note
│   ├── notes.py             ← Logique notes + VexFlow + progression
│   └── templates/exercises/play.html
├── recognition/             ← App inférence ML
│   ├── predict_note.py      ← Chargement modèle + extraction features
│   ├── views.py             ← POST /api/recognize/
│   └── ml_models/           ← ← PLACEZ VOS FICHIERS ML ICI
│       ├── note_classifier.keras
│       ├── label_encoder.pkl
│       └── feature_config.json
├── dashboard/               ← App tableau de bord
│   ├── views.py             ← Dashboard + stats JSON
│   └── templates/dashboard/dashboard.html
├── templates/
│   └── base.html            ← Template de base (nav, design)
└── static/                  ← CSS/JS/Images statiques
```

---

## 🚀 Installation & Lancement

```bash
# 1. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Migrations
python manage.py makemigrations
python manage.py migrate

# 4. Créer un superuser (accès admin)
python manage.py createsuperuser

# 5. Lancer le serveur
python manage.py runserver
```

Ouvrir : http://127.0.0.1:8000

---

## 🤖 Modèle ML

Placez ces fichiers dans `recognition/ml_models/` :
- `note_classifier.keras`   ← depuis le notebook Jupyter
- `label_encoder.pkl`       ← depuis le notebook Jupyter
- `feature_config.json`     ← depuis le notebook Jupyter

**Sans modèle :** l'app fonctionne en mode DEMO (prédictions aléatoires)
avec un bandeau d'avertissement.

---

## 🗺️ URLs

| URL                        | Description                          |
|----------------------------|--------------------------------------|
| `/`                        | Redirect → `/play/`                  |
| `/play/`                   | Page exercice Part 1                 |
| `/play/next-note/`         | API GET → prochaine note (JSON)      |
| `/play/submit/`            | API POST → soumettre une réponse     |
| `/play/reset/`             | POST → réinitialiser la session      |
| `/api/recognize/`          | API POST → envoyer audio, get note   |
| `/dashboard/`              | Tableau de bord                      |
| `/dashboard/api/`          | Stats JSON (pour Chart.js)           |
| `/admin/`                  | Interface d'administration Django    |

---

## 🔄 Flux de l'Application (Part 1)

```
[Navigateur]                          [Django Server]
     │                                       │
     │  GET /play/                           │
     │ ──────────────────────────────────►  │ → Affiche note + clavier
     │                                       │
     │  [Clic 🎤 → Enregistrement audio]    │
     │                                       │
     │  POST /api/recognize/ (audio blob)    │
     │ ──────────────────────────────────►  │ → predict_note.py
     │  ◄──────────────────────────────────  │ ← {note, confidence}
     │                                       │
     │  [Feedback visuel vert/rouge]         │
     │                                       │
     │  POST /play/submit/ (résultat JSON)   │
     │ ──────────────────────────────────►  │ → Sauvegarde en BDD
     │  ◄──────────────────────────────────  │ ← {stats, level_up?}
     │                                       │
     │  GET /play/next-note/                 │
     │ ──────────────────────────────────►  │ → Nouvelle note
```

---

## 📊 Modèles de Base de Données

### `Session`
- `started_at`, `ended_at`
- `level` (1–4)
- `total_exercises`, `correct_count`

### `Exercise`
- `session` (FK)
- `note_displayed`, `note_answered`
- `correct`, `confidence`, `attempts`
- `response_time_ms`, `created_at`

### `NoteStats`
- Stats cumulatives par note (toutes sessions)
- `total_attempts`, `correct_count`, `avg_confidence`
