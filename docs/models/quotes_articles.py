from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class QuoteArticles(Base):
    __tablename__ = 'cotizacionarticulo'
    Id = Column(Integer, primary_key=True)
    Cantidad = Column(Integer)
    Articulos_Id = Column(Integer, ForeignKey('articulos.Id'))
    Cotizaciones_Id = Column(Integer, ForeignKey('cotizaciones.Id'))

    def add(quantity, id_article, id_quote):
        with session_scope() as session:
            new_quote_article = QuoteArticles(Cantidad=quantity, Articulos_Id=id_article, Cotizaciones_Id=id_quote)
            session.add(new_quote_article)
            return True
        
    def edit(id_quote_article, quantity):
        with session_scope() as session:
            edit_quote_article = session.get(QuoteArticles, id_quote_article)
            if edit_quote_article:
                edit_quote_article.Cantidad = quantity
                return True
    
    def delete(id_quote_article):
        with session_scope() as session:
            quote_article = session.get(QuoteArticles, id_quote_article)
            if quote_article:
                session.delete(quote_article)
                return True

    # def save(note, id_quote_article):
    #     with session_scope() as session:
    #         save_note = session.get(QuoteArticles, id_quote_article)
    #         if save_note:
    #             save_note.Nota = note
    #             return True

    def find_quote_article(id_quote):
        with session_scope() as session:
            quotes_articles = session.query(QuoteArticles).filter(QuoteArticles.Cotizaciones_Id == id_quote).all()
            quotes_articles_list = [
                {
                    "id": quote_article.Id,
                    "quantity": quote_article.Cantidad,
                    "id_article": quote_article.Articulos_Id,
                }
                for quote_article in quotes_articles
            ]
            return quotes_articles_list

    def get_quantity_quote_article(id_quote_article):
        with session_scope() as session:
            quote_article = session.query(QuoteArticles).filter(QuoteArticles.Id == id_quote_article).first()
            if quote_article:
                return quote_article.Cantidad
            else:
                return "nota no encontrada"

    def find_id(id_article, id_quote):
        with session_scope() as session:
            quote_article = session.query(QuoteArticles).filter(QuoteArticles.Articulos_Id == id_article, QuoteArticles.Cotizaciones_Id == id_quote).first()
            if quote_article:
                return {
                    "id": quote_article.Id,
                }
            else:
                return "nota no encontrada"

