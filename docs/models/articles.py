from sqlalchemy import Column, Integer, String, ForeignKey, Float, select
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata
Base = declarative_base(metadata=metadata)

class Articles(Base):
    __tablename__ = 'articulos'
    Id = Column(Integer, primary_key=True)
    Revision = Column(String(2))
    Referencia = Column(String(50))
    ReferenciaProveedor = Column(String(50))
    DesignacionFR = Column(String(150))
    DesignacionEN = Column(String(150))
    DesignacionES = Column(String(150))
    Dimensiones = Column(String(50))
    Peso = Column(Float)
    CantidadStock = Column(Integer)
    PrecioCompraCLP = Column(Float)
    PrecioVentaCLP = Column(Float)
    PrecioCompraEUR = Column(Float)
    PrecioVentaEUR = Column(Float)
    ImagenURL = Column(String(500))
    PlanoURL = Column(String(500))
    NumeroAduana = Column(String(50))
    Empresas_Id = Column(Integer, ForeignKey('empresas.Id'))
    TiposFamilias_Id = Column(Integer, ForeignKey('tiposfamilias.Id'))
    Materias_Id = Column(Integer, ForeignKey('materias.Id'))
    TiposVentas_Id = Column(Integer, ForeignKey('tiposventas.Id'))

    def add(new_article_data):

        with session_scope() as session:
            articles = Articles(
                Revision=new_article_data["revision"], 
                Referencia=new_article_data["reference"], 
                ReferenciaProveedor=new_article_data["reference_provider"], 
                DesignacionFR=new_article_data["designation_fr"], 
                DesignacionEN=new_article_data["designation_en"], 
                DesignacionES=new_article_data["designation_es"], 
                Dimensiones=new_article_data["dimensions"], 
                Peso=new_article_data["weight"], 
                CantidadStock=new_article_data["quantity"], 
                PrecioCompraCLP=new_article_data["price_purchase_clp"], 
                PrecioVentaCLP=new_article_data["price_sale_clp"],
                PrecioCompraEUR=new_article_data["price_purchase_eur"],
                PrecioVentaEUR=new_article_data["price_sale_eur"], 
                ImagenURL=new_article_data["image_url"], 
                PlanoURL=new_article_data["plan_url"], 
                NumeroAduana=new_article_data["customs_number"], 
                Empresas_Id=new_article_data["id_company"], 
                TiposFamilias_Id=new_article_data["id_family_type"], 
                Materias_Id=new_article_data["id_matter"], 
                TiposVentas_Id=new_article_data["id_sale_type"])
            session.add(articles)
            return True

    def edit(edit_article_data):
        with session_scope() as session:
            article = session.query(Articles).filter_by(Id=edit_article_data["id_article"]).first()
            if article:
                article_attrs = {
                    'Revision': edit_article_data["revision"],
                    'Referencia': edit_article_data["reference"],
                    'ReferenciaProveedor': edit_article_data["reference_provider"],
                    'DesignacionFR': edit_article_data["designation_fr"],
                    'DesignacionEN': edit_article_data["designation_en"],
                    'DesignacionES': edit_article_data["designation_es"],
                    'Dimensiones': edit_article_data["dimensions"],
                    'Peso': edit_article_data["weight"],
                    'CantidadStock': edit_article_data["quantity"],
                    'PrecioCompraCLP': edit_article_data["price_purchase_clp"],
                    'PrecioVentaCLP': edit_article_data["price_sale_clp"],
                    'PrecioCompraEUR': edit_article_data["price_purchase_eur"],
                    'PrecioVentaEUR': edit_article_data["price_sale_eur"],
                    'ImagenURL': edit_article_data["image_url"],
                    'PlanoURL': edit_article_data["plan_url"],
                    'NumeroAduana': edit_article_data["customs_number"],
                    'Empresas_Id': edit_article_data["id_company"],
                    'Materias_Id': edit_article_data["id_matter"],
                    'TiposVentas_Id': edit_article_data["id_sale_type"],
                    'TiposFamilias_Id': edit_article_data["id_family_type"],
                }
                for attr, value in article_attrs.items():
                    if value and getattr(article, attr) != value:
                        setattr(article, attr, value)
                return True
            else:
                return False

    def delete(id_article):
        with session_scope() as session:
            articles = session.get(Articles, id_article)
            if articles:
                session.delete(articles)
                return True
            
    def read(id_article):
        with session_scope() as session:
            articles = session.query(Articles).filter_by(Id=id_article).first()
            if articles:
                return {
                    "revision": articles.Revision,
                    "reference": articles.Referencia,
                    "reference_provider": articles.ReferenciaProveedor,
                    "designation_fr": articles.DesignacionFR,
                    "designation_en": articles.DesignacionEN,
                    "designation_es": articles.DesignacionES,
                    "dimensions": articles.Dimensiones,
                    "weight": articles.Peso,
                    "stock_quantity": articles.CantidadStock,
                    "price_purchase_clp": articles.PrecioCompraCLP,
                    "price_sale_clp": articles.PrecioVentaCLP,
                    "price_purchase_eur": articles.PrecioCompraEUR,
                    "price_sale_eur": articles.PrecioVentaEUR,
                    "image_url": articles.ImagenURL,
                    "plan_url": articles.PlanoURL,
                    "customs_number": articles.NumeroAduana,
                    "id_company": articles.Empresas_Id,
                    "id_family_type": articles.TiposFamilias_Id,
                    "id_matter": articles.Materias_Id,
                    "id_sale_type": articles.TiposVentas_Id,
                }
            else:
                return "Articulo no encontrada"

    def read_only_designation(id_article):
        with session_scope() as session:
            articles = session.query(Articles).filter_by(Id=id_article).first()
            if articles:
                return {
                    "designation_fr": articles.DesignacionFR,
                    "designation_en": articles.DesignacionEN,
                    "designation_es": articles.DesignacionES,
                    "stock_quantity": articles.CantidadStock,
                }
            else:
                return "Articulo no encontrada"
    
    def read_all():
        with session_scope() as session:
            articles_objects = session.query(Articles).all()
            articles_list = [
                {
                    "id": article.Id,
                    "revision": article.Revision,
                    "reference": article.Referencia,
                    "reference_provider": article.ReferenciaProveedor,
                    "designation_fr": article.DesignacionFR,
                    "designation_en": article.DesignacionEN,
                    "designation_es": article.DesignacionES,
                    "dimensions": article.Dimensiones,
                    "weight": article.Peso,
                    "stock_quantity": article.CantidadStock,
                    "price_purchase_clp": article.PrecioCompraCLP,
                    "price_sale_clp": article.PrecioVentaCLP,
                    "price_purchase_eur": article.PrecioCompraEUR,
                    "price_sale_eur": article.PrecioVentaEUR,
                    "image_url": article.ImagenURL,
                    "plan_url": article.PlanoURL,
                    "customs_number": article.NumeroAduana,
                    "id_company": article.Empresas_Id,
                    "id_family_type": article.TiposFamilias_Id,
                    "id_matter": article.Materias_Id,
                    "id_sale_type": article.TiposVentas_Id,
                }
                for article in articles_objects
            ]
            return articles_list

    def latest_articles():

        with session_scope() as session:
            latest_articles_added = session.query(Articles).order_by(Articles.Id.desc()).limit(8).all()
            articles_list = [
                {
                    "id": article.Id,
                    "revision": article.Revision,
                    "reference": article.Referencia,
                    "reference_provider": article.ReferenciaProveedor,
                    "designation_fr": article.DesignacionFR,
                    "designation_en": article.DesignacionEN,
                    "designation_es": article.DesignacionES,
                    "dimensions": article.Dimensiones,
                    "weight": article.Peso,
                    "quantity": article.CantidadStock,
                    "price_purchase_clp": article.PrecioCompraCLP,
                    "price_sale_clp": article.PrecioVentaCLP,
                    "price_purchase_eur": article.PrecioCompraEUR,
                    "price_sale_eur": article.PrecioVentaEUR,
                    "image_url": article.ImagenURL,
                    "plan_url": article.PlanoURL,
                    "customs_number": article.NumeroAduana,
                    "id_company": article.Empresas_Id,
                    "id_family_type": article.TiposFamilias_Id,
                    "id_matter": article.Materias_Id,
                    "id_sale_type": article.TiposVentas_Id,
                }
                for article in latest_articles_added
            ]
            return articles_list

    def find_selected(name_article, designation):
        with session_scope() as session:
            articles = session.query(Articles).filter(getattr(Articles, designation)==name_article).first()
            if articles:
                return {
                    "id": articles.Id,
                    "revision": articles.Revision,
                    "reference": articles.Referencia,
                    "reference_provider": articles.ReferenciaProveedor,
                    "designation_fr": articles.DesignacionFR,
                    "designation_en": articles.DesignacionEN,
                    "designation_es": articles.DesignacionES,
                    "dimensions": articles.Dimensiones,
                    "weight": articles.Peso,
                    "stock_quantity": articles.CantidadStock,
                    "price_purchase_clp": articles.PrecioCompraCLP,
                    "price_sale_clp": articles.PrecioVentaCLP,
                    "price_purchase_eur": articles.PrecioCompraEUR,
                    "price_sale_eur": articles.PrecioVentaEUR,
                    "image_url": articles.ImagenURL,
                    "plan_url": articles.PlanoURL,
                    "customs_number": articles.NumeroAduana,
                    "id_company": articles.Empresas_Id,
                    "id_family_type": articles.TiposFamilias_Id,
                    "id_matter": articles.Materias_Id,
                    "id_sale_type": articles.TiposVentas_Id,
                }
            else:
                return "Articulo no encontrada"

    def find_articles(name_article, language):
        with session_scope() as session:
            if language == "es":
                article_found = session.query(Articles).filter(Articles.DesignacionES.like(f'%{name_article}%')).all()
            elif language == "en":
                article_found = session.query(Articles).filter(Articles.DesignacionEN.like(f'%{name_article}%')).all()
            else:
                article_found = session.query(Articles).filter(Articles.DesignacionFR.like(f'%{name_article}%')).all()
            articles_list = [
                {
                    "id": article.Id,
                    "revision": article.Revision,
                    "reference": article.Referencia,
                    "reference_provider": article.ReferenciaProveedor,
                    "designation_fr": article.DesignacionFR,
                    "designation_en": article.DesignacionEN,
                    "designation_es": article.DesignacionES,
                    "dimensions": article.Dimensiones,
                    "weight": article.Peso,
                    "stock_quantity": article.CantidadStock,
                    "price_purchase_clp": article.PrecioCompraCLP,
                    "price_sale_clp": article.PrecioVentaCLP,
                    "price_purchase_eur": article.PrecioCompraEUR,
                    "price_sale_eur": article.PrecioVentaEUR,
                    "image_url": article.ImagenURL,
                    "plan_url": article.PlanoURL,
                    "customs_number": article.NumeroAduana,
                    "id_company": article.Empresas_Id,
                    "id_family_type": article.TiposFamilias_Id,
                    "id_matter": article.Materias_Id,
                    "id_sale_type": article.TiposVentas_Id,
                }
                for article in article_found
            ]
            return articles_list

class FamilyTypes(Base):
    __tablename__ = 'tiposfamilias'
    Id = Column(Integer, primary_key=True)
    TipoFamilia = Column(String(50))

    def read():
        with session_scope() as session:
            result = session.query(FamilyTypes).all()
            family_types_list = [
                {
                    "id": article.Id,
                    "family_types": article.TipoFamilia,
                }
                for article in result
            ]
            return family_types_list
            
    def find_family_type(id_family_type):

        with session_scope() as session:
            family_type = session.query(FamilyTypes).filter_by(Id=id_family_type).first()
            if family_type:
                return family_type.TipoFamilia
            else:
                return "Articulo no encontrada"

class Matters(Base):
    __tablename__ = 'materias'
    Id = Column(Integer, primary_key=True)
    Materia = Column(String(50))
    
    def read():
        with session_scope() as session:
            result = session.query(Matters).all()
            matters_list = [
                {
                    "id": matter.Id,
                    "matters": matter.Materia,
                }
                for matter in result
            ]
            return matters_list

    def find_matter(id_matter):

        with session_scope() as session:
            matter = session.query(Matters).filter_by(Id=id_matter).first()
            if matter:
                return matter.Materia
            else:
                return "Articulo no encontrada"

class SalesTypes(Base):
    __tablename__ = 'tiposventas'
    Id = Column(Integer, primary_key=True)
    TipoVenta = Column(String(50))

    def read():
        with session_scope() as session:
            result = session.query(SalesTypes).all()
            sales_types_list = [
                {
                    "id": sales_type.Id,
                    "sales_types": sales_type.TipoVenta,
                }
                for sales_type in result
            ]
            return sales_types_list

    def find_sale_type(id_sale_type):

        with session_scope() as session:
            sale_type = session.query(SalesTypes).filter_by(Id=id_sale_type).first()
            if sale_type:
                return sale_type.TipoVenta
            else:
                return "Articulo no encontrada"
