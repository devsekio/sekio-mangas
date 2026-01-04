import requests
import os
import time
from flask import Flask
from models import db, Manga
from deep_translator import GoogleTranslator

# LISTA CONFIRMADA DE ÉXITOS EN MANGAPLUS (Enero 2026)
MANGAPLUS_HITS = [
    #"One Piece", "Jujutsu Kaisen", "Chainsaw Man", "Boruto: Two Blue Vortex",
    #"Spy x Family", "Kaiju No. 8", "Dandadan", "Sakamoto Days",
    "My Hero Academia", "Black Clover", "Blue Box", "Kagurabachi",
    #"Oshi no Ko", "Dragon Ball Super", "Blue Exorcist", "Bleach",
    #"Undead Unluck", "Mission: Yozakura Family", "Witch Watch", "Akane-banashi",
    #"Mashle", "The Elusive Samurai", "Me & Roboco", "Kill Blue",
    #"Marriage Toxin", "Kindergarten WARS", "Choujin X", "Heart Gear",
    #"RuriDragon", "Gokurakugai", "Show-ha Shoten!", "World Trigger",
    #"Twin Star Exorcists", "Seraph of the End", "Platinum End",
    #"Terra Formars", "Hell's Paradise: Jigokuraku", "Summer Time Rendering",
    #"Claymore", "Death Note", "Naruto", "Demon Slayer", "Dr. STONE"
]

def create_app():
    app = Flask(__name__)
    
    # --- CONFIGURACIÓN PARA LA NUBE ---
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mangas.db'
    # ----------------------------------
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def fetch_specific_manga(title):
    """Busca un manga específico por nombre en Jikan"""
    print(f"   Buscando datos para: {title}...")
    try:
        # Buscamos por nombre (?q=Title)
        url = "https://api.jikan.moe/v4/manga"
        params = {"q": title, "limit": 1, "type": "manga"} 
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                return data['data'][0] # Devolvemos el primer resultado
    except Exception as e:
        print(f"Error conectando: {e}")
    return None

def fetch_mp_catalog():
    app = create_app()
    
    # Si borraste la DB manual, esto la regenera
    with app.app_context():
        db.create_all()

    with app.app_context():
        count_new = 0
        
        print(f"🚀 Iniciando carga del catálogo MangaPlus ({len(MANGAPLUS_HITS)} series)...")
        
        for title in MANGAPLUS_HITS:
            manga_data = fetch_specific_manga(title)
            
            if manga_data:
                # Verificar si ya existe por MAL ID
                exists = Manga.query.filter_by(mal_id=manga_data['mal_id']).first()
                
                if not exists:
                    new_manga = Manga(
                        mal_id=manga_data['mal_id'],
                        title=manga_data['title'],
                        image_url=manga_data['images']['jpg']['large_image_url'], # Mejor calidad
                        synopsis=GoogleTranslator(source='en', target='es').translate(manga_data['synopsis']) if manga_data['synopsis'] else "",
                        status=manga_data['status']
                    )
                    db.session.add(new_manga)
                    print(f"      ✅ Guardado: {manga_data['title']}")
                    count_new += 1
                else:
                    print(f"      🔹 Ya existe: {manga_data['title']}")
            else:
                print(f"      ❌ No encontrado en Jikan: {title}")

            # Pausa OBLIGATORIA para Jikan (evita errores 429)
            time.sleep(1.5)

        try:
            db.session.commit()
            print(f"\n✨ ¡Terminado! Se agregaron {count_new} mangas al catálogo.")
        except Exception as e:
            print(f"Error guardando DB: {e}")

if __name__ == '__main__':
    fetch_mp_catalog()