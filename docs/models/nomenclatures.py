from sqlalchemy import Column, Integer, String, ForeignKey, Float, select
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from databases.connection import session_scope
from models.base import metadata


Base = declarative_base(metadata=metadata)

class Nomenclatures(Base):
    __tablename__ = 'nomenclaturas'
    Id = Column(Integer, primary_key=True)
    Revision = Column(String(2))
    Referencia = Column(String(50))
    DesignacionFR = Column(String(150))
    DesignacionEN = Column(String(150))
    DesignacionES = Column(String(150))
    Dimensiones = Column(String(50))
    Peso = Column(Float)
    CantidadStock = Column(Integer)
    PrecioCompraCLP = Column(Float)
    PrecioVentaCLP = Column(Float)
    PrecioCompraEUR = Column(Float)
    PrecioVentaEUR = Column(Float)
    ImagenURL = Column(String(500))
    PlanoURL = Column(String(500))
    TiposVentas_Id = Column(Integer, ForeignKey('tiposventas.Id'))

    def add(new_nomenclature_data):
        with session_scope() as session:
            nomenclature = Nomenclatures(
                Revision=new_nomenclature_data["revision"],
                Referencia=new_nomenclature_data["reference"],
                DesignacionFR=new_nomenclature_data["designation_fr"],
                DesignacionEN=new_nomenclature_data["designation_en"],
                DesignacionES=new_nomenclature_data["designation_es"], 
                Dimensiones=new_nomenclature_data["dimensions"], 
                Peso=new_nomenclature_data["weight"],
                CantidadStock=new_nomenclature_data["quantity"],
                PrecioCompraCLP=new_nomenclature_data["price_purchase_clp"],
                PrecioVentaCLP=new_nomenclature_data["price_sale_clp"],
                PrecioCompraEUR=new_nomenclature_data["price_purchase_eur"],
                PrecioVentaEUR=new_nomenclature_data["price_sale_eur"], 
                ImagenURL=new_nomenclature_data["image_url"],
                PlanoURL=new_nomenclature_data["plan_url"], 
                TiposVentas_Id=new_nomenclature_data["id_sale_type"])
            session.add(nomenclature)
            return True


    def edit(edit_nomenclature_data):
        with session_scope() as session:
            Nomenclature = session.query(Nomenclatures).filter_by(Id=edit_nomenclature_data["id_nomenclature"]).first()
            if Nomenclature:
                Nomenclature_attrs = {
                    'Revision': edit_nomenclature_data["revision"],
                    'Referencia': edit_nomenclature_data["reference"],
                    'DesignacionFR': edit_nomenclature_data["designation_fr"],
                    'DesignacionEN': edit_nomenclature_data["designation_en"],
                    'DesignacionES': edit_nomenclature_data["designation_es"],
                    'Dimensiones': edit_nomenclature_data["dimensions"],
                    'Peso': edit_nomenclature_data["weight"],
                    'CantidadStock': edit_nomenclature_data["quantity"],
                    'PrecioCompraCLP': edit_nomenclature_data["price_purchase_clp"],
                    'PrecioVentaCLP': edit_nomenclature_data["price_sale_clp"],
                    'PrecioCompraEUR': edit_nomenclature_data["price_purchase_eur"],
                    'PrecioVentaEUR': edit_nomenclature_data["price_sale_eur"],
                    'ImagenURL': edit_nomenclature_data["image_url"],
                    'PlanoURL': edit_nomenclature_data["plan_url"],
                    'TiposVentas_Id': edit_nomenclature_data["id_sale_type"],
                }
                for attr, value in Nomenclature_attrs.items():
                    if value and getattr(Nomenclature, attr) != value:
                        setattr(Nomenclature, attr, value)
                return True
            else:
                return False

    def delete(id_nomenclature):
        with session_scope() as session:
            nomenclatures = session.get(Nomenclatures, id_nomenclature)
            if nomenclatures:
                session.delete(nomenclatures)
                return True

    def read(id_nomenclature):
        with session_scope() as session:
            nomenclature = session.query(Nomenclatures).filter_by(Id=id_nomenclature).first()
            if nomenclature:
                return {
                    "revision": nomenclature.Revision,
                    "reference": nomenclature.Referencia,
                    "designation_fr": nomenclature.DesignacionFR,
                    "designation_en": nomenclature.DesignacionEN,
                    "designation_es": nomenclature.DesignacionES,
                    "dimensions": nomenclature.Dimensiones,
                    "weight": nomenclature.Peso,
                    "quantity": nomenclature.CantidadStock,
                    "price_purchase_clp": nomenclature.PrecioCompraCLP,
                    "price_sale_clp": nomenclature.PrecioVentaCLP,
                    "price_purchase_eur": nomenclature.PrecioCompraEUR,
                    "price_sale_eur": nomenclature.PrecioVentaEUR,
                    "image_url": nomenclature.ImagenURL,
                    "plan_url": nomenclature.PlanoURL,
                    "id_sale_type": nomenclature.TiposVentas_Id,
                }
            else:
                return "Nomenclatura no encontrada"
            
    def read_only_designation(id_nomenclature):
        with session_scope() as session:
            nomenclature = session.query(Nomenclatures).filter_by(Id=id_nomenclature).first()
            if nomenclature:
                return {
                    "designation_fr": nomenclature.DesignacionFR,
                    "designation_en": nomenclature.DesignacionEN,
                    "designation_es": nomenclature.DesignacionES,
                    "stock_quantity": nomenclature.CantidadStock,
                }
            else:
                return "Nomenclaturas no encontrada"
            
    def latest_nomenclatures():
        with session_scope() as session:
            nomenclatures = session.query(Nomenclatures).order_by(Nomenclatures.Id.desc()).limit(8).all()
            nomenclatures_list = [
                {
                    "id": nomenclature.Id,
                    "revision": nomenclature.Revision,
                    "reference": nomenclature.Referencia,
                    "designation_fr": nomenclature.DesignacionFR,
                    "designation_en": nomenclature.DesignacionEN,
                    "designation_es": nomenclature.DesignacionES,
                    "dimensions": nomenclature.Dimensiones,
                    "weight": nomenclature.Peso,
                    "quantity": nomenclature.CantidadStock,
                    "price_purchase_clp": nomenclature.PrecioCompraCLP,
                    "price_sale_clp": nomenclature.PrecioVentaCLP,
                    "price_purchase_eur": nomenclature.PrecioCompraEUR,
                    "price_sale_eur": nomenclature.PrecioVentaEUR,
                    "image_url": nomenclature.ImagenURL,
                    "plan_url": nomenclature.PlanoURL,
                    "id_sale_type": nomenclature.TiposVentas_Id,
                }
                for nomenclature in nomenclatures
            ]
            return nomenclatures_list

    def read_all():
        with session_scope() as session:
            nomenclatures = session.query(Nomenclatures).all()
            nomenclatures_list = [
                {
                    "id": nomenclature.Id,
                    "revision": nomenclature.Revision,
                    "reference": nomenclature.Referencia,
                    "designation_fr": nomenclature.DesignacionFR,
                    "designation_en": nomenclature.DesignacionEN,
                    "designation_es": nomenclature.DesignacionES,
                    "dimensions": nomenclature.Dimensiones,
                    "weight": nomenclature.Peso,
                    "quantity": nomenclature.CantidadStock,
                    "price_purchase_clp": nomenclature.PrecioCompraCLP,
                    "price_sale_clp": nomenclature.PrecioVentaCLP,
                    "price_purchase_eur": nomenclature.PrecioCompraEUR,
                    "price_sale_eur": nomenclature.PrecioVentaEUR,
                    "image_url": nomenclature.ImagenURL,
                    "plan_url": nomenclature.PlanoURL,
                    "id_sale_type": nomenclature.TiposVentas_Id,
                }
                for nomenclature in nomenclatures
            ]
            return nomenclatures_list

    def find_selected(name_nomenclature, designation):
        with session_scope() as session:
            nomenclature = session.query(Nomenclatures).filter(getattr(Nomenclatures, designation)==name_nomenclature).first()
            if nomenclature:
                return {
                    "id": nomenclature.Id,
                    "revision": nomenclature.Revision,
                    "reference": nomenclature.Referencia,
                    "designation_fr": nomenclature.DesignacionFR,
                    "designation_en": nomenclature.DesignacionEN,
                    "designation_es": nomenclature.DesignacionES,
                    "dimensions": nomenclature.Dimensiones,
                    "weight": nomenclature.Peso,
                    "quantity": nomenclature.CantidadStock,
                    "price_purchase_clp": nomenclature.PrecioCompraCLP,
                    "price_sale_clp": nomenclature.PrecioVentaCLP,
                    "price_purchase_eur": nomenclature.PrecioCompraEUR,
                    "price_sale_eur": nomenclature.PrecioVentaEUR,
                    "image_url": nomenclature.ImagenURL,
                    "plan_url": nomenclature.PlanoURL,
                    "id_sale_type": nomenclature.TiposVentas_Id,
                }
            else:
                return "Nomenclatura no encontrada"
    
    def find_nomenclatures(name_nomenclature, language):
        with session_scope() as session:
            if language == "ES":
                nomenclatures = session.query(Nomenclatures).filter(Nomenclatures.DesignacionES.like(f'%{name_nomenclature}%')).all()            
            elif language == "EN":
                nomenclatures = session.query(Nomenclatures).filter(Nomenclatures.DesignacionEN.like(f'%{name_nomenclature}%')).all()            
            else:
                nomenclatures = session.query(Nomenclatures).filter(Nomenclatures.DesignacionFR.like(f'%{name_nomenclature}%')).all()          
            nomenclatures_list = [
                {
                    "id": nomenclature.Id,
                    "revision": nomenclature.Revision,
                    "reference": nomenclature.Referencia,
                    "designation_fr": nomenclature.DesignacionFR,
                    "designation_en": nomenclature.DesignacionEN,
                    "designation_es": nomenclature.DesignacionES,
                    "dimensions": nomenclature.Dimensiones,
                    "weight": nomenclature.Peso,
                    "quantity": nomenclature.CantidadStock,
                    "price_purchase_clp": nomenclature.PrecioCompraCLP,
                    "price_sale_clp": nomenclature.PrecioVentaCLP,
                    "price_purchase_eur": nomenclature.PrecioCompraEUR,
                    "price_sale_eur": nomenclature.PrecioVentaEUR,
                    "image_url": nomenclature.ImagenURL,
                    "plan_url": nomenclature.PlanoURL,
                    "id_sale_type": nomenclature.TiposVentas_Id,
                }
                for nomenclature in nomenclatures
            ]
            return nomenclatures_list    