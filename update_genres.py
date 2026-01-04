import requests
import time
from app import app
from models import db, Manga

def update_existing_genres():
    with app.app_context():
        mangas = Manga.query.filter(Manga.genres == None).all()
        total = len(mangas)
        print(f"Actualizando géneros para {total} mangas...")
        
        for i, manga in enumerate(mangas):
            try:
                # Fetch full data for each manga to get genres
                api_url = f"https://api.jikan.moe/v4/manga/{manga.mal_id}"
                response = requests.get(api_url)
                response.raise_for_status()
                data = response.json().get('data', {})
                
                genres_list = data.get('genres', [])
                manga.genres = ', '.join([g['name'] for g in genres_list])
                
                print(f"[{i+1}/{total}] Actualizado: {manga.title} -> {manga.genres}")
                
                # Jikan rate limits: 3 requests per second
                time.sleep(0.4) 
                
                if (i + 1) % 10 == 0:
                    db.session.commit()
                    
            except Exception as e:
                print(f"Error actualizando {manga.title}: {e}")
                time.sleep(1) # Wait a bit before next retry
        
        db.session.commit()
        print("Actualización de géneros completada.")

if __name__ == '__main__':
    update_existing_genres()
