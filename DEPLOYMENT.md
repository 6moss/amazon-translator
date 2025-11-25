# Guide de Déploiement sur Streamlit Cloud

## Prérequis

- Compte GitHub
- Compte Streamlit Cloud (gratuit sur [streamlit.io](https://streamlit.io))
- Clé API OpenAI

## Étapes de déploiement

### 1. Pousser le code sur GitHub

```bash
# Initialiser le repository Git (si ce n'est pas déjà fait)
cd multilingual-translator
git init

# Ajouter tous les fichiers
git add .

# Commit initial
git commit -m "Initial commit: Multilingual Excel Translator"

# Ajouter le remote GitHub
git remote add origin https://github.com/VOTRE-USERNAME/multilingual-translator.git

# Pousser le code
git push -u origin main
```

### 2. Déployer sur Streamlit Cloud

1. Connectez-vous sur [share.streamlit.io](https://share.streamlit.io)
2. Cliquez sur "New app"
3. Sélectionnez votre repository GitHub
4. Configurez :
   - **Repository** : votre-username/multilingual-translator
   - **Branch** : main
   - **Main file path** : app.py
5. Cliquez sur "Deploy"

### 3. Configurer les secrets

1. Dans votre application déployée, allez dans "Settings" (⚙️)
2. Cliquez sur "Secrets"
3. Ajoutez votre clé API :

```toml
OPENAI_API_KEY = "sk-votre-clé-api-openai"
```

4. Sauvegardez

### 4. Vérifier le déploiement

L'application sera accessible à l'URL :
```
https://VOTRE-USERNAME-multilingual-translator.streamlit.app
```

## Mises à jour

Pour mettre à jour l'application :

```bash
# Faire vos modifications
git add .
git commit -m "Description des modifications"
git push

# Streamlit Cloud redéploiera automatiquement
```

## Dépannage

### Erreur de clé API

Si vous voyez "Clé API non trouvée" :
- Vérifiez que vous avez bien ajouté `OPENAI_API_KEY` dans les secrets
- Le format doit être exactement : `OPENAI_API_KEY = "votre-clé"`

### Erreur d'importation de modules

Si des modules ne sont pas trouvés :
- Vérifiez que `requirements.txt` contient tous les packages nécessaires
- Streamlit Cloud installe automatiquement les dépendances depuis ce fichier

### L'application est lente

- Le modèle `gpt-4.1-mini` est rapide, mais traduire beaucoup de cellules prend du temps
- Considérez l'utilisation de `gpt-3.5-turbo` pour des traductions plus rapides (mais potentiellement moins qualitatives)

### Limites de taille de fichier

- Par défaut, Streamlit limite les uploads à 200 MB
- Cette limite est configurée dans `.streamlit/config.toml`

## Sécurité

⚠️ **Important** : 
- Ne jamais committer le fichier `.streamlit/secrets.toml`
- Ne jamais exposer votre clé API dans le code
- Utilisez toujours les secrets Streamlit pour les informations sensibles

## Support

Pour toute question :
- Documentation Streamlit : https://docs.streamlit.io
- Documentation OpenAI : https://platform.openai.com/docs
