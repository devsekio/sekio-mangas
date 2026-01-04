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
@app.route('/setup-inicial')
def setup_inicial():
    try:
        # 1. Crear las tablas vacías (si no existen)
        with app.app_context():
            db.create_all()
            
            # 2. Ejecutar la descarga de mangas
            # (Llamamos a la función importada arriba)
            fetch_script() 
            
            # 3. Generar los enlaces
            links_script()
            
        return """
        <div style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1 style="color: green;">¡ÉXITO TOTAL! 🚀</h1>
            <p>La base de datos se ha llenado correctamente.</p>
            <a href="/" style="background: #6366f1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ir al Inicio</a>
        </div>
        """
    except Exception as e:
        return f"<h1>Hubo un error: {str(e)}</h1>"
# -----------------------------------

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