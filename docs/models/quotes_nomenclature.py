from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class QuoteNomenclature(Base):
    __tablename__ = 'cotizacionnomenclatura'
    Id = Column(Integer, primary_key=True)
    Cantidad = Column(Integer)
    Nomenclaturas_Id = Column(Integer, ForeignKey('nomenclaturas.Id'))
    Cotizaciones_Id = Column(Integer, ForeignKey('cotizaciones.Id'))

    def add(quantity, id_nomenclature, id_quote):
        with session_scope() as session:
            new_quote_article = QuoteNomenclature(Cantidad=quantity, Nomenclaturas_Id=id_nomenclature, Cotizaciones_Id=id_quote)
            session.add(new_quote_article)
            return True
        
    def edit(id_quote_nomenclature, quantity):
        with session_scope() as session:
            edit_quote_article = session.get(QuoteNomenclature, id_quote_nomenclature)
            if edit_quote_article:
                edit_quote_article.Cantidad = quantity
                return True
    
    def delete(id_quote_nomenclature):
        with session_scope() as session:
            quote_article = session.get(QuoteNomenclature, id_quote_nomenclature)
            if quote_article:
                session.delete(quote_article)
                return True

    # def save(note, id_quote_nomenclature):
    #     with session_scope() as session:
    #         save_note = session.query(QuoteNomenclature).get(id_quote_nomenclature)
    #         if save_note:
    #             save_note.Nota = note
    #             return True

    def find_quote_nomenclature(id_quote):
        with session_scope() as session:
            quotes_nomenclatures = session.query(QuoteNomenclature).filter(QuoteNomenclature.Cotizaciones_Id == id_quote).all()
            quotes_nomenclatures_list = [
                {
                    "id": quote_nomenclature.Id,
                    "quantity": quote_nomenclature.Cantidad,
                    "id_nomenclature": quote_nomenclature.Nomenclaturas_Id,
                }
                for quote_nomenclature in quotes_nomenclatures
            ]
            return quotes_nomenclatures_list

    def get_quantity_nomenclature(id_quote_nomenclature):
        with session_scope() as session:
            quote_nomenclature = session.query(QuoteNomenclature).filter(QuoteNomenclature.Id == id_quote_nomenclature).first()
            if quote_nomenclature:
                return quote_nomenclature.Cantidad
            else:
                return "nota no encontrada"

    def find_id(id_nomenclature, id_quote):
        with session_scope() as session:
            quote_nomenclature = session.query(QuoteNomenclature).filter(QuoteNomenclature.Nomenclaturas_Id == id_nomenclature, QuoteNomenclature.Cotizaciones_Id == id_quote).first()
            if quote_nomenclature:
                return {
                    "id": quote_nomenclature.Id,
                }
            else:
                return "nota no encontrada"

