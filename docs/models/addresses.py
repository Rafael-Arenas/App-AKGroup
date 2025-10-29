from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata
Base = declarative_base(metadata=metadata)

class Addresses(Base):
    __tablename__ = 'direcciones'
    Id = Column(Integer, primary_key=True)
    Direccion = Column(String(200))
    Empresas_Id = Column(Integer, ForeignKey('empresas.Id'))

    def create(new_address, id_company):
        with session_scope() as session:
            new_address_company = Addresses(Direccion=new_address, Empresas_Id=id_company)
            session.add(new_address_company)
            return True
        
    def edit(new_address, id_address):
        with session_scope() as session:
            delivery_address = session.query(Addresses).get(id_address)
            if delivery_address:
                delivery_address.Direccion = new_address
                return True

    def delete(id_address):

        with session_scope() as session:
            address = session.get(Addresses, id_address)
            if address:
                session.delete(address)
                return True
            
    def read(id_address):
        with session_scope() as session:
            address = session.query(Addresses).filter_by(Id=id_address).first()
            if address:
                return {
                    "address": address.Direccion,
                }
            else:
                return "Articulo no encontrada"

    def find_address(id_company):
        with session_scope() as session:
            addresses = session.query(Addresses).filter(Addresses.Empresas_Id == id_company).all()
            addresses_list = [
                {
                    "id": address.Id,
                    "address": address.Direccion,
                }
                for address in addresses
            ]
            return addresses_list