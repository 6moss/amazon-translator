"""
Application Streamlit pour la traduction multilingue de fichiers Excel
"""

import streamlit as st
import pandas as pd
from translator import MultilingualTranslator
import io
import traceback


# Configuration de la page
st.set_page_config(
    page_title="Traducteur Multilingue Excel",
    page_icon="🌍",
    layout="wide"
)

# Titre et description
st.title("🌍 Traducteur Multilingue Excel")
st.markdown("""
Cette application traduit automatiquement les colonnes B à H de votre fichier Excel en 7 langues :
**Français**, **Anglais**, **Allemand**, **Espagnol**, **Italien**, **Néerlandais**, **Portugais**

La langue source est détectée automatiquement.
""")

# Sidebar pour la configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Récupérer la clé API depuis les secrets Streamlit
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
        st.success("✅ Clé API chargée")
    except:
        st.error("❌ Clé API non trouvée")
        api_key = st.text_input(
            "Clé API OpenAI",
            type="password",
            help="Entrez votre clé API OpenAI"
        )
    
    st.divider()
    
    st.markdown("### 📊 Colonnes à traduire")
    st.info("Colonnes B à H (configurables)")
    
    # Configuration des colonnes (avec possibilité de personnaliser)
    default_columns = ['B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    with st.expander("Personnaliser les colonnes"):
        columns_input = st.text_input(
            "Colonnes à traduire",
            value=", ".join(default_columns),
            help="Séparez les noms de colonnes par des virgules"
        )
        columns_to_translate = [col.strip() for col in columns_input.split(",")]
    
    st.divider()
    
    st.markdown("### 🔧 Paramètres avancés")
    model = st.selectbox(
        "Modèle OpenAI",
        options=["gpt-4.1-mini", "gpt-4o-mini", "gpt-4o"],
        index=0,
        help="Sélectionnez le modèle à utiliser pour la traduction"
    )

# Zone principale
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📁 Importer votre fichier")
    uploaded_file = st.file_uploader(
        "Choisissez un fichier Excel (.xlsx, .xls)",
        type=['xlsx', 'xls'],
        help="Le fichier doit contenir les colonnes B à H à traduire"
    )

with col2:
    st.header("ℹ️ Instructions")
    st.markdown("""
    1. Uploadez votre fichier Excel
    2. Vérifiez l'aperçu
    3. Cliquez sur "Traduire"
    4. Téléchargez le résultat
    """)

# Afficher un aperçu du fichier uploadé
if uploaded_file is not None:
    try:
        df_preview = pd.read_excel(uploaded_file)
        
        st.subheader("📋 Aperçu du fichier")
        st.dataframe(df_preview.head(10), use_container_width=True)
        
        # Informations sur le fichier
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("Nombre de lignes", len(df_preview))
        with col_info2:
            st.metric("Nombre de colonnes", len(df_preview.columns))
        with col_info3:
            # Vérifier si les colonnes à traduire existent
            missing_cols = [col for col in columns_to_translate if col not in df_preview.columns]
            if missing_cols:
                st.warning(f"⚠️ Colonnes manquantes : {', '.join(missing_cols)}")
            else:
                st.success("✅ Toutes les colonnes présentes")
        
        st.divider()
        
        # Bouton de traduction
        if st.button("🚀 Lancer la traduction", type="primary", use_container_width=True):
            if not api_key:
                st.error("❌ Veuillez configurer votre clé API OpenAI dans la barre latérale")
            else:
                # Initialiser le traducteur
                translator = MultilingualTranslator(api_key=api_key, model=model)
                
                # Créer des conteneurs pour les messages
                status_container = st.container()
                progress_container = st.container()
                
                with status_container:
                    st.info("🔍 Détection de la langue source...")
                
                try:
                    # Réinitialiser le curseur du fichier
                    uploaded_file.seek(0)
                    
                    # Détecter la langue
                    df_temp = pd.read_excel(uploaded_file)
                    source_lang = translator.detect_language(df_temp, columns_to_translate)
                    
                    status_container.success(f"✅ Langue source détectée : **{translator.SUPPORTED_LANGUAGES[source_lang].upper()}**")
                    
                    # Obtenir les langues cibles
                    target_languages = translator.get_target_languages(source_lang)
                    
                    st.info(f"📝 Traduction vers : {', '.join([translator.SUPPORTED_LANGUAGES[lang] for lang in target_languages])}")
                    
                    # Créer un dictionnaire pour stocker les traductions
                    all_translations = {source_lang: df_temp.copy()}
                    
                    # Barre de progression globale
                    overall_progress = progress_container.progress(0)
                    status_text = progress_container.empty()
                    
                    # Traduire vers chaque langue
                    total_langs = len(target_languages)
                    
                    for idx, target_lang in enumerate(target_languages):
                        status_text.text(f"Traduction en cours : {translator.SUPPORTED_LANGUAGES[target_lang]}...")
                        
                        # Créer une barre de progression pour cette langue
                        lang_progress = progress_container.progress(0)
                        
                        def update_progress(progress):
                            lang_progress.progress(progress)
                        
                        df_translated = translator.translate_dataframe(
                            df_temp,
                            columns_to_translate,
                            source_lang,
                            target_lang,
                            progress_callback=update_progress
                        )
                        
                        all_translations[target_lang] = df_translated
                        
                        # Mettre à jour la progression globale
                        overall_progress.progress((idx + 1) / total_langs)
                        lang_progress.empty()
                    
                    status_text.text("✅ Traduction terminée !")
                    
                    # Créer le fichier Excel en mémoire
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        for lang, df in all_translations.items():
                            df.to_excel(writer, sheet_name=lang, index=False)
                    
                    output.seek(0)
                    
                    # Afficher les résultats
                    st.success("🎉 Traduction terminée avec succès !")
                    
                    # Bouton de téléchargement
                    st.download_button(
                        label="📥 Télécharger le fichier traduit",
                        data=output,
                        file_name="traductions_multilingues.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True
                    )
                    
                    # Aperçu des traductions
                    st.subheader("👀 Aperçu des traductions")
                    
                    tabs = st.tabs([translator.SUPPORTED_LANGUAGES[lang].upper() for lang in all_translations.keys()])
                    
                    for tab, (lang, df) in zip(tabs, all_translations.items()):
                        with tab:
                            st.dataframe(df.head(10), use_container_width=True)
                
                except Exception as e:
                    st.error(f"❌ Erreur lors de la traduction : {str(e)}")
                    with st.expander("Détails de l'erreur"):
                        st.code(traceback.format_exc())
    
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier : {str(e)}")
        st.info("Assurez-vous que le fichier est un fichier Excel valide (.xlsx ou .xls)")

else:
    st.info("👆 Commencez par uploader un fichier Excel")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Développé avec ❤️ par Woodbrass | Powered by OpenAI GPT-4.1-mini</p>
</div>
""", unsafe_allow_html=True)
