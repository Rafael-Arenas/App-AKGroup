from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class OrderDelivery(Base):
    __tablename__ = 'ordenesentrega'
    Id = Column(Integer, primary_key=True)
    Revision = Column(String(2))
    NumeroOrdenEntrega = Column(String(50))
    UltimaModificacion = Column(String(50))
    Ordenes_Id = Column(Integer, ForeignKey('ordenes.Id'))
    Empresas_Id = Column(Integer, ForeignKey('empresas.Id'))
    
    def add(new_order_delivery_data):
        with session_scope() as session:
            new_number_delivery_order = OrderDelivery(
                Revision=new_order_delivery_data["revision"],
                NumeroOrdenEntrega=new_order_delivery_data["number_delivery_order"], 
                UltimaModificacion=new_order_delivery_data["creation_date"],
                Ordenes_Id=new_order_delivery_data["id_order"],
                Empresas_Id=new_order_delivery_data["id_company"],
            )
            session.add(new_number_delivery_order)
            # session.flush()
            return True

    def edit(id_order_delivery, number_delivery_order, last_modification):
        with session_scope() as session:
            order_delivery = session.get(OrderDelivery, id_order_delivery)
            if order_delivery:
                order_delivery.NumeroOrdenEntrega = number_delivery_order
                order_delivery.UltimaModificacion = last_modification
                return True

    def edit_last_modification(id_order_delivery, date_last_modification):
        with session_scope() as session:
            order_delivery = session.get(OrderDelivery, id_order_delivery)
            if order_delivery:
                order_delivery.UltimaModificacion = date_last_modification
                return True

    def delete(id_rut):
        with session_scope() as session:
            rut = session.query(OrderDelivery).get(id_rut)
            if rut:
                session.delete(rut)
                return True


    def read(id_order_delivery):
        with session_scope() as session:
            order_deliverys = session.query(OrderDelivery).filter(OrderDelivery.Id == id_order_delivery).first()
            if order_deliverys:
                return {
                    "revision": order_deliverys.Revision,
                    "delivery_order_number": order_deliverys.NumeroOrdenEntrega,
                    "last_modification": order_deliverys.UltimaModificacion,
                    "id_order": order_deliverys.Ordenes_Id,
                    "id_company": order_deliverys.Empresas_Id,
                }
            else:
                return "Detalle orden no encontrada"
            
    def get_order_delivery_(id_order):
        with session_scope() as session:
            order = session.query(OrderDelivery).filter(OrderDelivery.Ordenes_Id == id_order).first()
            if order:
                return {
                    "id": order.Id,
                    "revision": order.Revision,
                    "delivery_order_number": order.NumeroOrdenEntrega,
                    "last_modification": order.UltimaModificacion,
                    "id_order": order.Ordenes_Id,
                    "id_company": order.Empresas_Id,
                }
            else:
                return False
        
    def get_all_order_delivery(id_order):
        with session_scope() as session:
            orders_delivery = session.query(OrderDelivery).filter(OrderDelivery.Ordenes_Id == id_order).all()
            orders_delivery_list = [
                {
                    "id": order_delivery.Id,
                    "revision": order_delivery.Revision,
                    "delivery_order_number": order_delivery.NumeroOrdenEntrega,
                    "last_modification": order_delivery.UltimaModificacion,
                    "id_order": order_delivery.Ordenes_Id,
                    "id_company": order_delivery.Empresas_Id,
                }
                for order_delivery in orders_delivery
            ]
            return orders_delivery_list
            
    def number_delivery_order(id_company):
        with session_scope() as session:
            number_delivery = session.query(OrderDelivery).filter_by(Empresas_Id=id_company).order_by(OrderDelivery.Id.desc()).first()
            if number_delivery:
                    return number_delivery.NumeroOrdenEntrega
            else:
                return False