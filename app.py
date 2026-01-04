import os
from flask import Flask, render_template, request
from models import db, Manga

app = Flask(__name__)

# Configuración de la base de datos
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mangas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy con la app
db.init_app(app)

@app.route('/')
def index():
    # Obtener todos los mangas de la base de datos
    mangas = Manga.query.all()
    # Pasa los mangas al template index.html (que crearemos en el siguiente paso)
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
