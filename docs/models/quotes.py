from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class Quote(Base):
    __tablename__ = 'cotizaciones'
    Id = Column(Integer, primary_key=True)
    Asunto = Column(String(150))
    Revision = Column(String(2))
    NumeroCotizacion = Column(String(50))
    FechaEnvio = Column(String(150))
    Estado = Column(String(50))
    Incoterm = Column(String(50))
    Unidad = Column(String(4))
    FechaCreacion = Column(String(50))
    UltimaModificacion = Column(String(50))
    Empresas_Id = Column(Integer, ForeignKey('empresas.Id'))
    Contactos_Id = Column(Integer, ForeignKey('contactos.Id'))
    RutEmpresas_Id = Column(Integer, ForeignKey('rutempresas.Id'))
    Sucursales_Id = Column(Integer, ForeignKey('sucursales.Id'))
    Personal_Id = Column(Integer, ForeignKey('personal.Id'))
    
    def add(new_quote_data):
        with session_scope() as session:
            new_quote = Quote(
                Asunto=new_quote_data["subject"], 
                Revision=new_quote_data["revision"], 
                NumeroCotizacion=new_quote_data["quote_number"], 
                FechaEnvio=new_quote_data["shipping_date"],
                Estado=new_quote_data["status"], 
                Incoterm=new_quote_data["incoterm"], 
                Unidad=new_quote_data["unit"], 
                FechaCreacion=new_quote_data["date_creation"],
                UltimaModificacion=new_quote_data["date_creation"], 
                Empresas_Id=new_quote_data["id_company"], 
                Contactos_Id=new_quote_data["id_contact"],
                RutEmpresas_Id=new_quote_data["id_rut"], 
                Sucursales_Id=new_quote_data["id_branch"],
                Personal_Id=new_quote_data["id_staff"])
            session.add(new_quote)
            return True

    def edit(edit_quote_data):
        with session_scope() as session:
            quote = session.query(Quote).filter_by(Id=edit_quote_data["id_quote"]).first()
            if quote:
                quote_attrs = {
                    'Asunto': edit_quote_data["subject"],
                    'Revision': edit_quote_data["revision"],
                    'NumeroCotizacion': edit_quote_data["quote_number"],
                    'FechaEnvio': edit_quote_data["shipping_date"],
                    'Estado': edit_quote_data["status"],
                    'Incoterm': edit_quote_data["incoterm"],
                    'Unidad': edit_quote_data["unit"],
                    'UltimaModificacion': edit_quote_data["date_creation"],
                    'Empresas_Id': edit_quote_data["id_company"],
                    'Contactos_Id': edit_quote_data["id_contact"],
                    'RutEmpresas_Id': edit_quote_data["id_rut"],
                    'Sucursales_Id': edit_quote_data["id_branch"],
                    'Personal_Id': edit_quote_data["id_staff"],
                }
                for attr, value in quote_attrs.items():
                    if value and getattr(quote, attr) != value:
                        setattr(quote, attr, value)
                return True
            else:
                return False

    def edit_date(id_quote, date_last_modification):
        with session_scope() as session:
            quote = session.query(Quote).filter_by(Id=id_quote).first()
            if quote:
                quote_attrs = {
                    'UltimaModificacion': date_last_modification,
                }
                for attr, value in quote_attrs.items():
                    if value and getattr(quote, attr) != value:
                        setattr(quote, attr, value)
                return True
            else:
                return False


    def delete(id_quote):
        with session_scope() as session:
            quote = session.get(Quote, id_quote)
            session.delete(quote)
            return True

    def read(id_quote):
        with session_scope() as session:
            quote = session.query(Quote).filter_by(Id=id_quote).first()
            if quote:
                return {
                    "subject": quote.Asunto,
                    "revision": quote.Revision,
                    "quote_number": quote.NumeroCotizacion,
                    "shipping_date": quote.FechaEnvio,
                    "statu": quote.Estado,
                    "incoterm": quote.Incoterm,
                    "unit": quote.Unidad,
                    "date_creation": quote.FechaCreacion,
                    "last_modification": quote.UltimaModificacion,
                    "id_company": quote.Empresas_Id,
                    "id_contact": quote.Contactos_Id,
                    "id_rut": quote.RutEmpresas_Id,
                    "id_branch": quote.Sucursales_Id,
                    "id_staff": quote.Personal_Id,
                }
            else:
                return "Contacto no encontrada"

    def get_quote(id_company):
        with session_scope() as session:
            quotes = session.query(Quote).filter(Quote.Empresas_Id == id_company).all()
            quotes_list = [
                {
                    "id": quote.Id,
                    "subject": quote.Asunto,
                    "revision": quote.Revision,
                    "quote_number": quote.NumeroCotizacion,
                    "shipping_date": quote.FechaEnvio,
                    "statu": quote.Estado,
                    "incoterm": quote.Incoterm,
                    "unit": quote.Unidad,
                    "id_contact": quote.Contactos_Id,
                    "id_rut": quote.RutEmpresas_Id,
                    "id_branch": quote.Sucursales_Id,
                    "id_staff": quote.Personal_Id,
                    "date_creation": quote.FechaCreacion,
                    "last_modification": quote.UltimaModificacion,
                }
                for quote in quotes
            ]
            return quotes_list

    def get_quote_all():
        with session_scope() as session:
            quotes = session.query(Quote).all()
            quotes_list = [
                {
                    "id": quote.Id,
                    "subject": quote.Asunto,
                    "revision": quote.Revision,
                    "quote_number": quote.NumeroCotizacion,
                    "shipping_date": quote.FechaEnvio,
                    "statu": quote.Estado,
                    "incoterm": quote.Incoterm,
                    "unit": quote.Unidad,
                    "id_company": quote.Empresas_Id,
                    "id_contact": quote.Contactos_Id,
                    "id_rut": quote.RutEmpresas_Id,
                    "id_branch": quote.Sucursales_Id,
                    "id_staff": quote.Personal_Id,
                    "date_creation": quote.FechaCreacion,
                    "last_modification": quote.UltimaModificacion,
                }
                for quote in quotes
            ]
            return quotes_list
        
    def find_id(id_company):
        with session_scope() as session:
            quotes = session.query(Quote).filter(Quote.Empresas_Id == id_company).all()
            ids_list = [quote.Id for quote in quotes]
            return ids_list


    def find_quote_written(searching, id_company):
        with session_scope() as session:
            quotes = session.query(Quote).filter(Quote.Asunto.like(f'%{searching}%'), Quote.Empresas_Id == id_company).all()
            quotes_list = [
                {
                    "id": quote.Id,
                    "subject": quote.Asunto,
                    "revision": quote.Revision,
                    "quote_number": quote.NumeroCotizacion,
                    "shipping_date": quote.FechaEnvio,
                    "statu": quote.Estado,
                    "incoterm": quote.Incoterm,
                    "unit": quote.Unidad,
                    "id_contact": quote.Contactos_Id,
                    "id_rut": quote.RutEmpresas_Id,
                    "id_branch": quote.Sucursales_Id,
                    "id_staff": quote.Personal_Id,
                    "date_creation": quote.FechaCreacion,
                    "last_modification": quote.UltimaModificacion,
                }
                for quote in quotes
            ]
            return quotes_list

    def quote_number(id_company):
        with session_scope() as session:
            quote = session.query(Quote).filter_by(Empresas_Id=id_company).order_by(Quote.Id.desc()).first()
            if quote:
                return quote.NumeroCotizacion
            else:
                return False
