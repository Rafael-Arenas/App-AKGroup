from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class PaymentCondition(Base):
    __tablename__ = 'condicionpagos'
    Id = Column(Integer, primary_key=True)
    Revision = Column(String(2))
    NumeroCondicionPago = Column(String(50))
    TiposPagos_Id = Column(Integer, ForeignKey('tipospagos.Id'))
    Ordenes_Id = Column(Integer, ForeignKey('ordenes.Id'))
    Empresas_Id = Column(Integer, ForeignKey('empresas.Id'))

    def add(new_payment_condition_data):
        with session_scope() as session:
            new_paid_statement = PaymentCondition(
                Revision=new_payment_condition_data["revision"], 
                NumeroCondicionPago=new_payment_condition_data["payment_condition_number"],
                TiposPagos_Id=new_payment_condition_data["id_type_payment"],
                Ordenes_Id=new_payment_condition_data["id_order"],
                Empresas_Id=new_payment_condition_data["id_company"],
            )
            session.add(new_paid_statement)
            session.flush()
            # return new_paid_statement.Id
            return True

    def edit(payment_condition_data):
        with session_scope() as session:
            payment_condition = session.query(PaymentCondition).filter_by(Id=payment_condition_data["id_payment_condition"]).first()
            if payment_condition:
                payment_condition_attrs = {
                    'Revision': payment_condition_data["revision"],
                    'NumeroCondicionPago': payment_condition_data["payment_condition_number"],
                    'TiposPagos_Id': payment_condition_data["id_type_payment"],
                    'Ordenes_Id': payment_condition_data["id_order"],
                    'Empresas_Id': payment_condition_data["id_company"],
                }
                for attr, value in payment_condition_attrs.items():
                    if value and getattr(payment_condition, attr) != value:
                        setattr(payment_condition, attr, value)
                return True
            else:
                return False
            
    def delete(id_payment_condition):
        with session_scope() as session:
            rut = session.get(PaymentCondition, id_payment_condition)
            if rut:
                session.delete(rut)
                return True
            
    # def get_payment_condition(id_order):
    #     with session_scope() as session:
    #         payment_condition = session.query(PaymentCondition).filter_by(Ordenes_Id=id_order).first()
    #         if payment_condition:
    #             return {
    #                 "id": payment_condition.Id,
    #                 "revision": payment_condition.Revision,
    #                 "payment_condition_number": payment_condition.NumeroCondicionPago,
    #                 "id_type_payment": payment_condition.TiposPagos_Id,
    #             }
    #         else:
    #             return False
    def get_payment_condition(id_order):
        with session_scope() as session:
            payments_conditions = session.query(PaymentCondition).filter(PaymentCondition.Ordenes_Id == id_order).all()
            payments_conditions_list = [
                {
                    "id": payment_condition.Id,
                    "revision": payment_condition.Revision,
                    "payment_condition_number": payment_condition.NumeroCondicionPago,
                    "id_type_payment": payment_condition.TiposPagos_Id,
                }
                for payment_condition in payments_conditions
            ]
            return payments_conditions_list

class PaymentsTypes(Base):
    __tablename__ = 'tipospagos'
    Id = Column(Integer, primary_key=True)
    TipoPago = Column(String(20))


    def read():
        with session_scope() as session:
            payment_types = session.query(PaymentsTypes).all()
            types_payments_list = [
                {
                    "id": payment_type.Id,
                    "payment_type": payment_type.TipoPago,
                    }
                for payment_type in payment_types
            ]
            return types_payments_list
        
    def find_payments_types(id_type_payment):
        with session_scope() as session:
            payment_type = session.query(PaymentsTypes).filter_by(Id=id_type_payment).first()
            if payment_type:
                return {
                    "payment_type": payment_type.TipoPago,
                }
            else:
                return False