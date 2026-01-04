from flask_sqlalchemy import SQLAlchemy
from typing import List

db = SQLAlchemy()

class Manga(db.Model):
    __tablename__ = 'manga'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(500))
    synopsis = db.Column(db.Text)
    status = db.Column(db.String(50))
    genres = db.Column(db.String(255))
    mal_id = db.Column(db.Integer, unique=True, nullable=True)

    # Relationship
    links = db.relationship('Link', back_populates='manga', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Manga {self.title}>'

class Link(db.Model):
    __tablename__ = 'link'

    id = db.Column(db.Integer, primary_key=True)
    manga_id = db.Column(db.Integer, db.ForeignKey('manga.id'), nullable=False)
    site_name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    type_ = db.Column('type', db.String(20), nullable=False)  # 'read' or 'buy'

    # Relationship
    manga = db.relationship('Manga', back_populates='links')

    def __repr__(self):
        return f'<Link {self.site_name} - {self.type_}>'
