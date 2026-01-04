import os
from deep_translator import GoogleTranslator
from app import app
from models import db, Manga
import time

def translate_synopses():
    translator = GoogleTranslator(source='en', target='es')
    
    with app.app_context():
        mangas = Manga.query.all()
        total = len(mangas)
        print(f"Iniciando traducción de {total} mangas...")
        
        for i, manga in enumerate(mangas):
            if manga.synopsis and len(manga.synopsis) > 10:
                try:
                    # Translate in chunks if necessary (GoogleTranslator has a limit of 5000 chars)
                    translated = translator.translate(manga.synopsis)
                    manga.synopsis = translated
                    print(f"[{i+1}/{total}] Traducido: {manga.title}")
                    
                    # Be nice to the service
                    time.sleep(0.5)
                    
                    # Commit every 5 to avoid losing progress
                    if (i + 1) % 5 == 0:
                        db.session.commit()
                        
                except Exception as e:
                    print(f"Error traduciendo {manga.title}: {e}")
        
        db.session.commit()
        print("Traducción completada.")

if __name__ == '__main__':
    translate_synopses()
