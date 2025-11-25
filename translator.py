"""
Module de traduction multilingue utilisant l'API OpenAI
"""

import pandas as pd
from langdetect import detect
from openai import OpenAI
import time
from typing import List, Dict, Tuple


class MultilingualTranslator:
    """Classe pour gérer la traduction multilingue de fichiers Excel"""
    
    SUPPORTED_LANGUAGES = {
        'FR': 'français',
        'EN': 'anglais',
        'DE': 'allemand',
        'ES': 'espagnol',
        'IT': 'italien',
        'NL': 'néerlandais',
        'PT': 'portugais'
    }
    
    LANG_CODE_MAPPING = {
        'fr': 'FR',
        'en': 'EN',
        'de': 'DE',
        'es': 'ES',
        'it': 'IT',
        'nl': 'NL',
        'pt': 'PT'
    }
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialise le traducteur
        
        Args:
            api_key: Clé API OpenAI
            model: Modèle OpenAI à utiliser
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def detect_language(self, df: pd.DataFrame, columns: List[str]) -> str:
        """
        Détecte la langue source à partir des premières lignes du DataFrame
        
        Args:
            df: DataFrame pandas
            columns: Liste des colonnes à analyser
            
        Returns:
            Code langue (FR, EN, DE, etc.)
        """
        # Collecter du texte des premières lignes
        sample_texts = []
        for col in columns:
            if col in df.columns:
                for idx in range(min(5, len(df))):
                    try:
                        text = str(df[col].iloc[idx])
                        if text and text != 'nan' and text != 'None' and len(text) > 10:
                            sample_texts.append(text)
                    except Exception:
                        continue
        
        if not sample_texts:
            # Par défaut, retourner FR si aucun texte n'est disponible
            return 'FR'
        
        # Détecter la langue sur plusieurs échantillons
        detected_langs = []
        for text in sample_texts[:10]:  # Analyser jusqu'à 10 échantillons
            try:
                lang = detect(text)
                if lang in self.LANG_CODE_MAPPING:
                    detected_langs.append(lang)
            except Exception:
                # Ignorer les erreurs de détection
                continue
        
        if not detected_langs:
            # Par défaut, retourner FR si la détection échoue
            return 'FR'
        
        # Prendre la langue la plus fréquente
        most_common = max(set(detected_langs), key=detected_langs.count)
        
        # Convertir en code langue supporté
        source_lang = self.LANG_CODE_MAPPING.get(most_common, 'FR')
        
        return source_lang
    
    def get_target_languages(self, source_lang: str) -> List[str]:
        """
        Retourne la liste des langues cibles (toutes sauf la source)
        
        Args:
            source_lang: Code langue source
            
        Returns:
            Liste des codes langues cibles
        """
        return [lang for lang in self.SUPPORTED_LANGUAGES.keys() if lang != source_lang]
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Traduit un texte via l'API OpenAI
        
        Args:
            text: Texte à traduire
            source_lang: Langue source
            target_lang: Langue cible
            
        Returns:
            Texte traduit
        """
        if not text or text.strip() == '' or str(text) == 'nan':
            return text
        
        source_name = self.SUPPORTED_LANGUAGES[source_lang]
        target_name = self.SUPPORTED_LANGUAGES[target_lang]
        
        prompt = f"""Traduis le texte suivant du {source_name} vers le {target_name}.
Fournis uniquement la traduction, sans commentaire ni explication.
Si le texte contient des termes techniques ou des noms de marque, conserve-les tels quels.

Texte à traduire :
{text}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Tu es un traducteur professionnel spécialisé dans les contenus techniques et marketing."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            translated = response.choices[0].message.content.strip()
            return translated
            
        except Exception as e:
            print(f"Erreur lors de la traduction : {e}")
            return f"[ERREUR: {text}]"
    
    def translate_dataframe(
        self, 
        df: pd.DataFrame, 
        columns_to_translate: List[str],
        source_lang: str,
        target_lang: str,
        progress_callback=None
    ) -> pd.DataFrame:
        """
        Traduit les colonnes spécifiées d'un DataFrame
        
        Args:
            df: DataFrame source
            columns_to_translate: Liste des colonnes à traduire
            source_lang: Langue source
            target_lang: Langue cible
            progress_callback: Fonction de callback pour suivre la progression
            
        Returns:
            DataFrame traduit
        """
        df_translated = df.copy()
        total_cells = len(df) * len(columns_to_translate)
        current_cell = 0
        
        for col in columns_to_translate:
            if col not in df.columns:
                continue
                
            for idx in range(len(df)):
                original_text = str(df[col].iloc[idx])
                
                if original_text and original_text != 'nan':
                    translated_text = self.translate_text(
                        original_text,
                        source_lang,
                        target_lang
                    )
                    df_translated.at[idx, col] = translated_text
                    
                    # Petit délai pour éviter les rate limits
                    time.sleep(0.1)
                
                current_cell += 1
                if progress_callback:
                    progress_callback(current_cell / total_cells)
        
        return df_translated
    
    def process_excel_file(
        self,
        input_file,
        columns_to_translate: List[str],
        progress_callback=None
    ) -> Tuple[Dict[str, pd.DataFrame], str]:
        """
        Traite un fichier Excel complet et génère toutes les traductions
        
        Args:
            input_file: Fichier Excel (file-like object ou chemin)
            columns_to_translate: Liste des colonnes à traduire (ex: ['B', 'C', 'D', 'E', 'F', 'G', 'H'])
            progress_callback: Fonction de callback pour suivre la progression
            
        Returns:
            Tuple (dictionnaire {langue: DataFrame}, langue_source)
        """
        # Charger le fichier
        df_source = pd.read_excel(input_file)
        
        # Détecter la langue source
        source_lang = self.detect_language(df_source, columns_to_translate)
        
        # Créer un dictionnaire pour stocker tous les DataFrames
        all_translations = {source_lang: df_source.copy()}
        
        # Obtenir les langues cibles
        target_languages = self.get_target_languages(source_lang)
        
        # Traduire vers chaque langue cible
        for target_lang in target_languages:
            if progress_callback:
                progress_callback(f"Traduction vers {self.SUPPORTED_LANGUAGES[target_lang]}...")
            
            df_translated = self.translate_dataframe(
                df_source,
                columns_to_translate,
                source_lang,
                target_lang,
                progress_callback=None  # Gérer la progression au niveau supérieur
            )
            
            all_translations[target_lang] = df_translated
        
        return all_translations, source_lang
    
    def save_translations_to_excel(
        self,
        translations: Dict[str, pd.DataFrame],
        output_file: str
    ):
        """
        Sauvegarde toutes les traductions dans un fichier Excel multi-feuilles
        
        Args:
            translations: Dictionnaire {langue: DataFrame}
            output_file: Chemin du fichier de sortie
        """
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for lang, df in translations.items():
                df.to_excel(writer, sheet_name=lang, index=False)
