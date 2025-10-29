from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class ArtiNomen(Base):
    __tablename__ = 'artinomen'
    Id = Column(Integer, primary_key=True)
    Cantidad = Column(Integer)
    Articulos_Id = Column(Integer, ForeignKey('articulos.Id'))
    Nomenclaturas_Id = Column(Integer, ForeignKey('nomenclaturas.Id'))

    def add(quantity, id_article, id_nomenclature):
        with session_scope() as session:
            new_artinomen = ArtiNomen(Cantidad=quantity, Articulos_Id=id_article, Nomenclaturas_Id=id_nomenclature)
            session.add(new_artinomen)
            session.flush()
            return new_artinomen.Id

    def edit(id_artinomen, quantity):
        with session_scope() as session:
            edit_artinomen = session.query(ArtiNomen).get(id_artinomen)
            if edit_artinomen:
                edit_artinomen.Cantidad = quantity
                return True
    
    def delete(id_artinomen):
        with session_scope() as session:
            artinomen = session.query(ArtiNomen).get(id_artinomen)
            if artinomen:
                session.delete(artinomen)
                return True
            
    def find_artinomen_article(id_nomenclature):
        with session_scope() as session:
            artinomens_objets = session.query(ArtiNomen).filter(ArtiNomen.Nomenclaturas_Id == id_nomenclature).all()
            artinomens_list = [
                {
                    "id": artinomen.Id,
                    "quantity": artinomen.Cantidad,
                    "id_article": artinomen.Articulos_Id,
                }
                for artinomen in artinomens_objets
            ]
            return artinomens_list

    def get_quantity(id_artinomen):
        with session_scope() as session:
            artinomen = session.query(ArtiNomen).filter(ArtiNomen.Id == id_artinomen).first()
            if artinomen:
                return artinomen.Cantidad
            else:
                return "Artinomen no encontrada"

    def find_id(id_article, id_nomenclature):
        with session_scope() as session:
            artinomen = session.query(ArtiNomen.Id).filter(ArtiNomen.Articulos_Id == id_article, ArtiNomen.Nomenclaturas_Id == id_nomenclature).first()
            if artinomen:
                return {
                    "id": artinomen.Id,
                }
            else:
                return "Artinomen no encontrada"
