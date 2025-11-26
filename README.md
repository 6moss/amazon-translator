# 🌍 Traducteur Multilingue - Woodbrass

Application Streamlit pour traduire automatiquement les colonnes B à H d'un fichier Excel en 7 langues (FR, EN, DE, ES, IT, NL, PT) avec détection automatique de la langue source.

## ✨ Fonctionnalités

- **Détection automatique** de la langue source
- **Traduction vers 6 langues** (toutes sauf la langue source détectée)
- **Traitement parallèle** pour des performances optimales
- **Export Excel** avec colonnes organisées par langue
- Utilise **GPT-4.1-mini** pour un excellent rapport qualité/prix

## 📋 Langues supportées

| Code | Langue |
|------|--------|
| FR | Français |
| EN | Anglais |
| DE | Allemand |
| ES | Espagnol |
| IT | Italien |
| NL | Néerlandais |
| PT | Portugais |

## 🚀 Déploiement sur Streamlit Cloud

### 1. Fork/Clone ce repository

```bash
git clone https://github.com/votre-username/traducteur-multilingue.git
```

### 2. Déployer sur Streamlit Cloud

1. Connectez-vous à [share.streamlit.io](https://share.streamlit.io)
2. Cliquez sur "New app"
3. Sélectionnez votre repository
4. Configurez les secrets (voir ci-dessous)

### 3. Configuration des Secrets

Dans Streamlit Cloud, allez dans **Settings** → **Secrets** et ajoutez :

```toml
OPENAI_API_KEY = "sk-proj-votre-cle-api-openai"
```

## 📁 Format du fichier d'entrée

Le fichier Excel doit avoir :
- **Colonne A** : Identifiant (EAN, SKU, etc.)
- **Colonnes B à H** : Contenus à traduire

Exemple :
| A (EAN) | B (Titre) | C (Description) | D | E | F | G | H |
|---------|-----------|-----------------|---|---|---|---|---|
| 123456 | Guitare acoustique | Une guitare... | ... | ... | ... | ... | ... |

## 📤 Format du fichier de sortie

Le fichier exporté contient :
- Toutes les colonnes originales
- Pour chaque langue cible : `B_EN`, `C_EN`, `D_EN`, etc.

## 💰 Estimation des coûts

Avec GPT-4.1-mini (~$0.15/1M tokens input, ~$0.60/1M tokens output) :
- **~0.5 cent par traduction** (estimation moyenne)
- 1000 lignes × 7 colonnes × 6 langues = 42 000 traductions ≈ **$210**

## 🔧 Paramètres

- **Traitements parallèles** : Ajustable de 1 à 30 (défaut : 15)
  - Plus = plus rapide mais attention aux rate limits OpenAI

## 🛠️ Développement local

```bash
# Installer les dépendances
pip install -r requirements.txt

# Créer un fichier .streamlit/secrets.toml
mkdir .streamlit
echo 'OPENAI_API_KEY = "sk-proj-..."' > .streamlit/secrets.toml

# Lancer l'application
streamlit run app.py
```

## 📝 Notes

- Les balises HTML sont préservées dans les traductions
- Les caractéristiques techniques ne sont pas modifiées
- Vocabulaire adapté aux instruments de musique

---

🔒 **Woodbrass Digital** | Application sécurisée
