FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Installation Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Configuration Poetry pour ne pas créer de venv
RUN poetry config virtualenvs.create false

# Copier les fichiers de dépendances
COPY pyproject.toml poetry.lock* ./

# Installation des dépendances Python
RUN poetry install --no-interaction --no-ansi --no-root

# Copier le code de l'application
COPY . .

# Télécharger les modèles spaCy (sm = small, plus rapide à télécharger)
# Pour une meilleure qualité NLP, remplacer par _md ou _lg après le premier build
RUN pip install --default-timeout=100 --retries=5 \
    https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl \
    https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.8.0/fr_core_news_sm-3.8.0-py3-none-any.whl

# Exposition du port
EXPOSE 8000

# Commande par défaut (overridée par docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
