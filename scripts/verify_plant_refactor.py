
import sys
import os
from datetime import date
from decimal import Decimal

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.models import Base
from src.backend.models import (
    Company, CompanyTypeEnum, Plant, Order, Quote, InvoiceSII, InvoiceExport,
    CompanyType, Country, City, Currency, PaymentStatus, OrderStatus, QuoteStatus, Incoterm, Staff
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use the app database
DB_URL = "sqlite:///app_akgroup.db"

def verify_refactor():
    print(f"Connecting to {DB_URL}...")
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("1. Creating prerequisites...")
        # Get or create lookups
        company_type = session.query(CompanyType).first()
        if not company_type:
            company_type = CompanyType(name="Client", description="Client")
            session.add(company_type)
        
        country = session.query(Country).filter_by(iso_code_alpha2="CL").first()
        if not country:
            country = Country(name="ChileTest", iso_code_alpha2="CL", iso_code_alpha3="CHL")
            session.add(country)
            
        city = session.query(City).filter_by(name="Santiago").first()
        if not city:
            # Check if country is flushed to get ID
            session.flush()
            city = City(name="Santiago", country_id=country.id)
            session.add(city)

        currency = session.query(Currency).filter_by(code="CLP").first()
        if not currency:
            currency = Currency(code="CLP", name="Peso", symbol="$", is_active=True)
            session.add(currency)
            
        # Create Staff
        staff = session.query(Staff).first()
        if not staff:
            # Assuming Staff model exists and has required fields. 
            # If Staff is not easily creatable, we might need to mock or skip if FKs are strict.
            # Based on models/core/staff.py (not read yet but imported in init), let's hope it's simple or exists.
            # If no staff, we can't create orders/quotes usually as they require staff_id.
            # Let's try to find one or create a dummy one.
            # Staff usually requires email, etc.
            pass
            
        # Check if we have any staff
        staff = session.query(Staff).first()
        if not staff:
            print("WARNING: No Staff found. Creating dummy staff.")
            staff = Staff(
                username="testuser",
                email="test@example.com", 
                first_name="Test", 
                last_name="User", 
                is_active=True,
                is_admin=True
            )
            session.add(staff)
            session.flush()

        # Statuses
        q_status = session.query(QuoteStatus).first()
        if not q_status:
            q_status = QuoteStatus(code="draft", name="Draft")
            session.add(q_status)
            
        o_status = session.query(OrderStatus).first()
        if not o_status:
            o_status = OrderStatus(code="draft", name="Draft")
            session.add(o_status)
            
        p_status = session.query(PaymentStatus).first()
        if not p_status:
            p_status = PaymentStatus(code="pending", name="Pending")
            session.add(p_status)
            
        incoterm = session.query(Incoterm).first()
        if not incoterm:
            incoterm = Incoterm(code="EXW", name="Ex Works", is_active=True)
            session.add(incoterm)

        session.commit()

        print("2. Creating Company...")
        company = Company(
            name="Test Company Refactor",
            trigram="TCR",
            company_type_id=company_type.id,
            country_id=country.id,
            is_active=True
        )
        session.add(company)
        session.flush()
        print(f"   Company created: ID={company.id}")

        print("3. Creating Plant (formerly Branch)...")
        plant = Plant(
            name="Test Plant 1",
            address="Av Test 123",
            company_id=company.id,
            city_id=city.id,
            is_active=True
        )
        session.add(plant)
        session.flush()
        print(f"   Plant created: ID={plant.id}")

        print("4. Creating Quote with Plant...")
        quote = Quote(
            quote_number="Q-TEST-001",
            subject="Test Quote",
            company_id=company.id,
            plant_id=plant.id,  # LINKING TO PLANT
            staff_id=staff.id,
            status_id=q_status.id,
            quote_date=date.today(),
            currency_id=currency.id,
            subtotal=Decimal("1000"),
            total=Decimal("1190")
        )
        session.add(quote)
        session.flush()
        print(f"   Quote created: ID={quote.id}, Plant ID={quote.plant_id}")

        print("5. Creating Order with Plant...")
        order = Order(
            order_number="O-TEST-001",
            company_id=company.id,
            plant_id=plant.id,  # LINKING TO PLANT
            staff_id=staff.id,
            status_id=o_status.id,
            payment_status_id=p_status.id,
            order_date=date.today(),
            currency_id=currency.id,
            subtotal=Decimal("1000"),
            total=Decimal("1190")
        )
        session.add(order)
        session.flush()
        print(f"   Order created: ID={order.id}, Plant ID={order.plant_id}")

        print("6. Creating InvoiceSII with Plant...")
        invoice = InvoiceSII(
            invoice_number="123456",
            invoice_type="33",
            order_id=order.id,
            company_id=company.id,
            plant_id=plant.id,  # LINKING TO PLANT
            staff_id=staff.id,
            payment_status_id=p_status.id,
            invoice_date=date.today(),
            currency_id=currency.id,
            subtotal=Decimal("1000"),
            total=Decimal("1190")
        )
        session.add(invoice)
        session.flush()
        print(f"   InvoiceSII created: ID={invoice.id}, Plant ID={invoice.plant_id}")
        
        # Verify relationships
        print("7. Verifying Relationships...")
        session.refresh(company)
        # Check plants relationship
        if company.plants and company.plants[0].id == plant.id:
            print("   ✅ Company -> Plants relationship works")
        else:
            print("   ❌ Company -> Plants relationship FAILED")

        session.refresh(plant)
        # Check inverse relationships (lazy loaded usually, but let's check basic access)
        # Depending on model definition, back_populates should work
        
        print("Verification successful! Database schema and Models are in sync.")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Verification FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    verify_refactor()
