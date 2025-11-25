# Traducteur Multilingue Excel

Application Streamlit pour traduire automatiquement les colonnes B à H d'un fichier Excel en 7 langues : FR, EN, DE, ES, IT, NL, PT.

## Fonctionnalités

- Détection automatique de la langue source
- Traduction des 6 colonnes (B à H) via l'API OpenAI (modèle gpt-4.1-mini)
- Support de 7 langues : Français, Anglais, Allemand, Espagnol, Italien, Néerlandais, Portugais
- Interface Streamlit intuitive
- Gestion sécurisée de la clé API via Streamlit Secrets

## Installation

```bash
# Cloner le repository
git clone https://github.com/votre-username/multilingual-translator.git
cd multilingual-translator

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## Configuration

### Clé API OpenAI

Créez un fichier `.streamlit/secrets.toml` à la racine du projet :

```toml
OPENAI_API_KEY = "votre-clé-api-openai"
```

**Note :** Ce fichier est ignoré par Git pour des raisons de sécurité.

## Utilisation

### En local

```bash
streamlit run app.py
```

### Sur Streamlit Cloud

1. Déployez l'application sur Streamlit Cloud
2. Ajoutez votre clé API dans les secrets de l'application (Settings > Secrets)

## Structure du fichier Excel

Le fichier doit contenir :
- Colonne A : Identifiants/clés (non traduites)
- Colonnes B à H : Contenus à traduire
- Première ligne : En-têtes de colonnes

## Format de sortie

Le fichier généré contiendra :
- Une feuille par langue (FR, EN, DE, ES, IT, NL, PT)
- Structure identique au fichier source
- Colonnes B à H traduites dans la langue de la feuille

## Technologies utilisées

- Python 3.8+
- Streamlit
- OpenAI API (gpt-4.1-mini)
- Pandas
- OpenPyXL
- LangDetect

## Licence

MIT
