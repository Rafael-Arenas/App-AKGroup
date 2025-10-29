from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata


Base = declarative_base(metadata=metadata)

class Branch(Base):
    __tablename__ = 'sucursales'
    Id = Column(Integer, primary_key=True)
    Nombre = Column(String(100))
    Direccion = Column(String(100))
    Telefono = Column(String(20))
    Ciudades_Id = Column(Integer, ForeignKey('ciudades.Id'))
    Empresas_Id = Column(Integer, ForeignKey('empresas.Id'))
    
    
    def add(new_branch_data):
        with session_scope() as session:
            new_branch = Branch(
                Nombre=new_branch_data["name"],
                Direccion=new_branch_data["address"], 
                Telefono=new_branch_data["phone"],
                Ciudades_Id= new_branch_data["id_city"],
                Empresas_Id=new_branch_data["id_company"])
            session.add(new_branch)
            return True

    def edit(edit_branch_data):
        with session_scope() as session:
            branch = session.query(Branch).filter_by(Id=edit_branch_data["id_branch"]).first()
            if branch:
                branch_attrs = {
                    'Nombre': edit_branch_data["name"],
                    'Direccion': edit_branch_data["address"],
                    'Telefono': edit_branch_data["phone"],
                    'Ciudades_Id': edit_branch_data["id_city"],
                    'Empresas_Id': edit_branch_data["id_company"],
                }
                for attr, value in branch_attrs.items():
                    if value and getattr(branch, attr) != value:
                        setattr(branch, attr, value)
                return True
            else:
                return False

    def delete(id_branch):
        with session_scope() as session:
            branch = session.get(Branch, id_branch)
            if not branch:
                return False
            session.delete(branch)
            return True

    def find_branch_offices(id_company):
        with session_scope() as session:
            branchs = session.query(Branch).filter(Branch.Empresas_Id == id_company).all()
            branchs_list = [
                {
                    "id": branch.Id,
                    "name": branch.Nombre,
                    "address": branch.Direccion,
                    "phone": branch.Telefono,
                    "id_city": branch.Ciudades_Id,
                }
                for branch in branchs
            ]
            return branchs_list

    def find_id(name):
        with session_scope() as session:
            branch = session.query(Branch).filter(Branch.Nombre == name).first()
            if branch:
                return {

                    "id": branch.Id,
                }
            else:
                return "Articulo no encontrada"

    def find_branch_id(id_branch):
        with session_scope() as session:
            branch = session.query(Branch).filter(Branch.Id == id_branch).first()
            if branch:
                return {
                    "name": branch.Nombre,
                    "address": branch.Direccion,
                    "phone": branch.Telefono,
                    "id_company": branch.Empresas_Id,
                    "id_city": branch.Ciudades_Id,
                }
            else:
                return "Articulo no encontrada"

    def get_name(id_branch):
        with session_scope() as session:
            branch = session.query(Branch).filter(Branch.Id == id_branch).first()
            if branch:
                return {
                    "name": branch.Nombre,
                }
            else:
                return "Articulo no encontrada"

    def find_all():
        with session_scope() as session:
            branchs = session.query(Branch).all()
            branchs_list = [
                {
                    "id": branch.Id,
                    "name": branch.Nombre,
                    "address": branch.Direccion,
                    "phone": branch.Telefono,
                    "id_company": branch.Empresas_Id,
                    "id_city": branch.Ciudades_Id,
                }
                for branch in branchs
            ]
            return branchs_list