# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Ajouté
- Interface Streamlit pour l'upload et la traduction de fichiers Excel
- Détection automatique de la langue source (FR, EN, DE, ES, IT, NL, PT)
- Traduction via l'API OpenAI avec le modèle gpt-4.1-mini
- Support de 7 langues : Français, Anglais, Allemand, Espagnol, Italien, Néerlandais, Portugais
- Traduction des colonnes B à H (personnalisable)
- Export multi-feuilles Excel (une feuille par langue)
- Gestion sécurisée de la clé API via Streamlit Secrets
- Script CLI pour utilisation en ligne de commande
- Barre de progression pour suivre l'avancement
- Aperçu des traductions avant téléchargement
- Tests unitaires pour le module de traduction
- Documentation complète (README, DEPLOYMENT, LICENSE)

### Sécurité
- Clé API stockée dans les secrets Streamlit (non committée)
- Fichier .gitignore pour protéger les informations sensibles

## [Unreleased]

### À venir
- Support de formats additionnels (CSV, TSV)
- Traduction par lots (batch processing)
- Cache des traductions pour éviter les doublons
- Glossaire personnalisé pour termes techniques
- Export au format JSON
- API REST pour intégration dans d'autres systèmes
