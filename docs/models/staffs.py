from sqlalchemy import Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.exc import IntegrityError
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class Staff(Base):
    __tablename__ = 'personal'
    Id = Column(Integer, primary_key=True)
    Nombre = Column(String(150))
    Cargo = Column(String(50))
    Telefono = Column(String(20))
    Email = Column(String(100))
    Trigrama = Column(String(6))

    def add(name, position, phone, email, trigram):
        with session_scope() as session:
            staff = Staff(Nombre=name, Cargo=position, Telefono=phone, Email=email ,Trigrama=trigram)
            session.add(staff)
            return True

    def edit(id_staff, name=None, position=None, phone=None, email=None, trigram=None):
        with session_scope() as session:
            staff = session.query(Staff).filter_by(Id=id_staff).first()
            if staff:
                if name and name != staff.Nombre:
                    staff.Nombre = name
                if position and position != staff.Cargo:
                    staff.Cargo = position
                if phone and phone != staff.Telefono:
                    staff.Telefono = phone
                if email and email != staff.Email:
                    staff.Email = email
                if trigram and trigram != staff.Trigrama:
                    staff.Trigrama = trigram
                return True
            else:
                return False

    def delete(id_staff):
        with session_scope() as session:
            staff = session.query(Staff).get(id_staff)
            if staff:
                session.delete(staff)
                return True
            
    def read(id_staff):
        with session_scope() as session:
            staff = session.query(Staff).filter_by(Id=id_staff).first()
            if staff:
                return {
                    "name": staff.Nombre,
                    "position": staff.Cargo,
                    "phone": staff.Telefono,
                    "email": staff.Email,
                    "trigram": staff.Trigrama,
                }
            else:
                return "Personal no encontrada"

    def find_staff():
        with session_scope() as session:
            staffs = session.query(Staff).order_by(Staff.Id.desc()).all()
            staffs_list = [
                {
                    "id": staff.Id,
                    "name": staff.Nombre,
                    "position": staff.Cargo,
                    "phone": staff.Telefono,
                    "email": staff.Email,
                    "trigram": staff.Trigrama,
                }
                for staff in staffs
            ]
            return staffs_list
        
    def find_staff_accor(trigram):
        with session_scope() as session:
            staff = session.query(Staff).filter_by(Trigrama=trigram).first()
            if staff:
                return {
                    "id": staff.Id,
                    "name": staff.Nombre,
                    "position": staff.Cargo,
                    "phone": staff.Telefono,
                    "email": staff.Email,
                    "trigram": staff.Trigrama,
                }
            else:
                return "Personal no encontrada"

    def find_staff_written(searching):
        with session_scope() as session:
            staffs = session.query(Staff).filter(Staff.Nombre.like(f'%{searching}%')).all()
            staffs_list = [
                {
                    "id": staff.Id,
                    "name": staff.Nombre,
                    "position": staff.Cargo,
                    "phone": staff.Telefono,
                    "email": staff.Email,
                    "trigram": staff.Trigrama,
                }
                for staff in staffs
            ]
            return staffs_list

    def find_id(name):
        with session_scope() as session:
            staff = session.query(Staff).filter(Staff.Nombre == name).first()
            if staff:
                return {
                    "id": staff.Id,
                }
            else:
                return "Personal no encontrada"

    def get_name(id_staff):
        with session_scope() as session:
            staff = session.query(Staff).filter_by(Id=id_staff).first()
            if staff:
                return {
                    "name": staff.Nombre,
                }
            else:
                return "Personal no encontrada"