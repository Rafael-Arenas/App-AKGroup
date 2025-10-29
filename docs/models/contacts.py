from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class Contact(Base):
    __tablename__ = 'contactos'
    Id = Column(Integer, primary_key=True)
    Nombre = Column(String(100))
    Email = Column(String(100))
    Telefono = Column(String(20))
    Empresas_Id = Column(Integer, ForeignKey('empresas.Id'))
    Servicios_Id = Column(Integer, ForeignKey('servicios.Id'))
    
    def create(new_contact_data):
        with session_scope() as session:
            new_contact = Contact(
                Nombre=new_contact_data["name"],
                Email=new_contact_data["email"],
                Telefono=new_contact_data["phone"],
                Empresas_Id=new_contact_data["id_company"],
                Servicios_Id=new_contact_data["id_service"])
            session.add(new_contact)
            return True

    def edit(edit_contact_data):
            with session_scope() as session:
                contact = session.query(Contact).filter(Contact.Id == edit_contact_data["id_contact"]).first()
                if contact:
                    contact_attrs = {
                        'Nombre': edit_contact_data["name"],
                        'Email': edit_contact_data["email"],
                        'Telefono': edit_contact_data["phone"],
                        'Empresas_Id': edit_contact_data["id_company"],
                        'Servicios_Id': edit_contact_data["id_service"],
                    }
                    for attr, value in contact_attrs.items():
                        if value and getattr(contact, attr) != value:
                            setattr(contact, attr, value)
                    return True
                else:
                    return False

    def delete(id_contact):
        with session_scope() as session:
            contact = session.get(Contact, id_contact)
            session.delete(contact)
            return True

    def find_contacts(id_company):
        with session_scope() as session:
            contacts = session.query(Contact).filter(Contact.Empresas_Id == id_company).all()
            contacts_list = [
                {
                    "id": contact.Id,
                    "name": contact.Nombre,
                    "email": contact.Email,
                    "phone": contact.Telefono,
                    "id_service": contact.Servicios_Id,
                }
                for contact in contacts
            ]
            return contacts_list

    def find_all():
        with session_scope() as session:
            contacts = session.query(Contact).all()
            contacts_list = [
                {
                    "id": contact.Id,
                    "name": contact.Nombre,
                    "email": contact.Email,
                    "phone": contact.Telefono,
                    "id_company": contact.Empresas_Id,
                    "id_service": contact.Servicios_Id,
                }
                for contact in contacts
            ]
            return contacts_list

    def find_contact_id(id_contact):
        with session_scope() as session:
            contact = session.query(Contact).filter(Contact.Id == id_contact).first()
            if contact:
                return {
                    "name": contact.Nombre,
                    "email": contact.Email,
                    "phone": contact.Telefono,
                    "id_company": contact.Empresas_Id,
                    "id_service": contact.Servicios_Id,
                }
            else:
                return "Contacto no encontrada"

    def get_name(id_contact):
        with session_scope() as session:
            contact = session.query(Contact).filter(Contact.Id == id_contact).first()
            if contact:
                return {
                    "name": contact.Nombre
                }

            else:
                return "Contacto no encontrada"

class Service(Base):
    __tablename__ = 'servicios'
    Id = Column(Integer, primary_key=True)
    Servicio = Column(String(50))

    def read():
        with session_scope() as session:
            contacts = session.query(Service).all()
            contacts_list = [
                {
                    "id": contact.Id,
                    "service": contact.Servicio,
                }
                for contact in contacts
            ]
            return contacts_list

    def find_name(id_service):
        with session_scope() as session:
            service = session.query(Service).filter(Service.Id == id_service).first()
            if service:
                return service.Servicio
                
            else:
                return "servicio no encontrada"
