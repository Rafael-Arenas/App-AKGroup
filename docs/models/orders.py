from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class Order(Base):
    __tablename__ = 'ordenes'
    Id = Column(Integer, primary_key=True)
    Revision = Column(String(2))
    NumeroOrden = Column(String(50))
    NumeroCotizacionCliente = Column(String(50))
    NumeroProyecto = Column(String(50))
    FechaCreacion = Column(String(50))
    UltimaModificacion = Column(String(50))
    Cotizaciones_Id = Column(Integer, ForeignKey('cotizaciones.Id'))
    Direcciones_Id = Column(Integer, ForeignKey('direcciones.Id'))
    Empresas_Id = Column(Integer, ForeignKey('empresas.Id'))

    def add(new_order_data):
        with session_scope() as session:
            new_order = Order(
                Revision=new_order_data["revision"], 
                NumeroOrden=new_order_data["number_order"], 
                NumeroCotizacionCliente=new_order_data["customer_purchase_order_number"],
                NumeroProyecto=new_order_data["proyect_number"], 
                FechaCreacion=new_order_data["creation_date"], 
                UltimaModificacion=new_order_data["creation_date"], 
                Cotizaciones_Id=new_order_data["id_quote"],
                Direcciones_Id=new_order_data["id_address"], 
                Empresas_Id=new_order_data["id_company"])
            session.add(new_order)
            session.flush()
            return new_order.Id
    def edit(edit_order_data):
        with session_scope() as session:
            order = session.query(Order).filter_by(Id=edit_order_data["id_order"]).first()
            if order:
                order_attrs = {
                    'Revision': edit_order_data["revision"],
                    'NumeroOrden': edit_order_data["number_order"],
                    'NumeroCotizacionCliente': edit_order_data["customer_purchase_order_number"],
                    'NumeroProyecto': edit_order_data["proyect_number"],
                    'UltimaModificacion': edit_order_data["last_modification"],
                    'Direcciones_Id': edit_order_data["id_address"],
                }
                for attr, value in order_attrs.items():
                    if value and getattr(order, attr) != value:
                        setattr(order, attr, value)
                return True
            else:
                return False
            
    def edit_date(id_order, date_last_modification):
        with session_scope() as session:
            order = session.query(Order).filter_by(Id=id_order).first()
            if order:
                order_attrs = {
                    'UltimaModificacion': date_last_modification,
                }
                for attr, value in order_attrs.items():
                    if value and getattr(order, attr) != value:
                        setattr(order, attr, value)
                return True
            else:
                return False

    def delete(id_order):
        with session_scope() as session:
            order = session.query(Order).filter(Order.Id == id_order).first()
            session.delete(order)
            return True

    def read(id_order):
        with session_scope() as session:
            order = session.query(Order).filter_by(Id=id_order).first()
            if order:
                return {
                    "id": order.Id,
                    "revision": order.Revision,
                    "number_order": order.NumeroOrden,
                    "customer_purchase_order_number": order.NumeroCotizacionCliente,
                    "proyect_number": order.NumeroProyecto,
                    "creation_date": order.FechaCreacion,
                    "last_modification": order.UltimaModificacion,
                    "id_quote": order.Cotizaciones_Id,
                    "id_address": order.Direcciones_Id,
                    "id_company": order.Empresas_Id,
                }
            else:
                return "Contacto no encontrada"
    
    def find_order_some(id_quote):
        with session_scope() as session:
            orders = session.query(Order).filter(Order.Cotizaciones_Id == id_quote).all()
            orders_list = [
                {
                    "id": order.Id,
                    "revision": order.Revision,
                    "number_order": order.NumeroOrden,
                    "customer_purchase_order_number": order.NumeroCotizacionCliente,
                    "proyect_number": order.NumeroProyecto,
                    "creation_date": order.FechaCreacion,
                    "last_modification": order.UltimaModificacion,
                    "id_quote": order.Cotizaciones_Id,
                    "id_address": order.Direcciones_Id,
                    "id_company": order.Empresas_Id,
                }
                for order in orders
            ]
            return orders_list

    def all_order(id_company):
        with session_scope() as session:
            orders = session.query(Order).filter(Order.Empresas_Id == id_company).all()
            orders_list = [
                {
                    "id": order.Id,
                    "revision": order.Revision,
                    "number_order": order.NumeroOrden,
                    "customer_purchase_order_number": order.NumeroCotizacionCliente,
                    "proyect_number": order.NumeroProyecto,
                    "creation_date": order.FechaCreacion,
                    "last_modification": order.UltimaModificacion,
                    "id_quote": order.Cotizaciones_Id,
                    "id_address": order.Direcciones_Id,
                    "id_company": order.Empresas_Id,
                }
                for order in orders
            ]
            return orders_list

    def one_order(id_order):
        with session_scope() as session:
            order = session.query(Order).filter_by(Id=id_order).first()
            if order:
                return {
                    "id": order.Id,
                    "revision": order.Revision,
                    "number_order": order.NumeroOrden,
                    "customer_purchase_order_number": order.NumeroCotizacionCliente,
                    "proyect_number": order.NumeroProyecto,
                    "creation_date": order.FechaCreacion,
                    "last_modification": order.UltimaModificacion,
                    "id_quote": order.Cotizaciones_Id,
                    "id_address": order.Direcciones_Id,
                    "id_company": order.Empresas_Id,
                }
            else:
                return "Contacto no encontrada"

    def last_number_order(id_company):
        with session_scope() as session:
            order = session.query(Order).filter_by(Empresas_Id=id_company).order_by(Order.Id.desc()).first()
            if order:
                return order.NumeroOrden
            else:
                return False

