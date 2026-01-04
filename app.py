import os
from flask import Flask, render_template, request
from models import db, Manga, Link

# --- IMPORTACIÓN INTELIGENTE DE TUS SCRIPTS ---
# Esto evita errores si tu archivo se llama diferente
try:
    from fetch_mangas import fetch_mp_catalog as fetch_script
except ImportError:
    from fetch_mangas import fetch_top_mangas as fetch_script

from update_links import update_links as links_script
# -----------------------------------------------

app = Flask(__name__)

# Configuración de Base de Datos (Detecta si es Nube o Local)
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mangas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# --- RUTA SECRETA DE INSTALACIÓN ---
# --- RUTAS DE INSTALACIÓN SEPARADAS ---
@app.route('/setup-1-mangas')
def setup_mangas():
    try:
        with app.app_context():
            db.create_all() # Asegura que la tabla exista
            fetch_script()  # Descarga solo los mangas
        return "<h1>✅ Paso 1 Completado: Mangas Descargados. <br><a href='/setup-2-links'>Ir al Paso 2 (Links)</a></h1>"
    except Exception as e:
        return f"<h1>Error en Paso 1: {str(e)}</h1>"

@app.route('/setup-2-links')
def setup_links():
    try:
        with app.app_context():
            links_script() # Busca solo los links
        return "<h1>✅ Paso 2 Completado: Links Generados. <br><a href='/'>¡IR AL INICIO!</a></h1>"
    except Exception as e:
        return f"<h1>Error en Paso 2: {str(e)}</h1>"
# --------------------------------------
@app.route('/')
def index():
    mangas = Manga.query.all()
    return render_template('index.html', mangas=mangas)

@app.route('/manga/<int:manga_id>')
def manga_detail(manga_id):
    manga = Manga.query.get_or_404(manga_id)
    return render_template('detail.html', manga=manga, links=manga.links)

@app.route('/search')
def search():
    query = request.args.get('q')
    if query:
        mangas = Manga.query.filter(Manga.title.ilike(f'%{query}%')).all()
    else:
        mangas = []
    return render_template('index.html', mangas=mangas)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

if __name__ == '__main__':
    app.run(debug=True)