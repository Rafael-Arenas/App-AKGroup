from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.models.base import Base
from src.backend.models.core.companies import Company, CompanyTypeEnum
from src.backend.models.core.staff import Staff
from src.backend.models.core.addresses import Address, AddressType
from src.backend.models.lookups import Currency
from src.backend.models.lookups import QuoteStatus
from src.backend.models.business.quotes import Quote
from src.backend.services.business.quote_service import QuoteService
from src.backend.repositories.business.quote_repository import QuoteRepository
from src.shared.schemas.business.quote import QuoteCreate
from src.backend.services.business.order_service import OrderService
from src.backend.repositories.business.order_repository import OrderRepository

# Database setup
engine = create_engine("sqlite:///./app_akgroup.db")
Session = sessionmaker(bind=engine)
db = Session()

def verify():
    print("Starting dynamic numbering verification...")
    
    # 1. Look for existing test entities or create them
    company1 = db.query(Company).filter(Company.trigram == 'AKG').first()
    if not company1:
        print("AKG company not found!")
        return
        
    company2 = db.query(Company).filter(Company.trigram == 'SIL').first()
    if not company2:
        print("SIL company not found!")
        return
        
    staff = db.query(Staff).first()
    
    # 2. Test QuoteService for AKG
    quote_service = QuoteService(QuoteRepository(db), db)
    
    print("\n--- Testing AKG Sequence ---")
    q1 = quote_service.create(QuoteCreate(
        quote_number="STRING",
        subject="AKG Quote 1",
        company_id=company1.id,
        staff_id=staff.id,
        status_id=1,
        quote_date=date.today(),
        currency_id=1
    ), staff.id)
    print(f"AKG Quote 1: {q1.quote_number}")
    
    q2 = quote_service.create(QuoteCreate(
        quote_number="STRING",
        subject="AKG Quote 2",
        company_id=company1.id,
        staff_id=staff.id,
        status_id=1,
        quote_date=date.today(),
        currency_id=1
    ), staff.id)
    print(f"AKG Quote 2: {q2.quote_number}")

    print("\n--- Testing SIL Sequence ---")
    q3 = quote_service.create(QuoteCreate(
        quote_number="STRING",
        subject="SIL Quote 1",
        company_id=company2.id,
        staff_id=staff.id,
        status_id=1,
        quote_date=date.today(),
        currency_id=1
    ), staff.id)
    print(f"SIL Quote 1: {q3.quote_number}")

    print("\n--- Testing Shared Sequence (Order) ---")
    order_service = OrderService(OrderRepository(db), db)
    o1 = order_service.create_from_quote(q1.id, staff.id)
    print(f"Order for AKG (from Q1): {o1.order_number}")
    
    db.commit()
    print("\nVerification successful!")

if __name__ == "__main__":
    verify()
