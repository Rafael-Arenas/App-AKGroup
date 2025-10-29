from sqlalchemy import Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.exc import IntegrityError
from databases.connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class Company(Base):
    __tablename__ = 'empresas'
    Id = Column(Integer, primary_key=True)
    Nombre = Column(String(150))
    Trigrama = Column(String(6))
    DireccionPrincipal = Column(String(200))
    Telefono = Column(String(20))
    SitioWeb = Column(String(100))
    Intracomunitario = Column(String(50))
    FechaCreacion = Column(String(50))
    TiposEmpresas_Id = Column(Integer, ForeignKey('tiposempresas.Id'))
    Paises_Id = Column(Integer, ForeignKey('paises.Id'))
    Ciudades_Id = Column(Integer, ForeignKey('ciudades.Id'))
    ciudad = relationship('City', back_populates='empresas')
    pais = relationship('Country', back_populates='empresas')
    
    
    def add(new_company_data):
        with session_scope() as session:
            company = Company(
                Nombre=new_company_data['name'], 
                Trigrama=new_company_data['trigram'], 
                DireccionPrincipal=new_company_data['address'], 
                Telefono=new_company_data['phone'], 
                SitioWeb=new_company_data['web'],
                Intracomunitario=new_company_data['intra'], 
                FechaCreacion=new_company_data['hour_creation'], 
                TiposEmpresas_Id=new_company_data['id_type_company'], 
                Paises_Id=new_company_data['id_country'], 
                Ciudades_Id=new_company_data['id_city']
            )
            session.add(company)
            session.flush()
            return company.Id

    def edit(edit_company_data):
        with session_scope() as session:
            company = session.query(Company).filter_by(Id=edit_company_data["id_company"]).first()
            if company:
                company_attrs = {
                    'Nombre': edit_company_data["name"],
                    'Trigrama': edit_company_data["trigram"],
                    'DireccionPrincipal': edit_company_data["address"],
                    'Telefono': edit_company_data["phone"],
                    'SitioWeb': edit_company_data["web"],
                    'Intracomunitario': edit_company_data["intra"],
                    'TiposEmpresas_Id': edit_company_data["id_type_company"],
                    'Paises_Id': edit_company_data["id_country"],
                    'Ciudades_Id': edit_company_data["id_city"]
                }
                for attr, value in company_attrs.items():
                    if value and getattr(company, attr) != value:
                        setattr(company, attr, value)
                return True
            else:
                return False


    def delete(id_company):
        with session_scope() as session:
            company = session.get(Company, id_company)
            if company:
                session.delete(company)
                return True

    def read(id_company):
        with session_scope() as session:
            company = session.query(Company).filter_by(Id=id_company).first()
            if company:
                return {
                    "name": company.Nombre,
                    "trigram": company.Trigrama,
                    "main_address": company.DireccionPrincipal,
                    "phone": company.Telefono,
                    "web_site": company.SitioWeb,
                    "intracommunity": company.Intracomunitario,
                    "creation_date": company.FechaCreacion,
                    "id_type_company": company.TiposEmpresas_Id,
                    "id_country": company.Paises_Id,
                    "id_city": company.Ciudades_Id,
                }
            else:
                return "Empresa no encontrada"

    def get_name_company(id_company):
        with session_scope() as session:
            company = session.query(Company).filter_by(Id=id_company).first()
            if company:
                return company.Nombre
            else:
                return "Empresa no encontrada"

    def find_provider_all():
        with session_scope() as session:
            supplier_all = session.query(Company).filter(Company.TiposEmpresas_Id == 2).all()
            supplier_all_list = [
                {
                    "id": supplier.Id,
                    "name": supplier.Nombre,
                    "trigram": supplier.Trigrama,
                    "main_address": supplier.DireccionPrincipal,
                    "phone": supplier.Telefono,
                    "web_site": supplier.SitioWeb,
                    "creation_date": supplier.FechaCreacion,
                    "intracommunity": supplier.Intracomunitario,
                    "id_type_company": supplier.TiposEmpresas_Id,
                    "id_country": supplier.Paises_Id,
                    "id_city": supplier.Ciudades_Id,
                }
                for supplier in supplier_all
            ]
            return supplier_all_list
    
    def find_companies(name_company, identifier):
        with session_scope() as session:
            companies_found = session.query(Company).options(joinedload(Company.ciudad)).options(joinedload(Company.pais)).filter(Company.Nombre.like(f'%{name_company}%'), Company.TiposEmpresas_Id == identifier).all()
            companies_found_list = [
                {
                    "id": company.Id,
                    "name": company.Nombre,
                    "trigram": company.Trigrama,
                    "main_address": company.DireccionPrincipal,
                    "phone": company.Telefono,
                    "web_site": company.SitioWeb,
                    "intracommunity": company.Intracomunitario,
                    "creation_date": company.FechaCreacion,
                    "id_type_company": company.TiposEmpresas_Id,
                    "id_country": company.Paises_Id,
                    "id_city": company.Ciudades_Id,
                }
                for company in companies_found
            ]
            return companies_found_list

    def find_selected(name_company):
        with session_scope() as session:
            company = session.query(Company).filter_by(Nombre=name_company).first()
            if company:
                return {
                    "id": company.Id,
                    "name": company.Nombre,
                    "trigram": company.Trigrama,
                    "main_address": company.DireccionPrincipal,
                    "phone": company.Telefono,
                    "web_site": company.SitioWeb,
                    "intracommunity": company.Intracomunitario,
                    "creation_date": company.FechaCreacion,
                    "id_type_company": company.TiposEmpresas_Id,
                    "id_country": company.Paises_Id,
                    "id_city": company.Ciudades_Id,
                }
            else:
                return "Empresa no encontrada"
    
    def latest_companies(identifier):
        with session_scope() as session:
            companies_found = session.query(Company).options(joinedload(Company.ciudad)).options(joinedload(Company.pais)).filter(Company.TiposEmpresas_Id == identifier).order_by(Company.Id.desc()).all()
            companies_found_list = [
                {
                    "id": company.Id,
                    "name": company.Nombre,
                    "trigram": company.Trigrama,
                    "main_address": company.DireccionPrincipal,
                    "phone": company.Telefono,
                    "web_site": company.SitioWeb,
                    "intracommunity": company.Intracomunitario,
                    "creation_date": company.FechaCreacion,
                    "id_type_company": company.TiposEmpresas_Id,
                    "id_country": company.Paises_Id,
                    "id_city": company.Ciudades_Id,
                }
                for company in companies_found
            ]
            return companies_found_list        
    
    def get_companies(identifier):
        with session_scope() as session:
            companies_found = session.query(Company).options(joinedload(Company.ciudad)).options(joinedload(Company.pais)).filter(Company.TiposEmpresas_Id == identifier).all()
            companies_found_list = [
                {
                    "id": company.Id,
                    "name": company.Nombre,
                    "trigram": company.Trigrama,
                    "main_address": company.DireccionPrincipal,
                    "phone": company.Telefono,
                    "web_site": company.SitioWeb,
                    "intracommunity": company.Intracomunitario,
                    "creation_date": company.FechaCreacion,
                    "id_type_company": company.TiposEmpresas_Id,
                    "id_country": company.Paises_Id,
                    "id_city": company.Ciudades_Id,
                }
                for company in companies_found
            ]
            return companies_found_list        
    
class Country(Base):
    __tablename__ = 'paises'
    Id = Column(Integer, primary_key=True)
    Pais = Column(String(50))
    empresas = relationship('Company', back_populates='pais')

    def read():
        with session_scope() as session:
            countries = session.query(Country).all()
            countries_list = [
                {
                    "id": country.Id,
                    "country": country.Pais,
                }
                for country in countries
            ]
            return countries_list

    def find_country(id_country):
        with session_scope() as session:
            country = session.query(Country).filter_by(Id=id_country).first()
            if country:
                return {
                    "country": country.Pais,
                }
            else:
                return "pais no encontrada"

    def get_name(id_country):
        with session_scope() as session:
            country = session.query(Country).filter_by(Id=id_country).first()
            if country:
                return country.Pais
  
            else:
                return "pais no encontrada"
            
class City(Base):
    __tablename__ = 'ciudades'
    Id = Column(Integer, primary_key=True)
    Ciudad = Column(String(50))
    Paises_Id = Column(Integer, ForeignKey('paises.Id'))
    empresas = relationship('Company', back_populates='ciudad')

    def find_cities(id_country):
        with session_scope() as session:
            cities = session.query(City).filter(City.Paises_Id == id_country).all()
            cities_country_list = [
                {
                    "id": city.Id,
                    "city": city.Ciudad,
                }
                for city in cities
            ]
            return cities_country_list

    def read():
        with session_scope() as session:
            cities = session.query(City).all()
            cities_list = [
                {
                    "id": city.Id,
                    "city": city.Ciudad,
                    "id_country": city.Paises_Id,
                }
                for city in cities
            ]
            return cities_list

    def find_city(id_city):
        with session_scope() as session:
            city = session.query(City).filter_by(Id=id_city).first()
            if city:
                return city.Ciudad

            else:
                return "Ciudad no encontrada"

    def get_name(id_city):
        with session_scope() as session:
            city = session.query(City).filter_by(Id=id_city).first()
            if city:
                return city.Ciudad
                
            else:
                return "Ciudad no encontrada"


class CompanyType(Base):
    __tablename__ = 'tiposempresas'
    Id = Column(Integer, primary_key=True)
    TipoEmpresa = Column(String(50))
    
    def read():
        with session_scope() as session:
            result = session.query(CompanyType).all()
            company_type_list = [
                {
                    "id": company_type.Id,
                    "company_type": company_type.TipoEmpresa,
                }
                for company_type in result
            ]
            return company_type_list

    def get_name(id_type_company):
        with session_scope() as session:
            result = session.query(CompanyType).filter_by(Id=id_type_company).first()
            if result:
                return result.TipoEmpresa
            else:
                return "Tipo de empresa no encontrada"
        

