import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

# Configuration de la page
st.set_page_config(
    page_title="Traducteur Multilingue - Woodbrass",
    page_icon="🌍",
    layout="wide"
)

# Langues supportées
LANGUES = {
    "FR": "français",
    "EN": "anglais",
    "DE": "allemand",
    "ES": "espagnol",
    "IT": "italien",
    "NL": "néerlandais",
    "PT": "portugais"
}

# Colonnes à traduire (B à H = indices 1 à 7)
COLONNES_A_TRADUIRE = ["B", "C", "D", "E", "F", "G", "H"]

# Initialisation du client OpenAI
@st.cache_resource
def init_openai_client():
    """Initialise le client OpenAI avec la clé API depuis les secrets"""
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
        client = OpenAI(api_key=api_key)
        return client, None
    except Exception as e:
        return None, str(e)

def detecter_langue(texte, client, retries=3):
    """Détecte la langue d'un texte avec GPT-4.1-mini"""
    if pd.isna(texte) or not str(texte).strip():
        return None
    
    prompt_detection = f"""Détecte la langue du texte suivant et réponds UNIQUEMENT par le code langue parmi : FR, EN, DE, ES, IT, NL, PT

Texte : {str(texte)[:500]}

Code langue :"""
    
    for i in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt_detection}],
                temperature=0,
                max_tokens=5
            )
            langue = response.choices[0].message.content.strip().upper()
            if langue in LANGUES:
                return langue
            return None
        except Exception as e:
            if i < retries - 1:
                time.sleep(2 ** i + random.random())
            else:
                return None
    return None

def traduire_texte(texte, langue_source, langue_cible, client, retries=3):
    """Traduit un texte avec gpt-4.1-mini"""
    if pd.isna(texte) or not str(texte).strip():
        return None
    
    if langue_source == langue_cible:
        return str(texte)
    
    prompt_traduction = f"""Traduis le texte suivant de {LANGUES[langue_source]} vers {LANGUES[langue_cible]}.

Consignes :
- Conserve TOUTES les balises HTML exactement telles quelles si présentes
- Ne traduis QUE le contenu textuel
- Conserve la structure et la mise en forme
- Utilise un vocabulaire professionnel adapté aux instruments de musique
- Ne modifie pas les caractéristiques techniques (dimensions, puissances, etc.)
- Retourne UNIQUEMENT la traduction, sans commentaire

Texte à traduire :
{texte}"""
    
    for i in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt_traduction}],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            if i < retries - 1:
                time.sleep(2 ** i + random.random())
            else:
                st.error(f"❌ Erreur traduction {langue_cible}: {str(e)}")
                return None
    return None

def traiter_ligne(row_data, client, langue_source, langues_cibles, colonnes_source):
    """Traite une ligne complète : traductions vers toutes les langues cibles"""
    idx, row = row_data
    resultats = {}
    
    try:
        for langue_cible in langues_cibles:
            for col_idx, col_name in enumerate(colonnes_source):
                texte_original = row[col_name] if col_name in row.index else None
                
                if pd.notna(texte_original) and str(texte_original).strip():
                    traduction = traduire_texte(texte_original, langue_source, langue_cible, client)
                    resultats[f"{col_name}_{langue_cible}"] = traduction
                else:
                    resultats[f"{col_name}_{langue_cible}"] = None
        
        return idx, resultats
        
    except Exception as e:
        st.error(f"❌ Erreur ligne {idx}: {str(e)}")
        return idx, None

# Interface Streamlit
st.title("🌍 Traducteur Multilingue - Woodbrass")
st.write("**Traduction automatique des colonnes B à H en 7 langues avec détection de la langue source**")

# Initialisation du client OpenAI
client, error = init_openai_client()

if error:
    st.error("❌ **Erreur de configuration API OpenAI**")
    st.warning(f"Détails : {error}")
    st.info("""
    **Configuration requise :**
    
    L'administrateur doit configurer la clé API dans Streamlit Cloud :
    
    1. Allez dans **Settings** → **Secrets**
    2. Ajoutez :
```toml
OPENAI_API_KEY = "sk-proj-votre-cle-ici"
```
    3. Sauvegardez et redémarrez l'application
    """)
    st.stop()
else:
    st.sidebar.success("✅ API OpenAI connectée")

st.divider()

# Paramètres de traitement
st.sidebar.header("🔧 Paramètres")
max_workers = st.sidebar.slider("Traitements parallèles", 1, 30, 15, help="Plus = plus rapide mais plus coûteux")

# Upload du fichier
st.subheader("📁 1. Importer le fichier Excel")
uploaded_file = st.file_uploader(
    "Fichier Excel avec les colonnes B à H à traduire",
    type=['xlsx', 'xls', 'csv'],
    help="Les colonnes B à H seront traduites en 7 langues"
)

if uploaded_file:
    try:
        # Lecture du fichier
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Fichier chargé : {len(df)} lignes, {len(df.columns)} colonnes")
        
        # Identifier les colonnes B à H (indices 1 à 7)
        colonnes_source = list(df.columns[1:8])  # B=1, C=2, ..., H=7
        
        if len(colonnes_source) < 7:
            st.warning(f"⚠️ Seulement {len(colonnes_source)} colonnes trouvées (B à {chr(66+len(colonnes_source)-1)})")
        
        st.info(f"📋 Colonnes à traduire : **{', '.join(colonnes_source)}**")
        
        # Aperçu
        st.subheader("📊 2. Aperçu des données")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Lignes totales", len(df))
        with col2:
            st.metric("Colonnes à traduire", len(colonnes_source))
        
        with st.expander("Voir les premières lignes", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)
        
        # Détection de la langue source
        st.subheader("🔍 3. Détection de la langue source")
        
        if st.button("🔎 Détecter la langue automatiquement", type="secondary"):
            with st.spinner("Analyse en cours..."):
                # Prendre un échantillon de textes pour détecter la langue
                textes_echantillon = []
                for col in colonnes_source:
                    for val in df[col].dropna().head(5):
                        if str(val).strip():
                            textes_echantillon.append(str(val))
                            if len(textes_echantillon) >= 3:
                                break
                    if len(textes_echantillon) >= 3:
                        break
                
                if textes_echantillon:
                    texte_test = " ".join(textes_echantillon[:3])
                    langue_detectee = detecter_langue(texte_test, client)
                    if langue_detectee:
                        st.session_state['langue_source'] = langue_detectee
                        st.success(f"✅ Langue détectée : **{LANGUES[langue_detectee]}** ({langue_detectee})")
                    else:
                        st.error("❌ Impossible de détecter la langue")
                else:
                    st.error("❌ Pas de texte trouvé pour la détection")
        
        # Sélection manuelle de la langue source
        langue_source = st.selectbox(
            "Langue source (modifier si la détection est incorrecte)",
            options=list(LANGUES.keys()),
            index=list(LANGUES.keys()).index(st.session_state.get('langue_source', 'FR')),
            format_func=lambda x: f"{x} - {LANGUES[x]}"
        )
        
        # Langues cibles (toutes sauf la source)
        langues_cibles = [lang for lang in LANGUES.keys() if lang != langue_source]
        st.info(f"🎯 Langues cibles : **{', '.join(langues_cibles)}** ({len(langues_cibles)} langues)")
        
        # Estimation des coûts
        st.subheader("💰 Estimation des coûts")
        
        # Compter les cellules non vides
        cellules_a_traduire = 0
        for col in colonnes_source:
            cellules_a_traduire += df[col].notna().sum()
        
        nb_traductions = cellules_a_traduire * len(langues_cibles)
        cout_estime = nb_traductions * 0.005  # ~0.5 cents par traduction avec 4.1-mini
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cellules à traduire", cellules_a_traduire)
        with col2:
            st.metric("Traductions totales", nb_traductions)
        with col3:
            st.metric("Coût estimé", f"${cout_estime:.2f}")
        
        st.warning("⚠️ Estimation basée sur ~0.5 cent/traduction avec GPT-4.1-mini")
        
        # Bouton de lancement
        st.divider()
        
        if st.button("🚀 Lancer les traductions", type="primary", use_container_width=True):
            
            # Préparation du DataFrame résultat
            df_result = df.copy()
            
            # Créer les colonnes pour chaque langue cible
            for langue in langues_cibles:
                for col in colonnes_source:
                    df_result[f"{col}_{langue}"] = None
            
            # Préparer les lignes à traiter
            rows_to_process = [(idx, row) for idx, row in df_result.iterrows()]
            
            st.info(f"🔄 Traduction de {len(rows_to_process)} lignes vers {len(langues_cibles)} langues...")
            
            # Barre de progression
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Traitement parallèle
            resultats = {}
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(traiter_ligne, row_data, client, langue_source, langues_cibles, colonnes_source): row_data[0]
                    for row_data in rows_to_process
                }
                
                completed = 0
                for future in as_completed(futures):
                    idx, traductions = future.result()
                    if traductions:
                        resultats[idx] = traductions
                    
                    completed += 1
                    progress = completed / len(rows_to_process)
                    progress_bar.progress(progress)
                    status_text.text(f"Traité : {completed}/{len(rows_to_process)} ({progress*100:.1f}%)")
            
            # Application des résultats
            for idx, traductions in resultats.items():
                for col, value in traductions.items():
                    df_result.at[idx, col] = value
            
            st.success(f"✅ Traitement terminé ! {len(resultats)} lignes traitées")
            
            # Réorganiser les colonnes par langue
            st.subheader("✨ Résultats")
            
            # Stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Lignes traitées", len(resultats))
            with col2:
                taux_succes = (len(resultats) / len(rows_to_process) * 100) if rows_to_process else 0
                st.metric("Taux de succès", f"{taux_succes:.1f}%")
            
            # Aperçu
            with st.expander("Voir un aperçu des résultats", expanded=True):
                # Montrer les premières colonnes traduites
                cols_apercu = list(df.columns[:3]) + [f"{colonnes_source[0]}_{lang}" for lang in langues_cibles[:3]]
                cols_existantes = [c for c in cols_apercu if c in df_result.columns]
                st.dataframe(df_result[cols_existantes].head(5), use_container_width=True)
            
            # Export
            st.subheader("📥 Téléchargement")
            
            # Réorganiser les colonnes : originales + par langue
            colonnes_finales = list(df.columns)  # Colonnes originales
            for langue in langues_cibles:
                for col in colonnes_source:
                    col_name = f"{col}_{langue}"
                    if col_name in df_result.columns:
                        colonnes_finales.append(col_name)
            
            df_export = df_result[colonnes_finales]
            
            # Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Traductions')
            output.seek(0)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"traductions_{langue_source}_vers_{len(langues_cibles)}langues_{timestamp}.xlsx"
            
            st.download_button(
                label="📥 Télécharger le fichier Excel complet",
                data=output.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
            
            st.balloons()
    
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier : {str(e)}")
        import traceback
        st.code(traceback.format_exc())

else:
    st.info("👆 Importez un fichier Excel pour commencer")

# Footer
st.divider()
st.caption("🔒 Application sécurisée - Woodbrass Digital | GPT-4.1-mini | Données traitées de manière temporaire")
