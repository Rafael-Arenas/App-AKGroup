from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class DeliveryDates(Base):
    __tablename__ = 'fechasentregas'
    Id = Column(Integer, primary_key=True)
    FechaEntrega = Column(String(150))
    Ordenes_Id = Column(Integer, ForeignKey('ordenes.Id'))
    Empresas_Id = Column(Integer, ForeignKey('empresas.Id'))

    def add(new_date_delivery_data):
        with session_scope() as session:
            new_delivery_date = DeliveryDates(
                FechaEntrega=new_date_delivery_data["number_delivery_date"], 
                Ordenes_Id=new_date_delivery_data["id_order"],
                Empresas_Id=new_date_delivery_data["id_company"]
            )
            session.add(new_delivery_date)
            return True
        
    def edit(date_delivery_data):
        with session_scope() as session:
            date_delivery = session.query(DeliveryDates).filter_by(Id=date_delivery_data["id_date_delivery"]).first()
            if date_delivery:
                date_delivery_attrs = {
                    'FechaEntrega': date_delivery_data["number_delivery_date"],
                }
                for attr, value in date_delivery_attrs.items():
                    if value and getattr(date_delivery, attr) != value:
                        setattr(date_delivery, attr, value)
                return True
            else:
                return False

    
    def delete(id_date_delivery):
        with session_scope() as session:
            date_delivery = session.get(DeliveryDates, id_date_delivery)
            if date_delivery:
                session.delete(date_delivery)
                return True

    # def get(id_order):
    #     with session_scope() as session:
    #         delivery_date = session.query(DeliveryDates).filter(DeliveryDates.Ordenes_Id == id_order).first()
    #         if delivery_date:
    #             return {
    #                 "id": delivery_date.Id,
    #                 "number_delivery_date": delivery_date.FechaEntrega,
    #             }
    #         else:
    #             return False
    def get(id_order):
        with session_scope() as session:
            deliverys_dates = session.query(DeliveryDates).filter(DeliveryDates.Ordenes_Id == id_order).all()
            deliverys_dates_list = [
                {
                    "id": date_delivery.Id,
                    "number_delivery_date": date_delivery.FechaEntrega,
                }
                for date_delivery in deliverys_dates
            ]
            return deliverys_dates_list