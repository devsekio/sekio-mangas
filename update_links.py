import time
import os
import urllib.parse
from flask import Flask
from models import db, Manga, Link
import requests

# Intentamos importar la librería de búsqueda (para lo que no esté en el mapa)
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

# --- PLAN A: EL MAPA DEL TESORO ---
# IDs confirmados de MangaPlus para los éxitos (Enero 2026)
# Esto garantiza que los botones de los mangas importantes SIEMPRE aparezcan.
KNOWN_IDS = {
    "One Piece": "100020",
    "Jujutsu Kaisen": "100034",
    "Chainsaw Man": "100037",
    "Boruto: Two Blue Vortex": "100269",
    "My Hero Academia": "100017",
    "Spy x Family": "100056",
    "Dragon Ball Super": "100012",
    "Black Clover": "100003",
    "Dandadan": "100032",
    "Kaiju No. 8": "100058",
    "Sakamoto Days": "100033",
    "Blue Box": "100040",
    "Oshi no Ko": "100191",
    "Kagurabachi": "100274",
    "Undead Unluck": "100026",
    "Mashle": "100029",
    "Mission: Yozakura Family": "100024",
    "Bleach": "100014",
    "Naruto": "100009",
    "Demon Slayer: Kimetsu no Yaiba": "100007",
    "Dr. STONE": "100010",
    "Claymore": "100094",
    "Death Note": "100008",
    "Blue Exorcist": "100004",
    "Seraph of the End": "100005",
    "Twin Star Exorcists": "100011",
    "World Trigger": "100002",
    "Witch Watch": "100028",
    "Akane-banashi": "100092",
    "RuriDragon": "100144",
    "Gokurakugai": "100155"
}

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

def get_jikan_links(mal_id):
    """Consulta rápida a la API oficial de MyAnimeList/Jikan"""
    url = f"https://api.jikan.moe/v4/manga/{mal_id}/external"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 429: 
            time.sleep(2)
            return get_jikan_links(mal_id)
        return response.json().get('data', []) if response.status_code == 200 else []
    except:
        return []

def search_mangaplus_smart(title):
    """Plan B: El Detective (Buscador)"""
    if not DDGS: return None
    
    # Intento de búsqueda simplificado
    try:
        query = f"{title} manga plus"
        with DDGS() as ddgs:
            # Pedimos 3 resultados
            results = list(ddgs.text(query, max_results=3))
            
            for res in results:
                url = res.get('href') or res.get('link')
                if url and "mangaplus.shueisha.co.jp/titles/" in url:
                    return url.split('?')[0]
    except Exception:
        pass # Si falla, falla en silencio
    return None

def update_links():
    app = create_app()
    
    with app.app_context():
        print("🔧 Iniciando actualización de enlaces...")
        
        # Limpieza inicial
        try:
            db.session.query(Link).delete()
            db.session.commit()
            print("🗑️  Links antiguos eliminados.")
        except Exception:
            print("❌ Error: La base de datos está bloqueada. Cierra 'python app.py'.")
            return

        mangas = Manga.query.all()
        total_links = 0
        
        for index, manga in enumerate(mangas):
            found_url = None
            source = ""
            
            # --- 1. REVISAR MAPA MANUAL (Plan A - Infalible) ---
            # Buscamos coincidencias aproximadas o exactas en nuestro diccionario
            for key_title, mp_id in KNOWN_IDS.items():
                # Si el título del manga contiene el nombre clave (ej: "One Piece" está en "One Piece")
                if key_title.lower() in manga.title.lower():
                    found_url = f"https://mangaplus.shueisha.co.jp/titles/{mp_id}"
                    source = "MAPA MAESTRO"
                    break
            
            # --- 2. REVISAR API JIKAN (Plan B) ---
            if not found_url:
                external_data = get_jikan_links(manga.mal_id)
                for site in external_data:
                    url = site.get('url', '').lower()
                    if 'mangaplus.shueisha.co.jp/titles/' in url:
                        found_url = site.get('url')
                        source = "API Jikan"
                        break
            
            # --- 3. REVISAR DETECTIVE (Plan C) ---
            if not found_url:
                found_url = search_mangaplus_smart(manga.title)
                if found_url:
                    source = "Detective"

            # --- RESULTADO ---
            print(f"[{index+1}/{len(mangas)}] {manga.title}")
            
            if found_url:
                db.session.add(Link(manga_id=manga.id, site_name='MangaPlus', url=found_url, type_='read'))
                print(f"   ✅ LINK AGREGADO ({source}): {found_url}")
                total_links += 1
            else:
                print("   ❌ No encontrado (Añadir al mapa manual si existe)")

            # Siempre añadir Amazon
            encoded_title = urllib.parse.quote(manga.title)
            amz_url = f"https://www.amazon.com/s?k={encoded_title}&i=stripbooks"
            db.session.add(Link(manga_id=manga.id, site_name='Amazon', url=amz_url, type_='buy'))

            # Pausa pequeña
            time.sleep(0.5)
        
        try:
            db.session.commit()
            print(f"\n✨ ¡ÉXITO! Total enlaces de lectura: {total_links}")
        except Exception as e:
            print(f"Error final: {e}")

if __name__ == '__main__':
    update_links()