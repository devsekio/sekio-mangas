from flask import Flask
from models import db, Manga, Link

def setup_database():
    app = Flask(__name__)
    # Configuración de la base de datos SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mangas.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        print("Base de datos 'mangas.db' creada correctamente con las tablas Manga y Link.")

if __name__ == '__main__':
    setup_database()
