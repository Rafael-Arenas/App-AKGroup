from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class RutCompany(Base):
    __tablename__ = 'rutempresas'
    Id = Column(Integer, primary_key=True)
    Rut = Column(String(20))
    Empresas_Id = Column(Integer, ForeignKey('empresas.Id'))

    def create(new_rut, id_company):
        with session_scope() as session:
            new_rut_company = RutCompany(Rut=new_rut, Empresas_Id=id_company)
            session.add(new_rut_company)
            return True

    def edit(new_rut, id_rut):
        with session_scope() as session:
            rut_company = session.query(RutCompany).get(id_rut)
            if rut_company:
                rut_company.Rut = new_rut
                return True

    def delete(id_rut):
        with session_scope() as session:
            rut = session.query(RutCompany).get(id_rut)
            if rut:
                session.delete(rut)
                return True

    def find_ruts(id_company):
        with session_scope() as session:
            ruts = session.query(RutCompany).filter(RutCompany.Empresas_Id == id_company).all()
            ruts_list = [
                {
                    "id": rut.Id,
                    "rut": rut.Rut,

                }
                for rut in ruts
            ]
            return ruts_list

    def find_rut(id_rut):
        with session_scope() as session:
            rut = session.query(RutCompany).filter(RutCompany.Id == id_rut).first()
            if rut:
                return {
                    "id": rut.Id,
                    "rut": rut.Rut,
                    "id_company": rut.Empresas_Id,
                }
            else:
                return "Contacto no encontrada"

    def get_rut(id_rut):
        with session_scope() as session:
            rut = session.query(RutCompany).filter(RutCompany.Id == id_rut).first()
            if rut:
                return {
                    "rut": rut.Rut,
                }
            else:
                return "Contacto no encontrada"

    def find_id(number_rut):
        with session_scope() as session:
            contact = session.query(RutCompany).filter(RutCompany.Rut == number_rut).first()
            if contact:
                return {
                    "id": contact.Id,
                    "id_company": contact.Empresas_Id,
                }
            else:
                return "Contacto no encontrada"
            
    def find_all():
        with session_scope() as session:
            ruts = session.query(RutCompany).all()
            ruts_list = [
                {
                    "id": rut.Id,
                    "rut": rut.Rut,

                }
                for rut in ruts
            ]
            return ruts_list