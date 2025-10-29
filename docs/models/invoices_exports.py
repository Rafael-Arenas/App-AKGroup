from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class InvoicesExports(Base):
    __tablename__ = 'facturasexportaciones'
    Id = Column(Integer, primary_key=True)
    Revision = Column(String(2))
    NumeroFactura = Column(String(50))
    Ordenes_Id = Column(Integer, ForeignKey('ordenes.Id'))

    def add(number_invoice_export, revision_invoice_export, id_order):
        with session_scope() as session:
            new_invoice_export = InvoicesExports(NumeroFactura=number_invoice_export, Revision=revision_invoice_export,Ordenes_Id=id_order)
            session.add(new_invoice_export)
            return True
        
    def edit(revision, number_invoice_export, id_invoice_export):
        with session_scope() as session:
            invoice = session.query(InvoicesExports).get(id_invoice_export)
            if invoice:
                invoice.Revision = revision
                invoice.NumeroFactura = number_invoice_export
                return True
            
    def delete(id_invoice_export):

        with session_scope() as session:
            invoice = session.get(InvoicesExports, id_invoice_export)
            if invoice:
                session.delete(invoice)
                return True


    def read(id_order):
        with session_scope() as session:
            invoice = session.query(InvoicesExports).filter(InvoicesExports.Ordenes_Id == id_order).first()
            if invoice:
                return {
                    "id": invoice.Id,
                    "number_invoice": invoice.NumeroFactura,
                }
            else:
                return False
            
            
    def get_invoice(id_order):
        with session_scope() as session:
            invoices = session.query(InvoicesExports).filter(InvoicesExports.Ordenes_Id == id_order).all()
            invoices_list = [
                {
                    "id": invoice.Id,
                    "number_invoice": invoice.NumeroFactura,
                    "revision": invoice.Revision,
                }
                for invoice in invoices
            ]
            return invoices_list