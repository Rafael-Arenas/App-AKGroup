from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class NomenNomen(Base):
    __tablename__ = 'nomennomen'
    Id = Column(Integer, primary_key=True)
    Cantidad = Column(Integer)
    Nomenclaturas_Id = Column(Integer, ForeignKey('nomenclaturas.Id'))
    Nomen_Id = Column(Integer, ForeignKey('nomenclaturas.Id'))

    def add(quantity, id_nomenclature, id_nomen):
        with session_scope() as session:
            new_nomen_nomen = NomenNomen(Cantidad=quantity, Nomenclaturas_Id=id_nomenclature, Nomen_Id=id_nomen)
            session.add(new_nomen_nomen)
            session.flush()
            return new_nomen_nomen.Id

    def edit(id_nomen_nomen, quantity):
        with session_scope() as session:
            edit_nomen_nomen = session.query(NomenNomen).get(id_nomen_nomen)
            if edit_nomen_nomen:
                edit_nomen_nomen.Cantidad = quantity
                return True
    
    def delete(id_nomen_nomen):
        with session_scope() as session:
            nomen_nomen = session.query(NomenNomen).get(id_nomen_nomen)
            if nomen_nomen:
                session.delete(nomen_nomen)
                return True
            
    def find_nomen_nomen(id_nomenclature):
        with session_scope() as session:
            nomen_nomens_objets = session.query(NomenNomen).filter(NomenNomen.Nomenclaturas_Id == id_nomenclature).all()
            nomen_nomens_list = [
                {
                    "id": nomen_nomen.Id,
                    "quantity": nomen_nomen.Cantidad,
                    "id_nomen": nomen_nomen.Nomen_Id,
                }
                for nomen_nomen in nomen_nomens_objets
            ]
            return nomen_nomens_list

    def get_quantity(id_nomen_nomen):
        with session_scope() as session:
            nomen_nomen = session.query(NomenNomen).filter(NomenNomen.Id == id_nomen_nomen).first()
            if nomen_nomen:
                return nomen_nomen.Cantidad
            else:
                return "Artinomen no encontrada"



    def get_nomen_nomen(id_nomen_nomen):
        with session_scope() as session:
            nomen_nomen = session.query(NomenNomen).filter(NomenNomen.Id == id_nomen_nomen).first()
            if nomen_nomen:
                return {
                    "quantity": nomen_nomen.Cantidad,
                    "id_nomenclature": nomen_nomen.Nomenclaturas_Id,
                    "id_nomen": nomen_nomen.Nomen_Id,
                }
            else:
                return "Artinomen no encontrada"

    def find_id(id_nomen, id_nomenclature):
        with session_scope() as session:
            nomen_nomen = session.query(NomenNomen.Id).filter(NomenNomen.Nomen_Id == id_nomen, NomenNomen.Nomenclaturas_Id == id_nomenclature).first()
            if nomen_nomen:
                return {
                    "id": nomen_nomen.Id,
                }
            else:
                return "Artinomen no encontrada"
