from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class Transports(Base):
    __tablename__ = 'transportes'
    Id = Column(Integer, primary_key=True)
    NumeroEntrega = Column(String(50))
    Estado = Column(String(50))
    Empresas_Id = Column(Integer, ForeignKey('empresas.Id'))
    Ordenes_Id = Column(Integer, ForeignKey('ordenes.Id'))

    # @classmethod
    def add(new_transport_data):
        with session_scope() as session:
            new_transport = Transports(
                NumeroEntrega=new_transport_data["delivery_number"], 
                Estado=new_transport_data["statu"],
                Empresas_Id=new_transport_data["id_company"],
                Ordenes_Id=new_transport_data["id_order"],
            )
            session.add(new_transport)
            session.flush()  # Hacer flush para asegurar que se asignen los valores auto-generados, como el ID
            return True
            # return new_transport.Id
        
    def edit(transport_data):
        with session_scope() as session:
            transport = session.query(Transports).filter_by(Id=transport_data["id_transport"]).first()
            if transport:
                transport_attrs = {
                    'NumeroEntrega': transport_data["delivery_number"],
                    'Estado': transport_data["statu"],
                }
                for attr, value in transport_attrs.items():
                    if value and getattr(transport, attr) != value:
                        setattr(transport, attr, value)
                return True
            else:
                return False
    
    def delete(id_transport):
        with session_scope() as session:
            transport = session.get(Transports, id_transport)
            if transport:
                session.delete(transport)
                return True

    def read(id_transport):
        with session_scope() as session:
            transport = session.query(Transports).filter(Transports.Id == id_transport).first()
            if transport:
                return {
                    "delivery_number": transport.NumeroEntrega,
                    "status": transport.Estado,
                }
            else:
                return "transporte no encontrada"

    # def get_transport(id_company):
    #     with session_scope() as session:
    #         transport = session.query(Transports).filter(Transports.Empresas_Id == id_company).first()
    #         if transport:
    #             return {
    #                 "id": transport.Id,
    #                 "delivery_number": transport.NumeroEntrega,
    #                 "status": transport.Estado,
    #             }
    #         else:
    #             return False
    def get_transport(id_order):
        with session_scope() as session:
            transports = session.query(Transports).filter(Transports.Ordenes_Id == id_order).all()
            transports_list = [
                {
                    "id": transport.Id,
                    "delivery_number": transport.NumeroEntrega,
                    "status": transport.Estado,
                }
                for transport in transports
            ]
            return transports_list
            
    # def save(note, id_note):
    #     with session_scope() as session:
    #         save_note = session.query(Transport).get(id_note)
    #         if save_note:
    #             save_note.Nota = note
    #             return True

    def find_notes(id_quote):
        with session_scope() as session:
            notes = session.query(Transports).filter(Transports.Cotizaciones_Id == id_quote).all()
            notes_list = [
                {
                    "id": note.Id,
                    "name": note.Nombre,
                    "note": note.Nota,
                }
                for note in notes
            ]
            return notes_list


