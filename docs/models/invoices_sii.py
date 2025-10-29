from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class InvoicesSii(Base):
    __tablename__ = 'facturassii'
    Id = Column(Integer, primary_key=True)
    Revision = Column(String(2))
    NumeroFactura = Column(String(50))
    FechaAproximativa = Column(String(50))
    Estado = Column(String(50))
    Ordenes_Id = Column(Integer, ForeignKey('ordenes.Id'))

    def add(revision, number_invoice, approximate_date, status, id_order):
        with session_scope() as session:
            new_invoice = InvoicesSii(Revision=revision, NumeroFactura=number_invoice, FechaAproximativa=approximate_date, Estado=status, Ordenes_Id=id_order)
            session.add(new_invoice)
            return True

    def edit(revision, number_invoice, approximate_date, status, id_invoice_sii):
        with session_scope() as session:
            invoice = session.query(InvoicesSii).get(id_invoice_sii)
            if invoice:
                invoice.Revision = revision
                invoice.NumeroFactura = number_invoice
                invoice.FechaAproximativa = approximate_date
                invoice.Estado = status
                return True

    def delete(id_invoice_sii):

        with session_scope() as session:
            invoice = session.get(InvoicesSii, id_invoice_sii)
            if invoice:
                session.delete(invoice)
                return True
            
    def read(id_order):
        with session_scope() as session:
            invoice = session.query(InvoicesSii).filter(InvoicesSii.Ordenes_Id == id_order).first()
            if invoice:
                return {
                    "id": invoice.Id,
                    "number_invoice": invoice.NumeroFactura,
                    "approximate_date": invoice.FechaAproximativa,
                    "status": invoice.Estado,
                }
            else:
                return False

            
    def get_invoice(id_order):
        with session_scope() as session:
            invoices = session.query(InvoicesSii).filter(InvoicesSii.Ordenes_Id == id_order).all()
            invoices_list = [
                {
                    "id": invoice.Id,
                    "revision": invoice.Revision,
                    "number_invoice": invoice.NumeroFactura,
                    "approximate_date": invoice.FechaAproximativa,
                    "status": invoice.Estado,

                }
                for invoice in invoices
            ]
            return invoices_list