#!/usr/bin/env python3
"""
Script CLI pour traduire des fichiers Excel en ligne de commande
"""

import argparse
import os
import sys
from translator import MultilingualTranslator


def main():
    parser = argparse.ArgumentParser(
        description='Traducteur multilingue Excel via OpenAI API'
    )
    
    parser.add_argument(
        'input_file',
        help='Fichier Excel source'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='traductions.xlsx',
        help='Fichier Excel de sortie (défaut: traductions.xlsx)'
    )
    
    parser.add_argument(
        '-k', '--api-key',
        help='Clé API OpenAI (ou variable d\'environnement OPENAI_API_KEY)'
    )
    
    parser.add_argument(
        '-m', '--model',
        default='gpt-4.1-mini',
        help='Modèle OpenAI à utiliser (défaut: gpt-4.1-mini)'
    )
    
    parser.add_argument(
        '-c', '--columns',
        default='B,C,D,E,F,G,H',
        help='Colonnes à traduire, séparées par des virgules (défaut: B,C,D,E,F,G,H)'
    )
    
    args = parser.parse_args()
    
    # Vérifier que le fichier existe
    if not os.path.exists(args.input_file):
        print(f"❌ Erreur : Le fichier {args.input_file} n'existe pas")
        sys.exit(1)
    
    # Récupérer la clé API
    api_key = args.api_key or os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ Erreur : Clé API OpenAI non fournie")
        print("Utilisez --api-key ou définissez la variable OPENAI_API_KEY")
        sys.exit(1)
    
    # Parser les colonnes
    columns = [col.strip() for col in args.columns.split(',')]
    
    print(f"🚀 Démarrage de la traduction...")
    print(f"   Fichier source : {args.input_file}")
    print(f"   Colonnes : {', '.join(columns)}")
    print(f"   Modèle : {args.model}")
    
    try:
        # Initialiser le traducteur
        translator = MultilingualTranslator(api_key=api_key, model=args.model)
        
        # Traiter le fichier
        print("\n🔍 Détection de la langue source...")
        translations, source_lang = translator.process_excel_file(
            args.input_file,
            columns
        )
        
        print(f"✅ Langue source : {translator.SUPPORTED_LANGUAGES[source_lang].upper()}")
        
        # Sauvegarder
        print(f"\n💾 Sauvegarde vers {args.output}...")
        translator.save_translations_to_excel(translations, args.output)
        
        print(f"\n✅ Traduction terminée avec succès !")
        print(f"   Langues générées : {', '.join([translator.SUPPORTED_LANGUAGES[lang] for lang in translations.keys()])}")
        print(f"   Fichier de sortie : {args.output}")
        
    except Exception as e:
        print(f"\n❌ Erreur : {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
