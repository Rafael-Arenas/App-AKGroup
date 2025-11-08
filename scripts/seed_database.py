"""
Script para poblar la base de datos con datos ficticios.

Este script genera datos de prueba realistas para todos los modelos del sistema
usando la librería Faker. Respeta el orden de dependencias entre tablas.

Usage:
    # Con base de datos por defecto
    python scripts/seed_database.py

    # Con base de datos personalizada
    python scripts/seed_database.py sqlite:///custom.db

    # Especificar cantidad de registros
    python scripts/seed_database.py sqlite:///app_akgroup.db --count 100

Example:
    >>> from scripts.seed_database import seed_all
    >>> seed_all(count=50)
    ✓ Seeding lookups...
    ✓ Seeding core models...
    ✓ Seeding business models...
    Database seeded successfully with 50 records per model!
"""

import random
import sys
from decimal import Decimal
from typing import List, Optional

import pendulum
from faker import Faker
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.backend.models import (
    # Lookups
    City,
    CompanyType,
    Country,
    Currency,
    FamilyType,
    Incoterm,
    Matter,
    OrderStatus,
    PaymentStatus,
    QuoteStatus,
    SalesType,
    Unit,
    # Core
    Address,
    AddressType,
    Branch,
    Company,
    CompanyRut,
    CompanyTypeEnum,
    Contact,
    Note,
    NotePriority,
    PriceCalculationMode,
    Product,
    ProductComponent,
    ProductType,
    Service,
    Staff,
    # Business
    DeliveryDate,
    DeliveryOrder,
    Order,
    PaymentCondition,
    Quote,
    QuoteProduct,
    Transport,
)

# Initialize Faker with Spanish (Colombia) locale
fake = Faker("es_CO")


def generate_phone() -> str:
    """
    Genera un número de teléfono válido que cumple con PhoneValidator.

    Returns:
        Teléfono en formato +569XXXXXXXX (Chile móvil)
    """
    return f"+56{random.randint(900000000, 999999999)}"


def seed_lookups(session: Session) -> dict:
    """
    Pobla todas las tablas de lookups (catálogos).

    Args:
        session: Sesión de SQLAlchemy

    Returns:
        Dict con los registros creados para usar como FK
    """
    logger.info("📋 Seeding lookup tables...")

    # ========== COUNTRIES ==========
    countries_data = [
        {"name": "Chile", "iso_code_alpha2": "CL", "iso_code_alpha3": "CHL"},
        {"name": "Colombia", "iso_code_alpha2": "CO", "iso_code_alpha3": "COL"},
        {"name": "Francia", "iso_code_alpha2": "FR", "iso_code_alpha3": "FRA"},
        {"name": "España", "iso_code_alpha2": "ES", "iso_code_alpha3": "ESP"},
        {"name": "Estados Unidos", "iso_code_alpha2": "US", "iso_code_alpha3": "USA"},
        {"name": "México", "iso_code_alpha2": "MX", "iso_code_alpha3": "MEX"},
        {"name": "Argentina", "iso_code_alpha2": "AR", "iso_code_alpha3": "ARG"},
        {"name": "Perú", "iso_code_alpha2": "PE", "iso_code_alpha3": "PER"},
        {"name": "Brasil", "iso_code_alpha2": "BR", "iso_code_alpha3": "BRA"},
        {"name": "Alemania", "iso_code_alpha2": "DE", "iso_code_alpha3": "DEU"},
    ]

    countries = []
    for data in countries_data:
        country = Country(**data)
        session.add(country)
        countries.append(country)
    session.flush()
    logger.success(f"  ✓ Created {len(countries)} countries")

    # ========== CITIES ==========
    cities_data = [
        # Chile
        {"name": "Santiago", "country_id": countries[0].id},
        {"name": "Valparaíso", "country_id": countries[0].id},
        {"name": "Concepción", "country_id": countries[0].id},
        # Colombia
        {"name": "Bogotá", "country_id": countries[1].id},
        {"name": "Medellín", "country_id": countries[1].id},
        {"name": "Cali", "country_id": countries[1].id},
        # Francia
        {"name": "París", "country_id": countries[2].id},
        {"name": "Lyon", "country_id": countries[2].id},
        # España
        {"name": "Madrid", "country_id": countries[3].id},
        {"name": "Barcelona", "country_id": countries[3].id},
        # USA
        {"name": "New York", "country_id": countries[4].id},
        {"name": "Los Angeles", "country_id": countries[4].id},
    ]

    cities = []
    for data in cities_data:
        city = City(**data)
        session.add(city)
        cities.append(city)
    session.flush()
    logger.success(f"  ✓ Created {len(cities)} cities")

    # ========== COMPANY TYPES ==========
    company_types_data = [
        {"name": "CLIENT", "description": "Empresa que adquiere productos o servicios"},
        {
            "name": "SUPPLIER",
            "description": "Empresa que provee productos o servicios",
        },
    ]

    company_types = []
    for data in company_types_data:
        company_type = CompanyType(**data)
        session.add(company_type)
        company_types.append(company_type)
    session.flush()
    logger.success(f"  ✓ Created {len(company_types)} company types")

    # ========== CURRENCIES ==========
    currencies_data = [
        {"code": "CLP", "name": "Chilean Peso", "symbol": "$"},
        {"code": "USD", "name": "US Dollar", "symbol": "US$"},
        {"code": "EUR", "name": "Euro", "symbol": "€"},
        {"code": "COP", "name": "Colombian Peso", "symbol": "$"},
    ]

    currencies = []
    for data in currencies_data:
        currency = Currency(**data, is_active=True)
        session.add(currency)
        currencies.append(currency)
    session.flush()
    logger.success(f"  ✓ Created {len(currencies)} currencies")

    # ========== INCOTERMS ==========
    incoterms_data = [
        {"code": "EXW", "name": "Ex Works", "description": "Vendedor entrega en su establecimiento"},
        {"code": "FCA", "name": "Free Carrier", "description": "Vendedor entrega al transportista"},
        {"code": "FOB", "name": "Free On Board", "description": "Vendedor entrega en el puerto"},
        {"code": "CIF", "name": "Cost Insurance and Freight", "description": "Incluye costo, seguro y flete"},
        {"code": "DAP", "name": "Delivered At Place", "description": "Entregado en lugar"},
        {"code": "DDP", "name": "Delivered Duty Paid", "description": "Entregado con impuestos pagados"},
    ]

    incoterms = []
    for data in incoterms_data:
        incoterm = Incoterm(**data, is_active=True)
        session.add(incoterm)
        incoterms.append(incoterm)
    session.flush()
    logger.success(f"  ✓ Created {len(incoterms)} incoterms")

    # ========== UNITS ==========
    units_data = [
        {"code": "pcs", "name": "Pieces", "description": "Piezas/unidades"},
        {"code": "kg", "name": "Kilogram", "description": "Kilogramo"},
        {"code": "m", "name": "Meter", "description": "Metro"},
        {"code": "l", "name": "Liter", "description": "Litro"},
        {"code": "box", "name": "Box", "description": "Caja"},
        {"code": "set", "name": "Set", "description": "Conjunto"},
    ]

    units = []
    for data in units_data:
        unit = Unit(**data, is_active=True)
        session.add(unit)
        units.append(unit)
    session.flush()
    logger.success(f"  ✓ Created {len(units)} units")

    # ========== FAMILY TYPES ==========
    family_types_data = [
        {"name": "Mecánico", "description": "Componentes mecánicos"},
        {"name": "Eléctrico", "description": "Componentes eléctricos"},
        {"name": "Electrónico", "description": "Componentes electrónicos"},
        {"name": "Consumibles", "description": "Materiales consumibles"},
        {"name": "Herramientas", "description": "Herramientas y equipos"},
        {"name": "Servicios", "description": "Servicios profesionales"},
    ]

    family_types = []
    for data in family_types_data:
        family_type = FamilyType(**data)
        session.add(family_type)
        family_types.append(family_type)
    session.flush()
    logger.success(f"  ✓ Created {len(family_types)} family types")

    # ========== MATTERS ==========
    matters_data = [
        {"name": "Acero inoxidable", "description": "Acero resistente a la corrosión"},
        {"name": "Aluminio", "description": "Metal ligero"},
        {"name": "Plástico ABS", "description": "Plástico de alta resistencia"},
        {"name": "Cobre", "description": "Metal conductor"},
        {"name": "Madera", "description": "Material natural"},
        {"name": "Vidrio", "description": "Material transparente"},
    ]

    matters = []
    for data in matters_data:
        matter = Matter(**data)
        session.add(matter)
        matters.append(matter)
    session.flush()
    logger.success(f"  ✓ Created {len(matters)} matters")

    # ========== SALES TYPES ==========
    sales_types_data = [
        {"name": "Retail", "description": "Venta minorista"},
        {"name": "Wholesale", "description": "Venta mayorista"},
        {"name": "Export", "description": "Exportación"},
        {"name": "Domestic", "description": "Mercado local"},
    ]

    sales_types = []
    for data in sales_types_data:
        sales_type = SalesType(**data)
        session.add(sales_type)
        sales_types.append(sales_type)
    session.flush()
    logger.success(f"  ✓ Created {len(sales_types)} sales types")

    # ========== QUOTE STATUSES ==========
    quote_statuses_data = [
        {"code": "draft", "name": "Borrador", "description": "Cotización en edición"},
        {"code": "sent", "name": "Enviada", "description": "Cotización enviada al cliente"},
        {"code": "accepted", "name": "Aceptada", "description": "Cliente aceptó la cotización"},
        {"code": "rejected", "name": "Rechazada", "description": "Cliente rechazó la cotización"},
        {"code": "expired", "name": "Expirada", "description": "Cotización vencida"},
    ]

    quote_statuses = []
    for data in quote_statuses_data:
        quote_status = QuoteStatus(**data)
        session.add(quote_status)
        quote_statuses.append(quote_status)
    session.flush()
    logger.success(f"  ✓ Created {len(quote_statuses)} quote statuses")

    # ========== ORDER STATUSES ==========
    order_statuses_data = [
        {"code": "pending", "name": "Pendiente", "description": "Orden pendiente de confirmación"},
        {"code": "confirmed", "name": "Confirmada", "description": "Orden confirmada"},
        {"code": "in_production", "name": "En Producción", "description": "Orden en fabricación"},
        {"code": "shipped", "name": "Enviada", "description": "Orden despachada"},
        {"code": "delivered", "name": "Entregada", "description": "Orden entregada"},
        {"code": "cancelled", "name": "Cancelada", "description": "Orden cancelada"},
    ]

    order_statuses = []
    for data in order_statuses_data:
        order_status = OrderStatus(**data)
        session.add(order_status)
        order_statuses.append(order_status)
    session.flush()
    logger.success(f"  ✓ Created {len(order_statuses)} order statuses")

    # ========== PAYMENT STATUSES ==========
    payment_statuses_data = [
        {"code": "pending", "name": "Pendiente", "description": "Pago pendiente"},
        {"code": "partial", "name": "Parcial", "description": "Pago parcial realizado"},
        {"code": "paid", "name": "Pagado", "description": "Totalmente pagado"},
        {"code": "overdue", "name": "Vencido", "description": "Pago vencido"},
        {"code": "cancelled", "name": "Cancelado", "description": "Pago cancelado"},
    ]

    payment_statuses = []
    for data in payment_statuses_data:
        payment_status = PaymentStatus(**data)
        session.add(payment_status)
        payment_statuses.append(payment_status)
    session.flush()
    logger.success(f"  ✓ Created {len(payment_statuses)} payment statuses")

    session.commit()

    return {
        "countries": countries,
        "cities": cities,
        "company_types": company_types,
        "currencies": currencies,
        "incoterms": incoterms,
        "units": units,
        "family_types": family_types,
        "matters": matters,
        "sales_types": sales_types,
        "quote_statuses": quote_statuses,
        "order_statuses": order_statuses,
        "payment_statuses": payment_statuses,
    }


def seed_core_models(session: Session, lookups: dict, count: int = 50) -> dict:
    """
    Pobla los modelos core (Staff, Company, Product, etc.).

    Args:
        session: Sesión de SQLAlchemy
        lookups: Dict con registros de lookups
        count: Cantidad de registros a crear

    Returns:
        Dict con los registros creados
    """
    logger.info(f"🏢 Seeding core models ({count} records each)...")

    # ========== SERVICES ==========
    services_data = [
        {"name": "Ventas", "description": "Departamento de ventas"},
        {"name": "Compras", "description": "Departamento de compras"},
        {"name": "Soporte Técnico", "description": "Soporte y asistencia técnica"},
        {"name": "Administración", "description": "Administración general"},
        {"name": "Finanzas", "description": "Departamento financiero"},
        {"name": "Logística", "description": "Logística y distribución"},
    ]

    services = []
    for data in services_data:
        service = Service(**data, is_active=True)
        session.add(service)
        services.append(service)
    session.flush()
    logger.success(f"  ✓ Created {len(services)} services")

    # ========== STAFF ==========
    staff_list = []
    staff_trigrams = set()

    for i in range(min(count, 20)):  # Limitar staff a 20
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = fake.unique.user_name()

        # Generar trigrama único (3 letras)
        base_trigram = None
        if len(last_name) >= 2:
            base_trigram = (first_name[0] + last_name[:2]).upper()
        else:
            base_trigram = (first_name[:3]).upper()

        # Asegurar unicidad
        trigram = base_trigram
        counter = 0
        while trigram in staff_trigrams:
            # Si ya existe, generar uno aleatorio
            trigram = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
            counter += 1
            if counter > 100:  # Evitar loop infinito
                raise ValueError("No se pudo generar trigrama único")

        staff_trigrams.add(trigram)

        staff = Staff(
            username=username,
            email=fake.unique.email(),
            first_name=first_name,
            last_name=last_name,
            trigram=trigram,
            phone=generate_phone(),
            position=random.choice(
                [
                    "Vendedor Senior",
                    "Ejecutivo de Ventas",
                    "Gerente Comercial",
                    "Ingeniero de Ventas",
                ]
            ),
            is_active=True,
            is_admin=i == 0,  # Primer usuario es admin
        )
        session.add(staff)
        staff_list.append(staff)
    session.flush()
    logger.success(f"  ✓ Created {len(staff_list)} staff members")

    # ========== COMPANIES ==========
    companies = []
    used_trigrams = set()

    for i in range(count):
        # Generar trigrama único
        while True:
            trigram = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
            if trigram not in used_trigrams:
                used_trigrams.add(trigram)
                break

        company = Company(
            name=fake.company(),
            trigram=trigram,
            main_address=fake.address(),
            phone=generate_phone(),
            website=fake.url(),
            company_type_id=random.choice(lookups["company_types"]).id,
            country_id=random.choice(lookups["countries"]).id,
            city_id=random.choice(lookups["cities"]).id,
            is_active=True,
        )
        session.add(company)
        companies.append(company)
    session.flush()
    logger.success(f"  ✓ Created {len(companies)} companies")

    # ========== COMPANY RUTS (solo para empresas chilenas) ==========
    ruts = []
    for company in companies[:20]:  # Solo primeras 20 empresas
        # Generar RUT ficticio válido
        rut_number = random.randint(70000000, 99999999)
        dv = _calculate_rut_dv(rut_number)
        rut = CompanyRut(
            rut=f"{rut_number}-{dv}",
            is_main=True,
            company_id=company.id,
        )
        session.add(rut)
        ruts.append(rut)
    session.flush()
    logger.success(f"  ✓ Created {len(ruts)} company RUTs")

    # ========== BRANCHES ==========
    branches = []
    for company in companies[:30]:  # Primeras 30 empresas con sucursales
        num_branches = random.randint(1, 3)
        for j in range(num_branches):
            branch = Branch(
                name=f"{company.name} - Sucursal {j+1}",
                address=fake.address(),
                phone=generate_phone(),
                email=fake.email(),
                company_id=company.id,
                city_id=random.choice(lookups["cities"]).id,
                is_active=True,
            )
            session.add(branch)
            branches.append(branch)
    session.flush()
    logger.success(f"  ✓ Created {len(branches)} branches")

    # ========== CONTACTS ==========
    contacts = []
    for company in companies:
        num_contacts = random.randint(1, 4)
        for j in range(num_contacts):
            contact = Contact(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone=generate_phone(),
                mobile=generate_phone(),
                position=random.choice(
                    [
                        "Gerente de Compras",
                        "Jefe de Proyectos",
                        "Encargado de Compras",
                        "Director Técnico",
                    ]
                ),
                company_id=company.id,
                service_id=random.choice(services).id if random.random() > 0.3 else None,
                is_active=True,
            )
            session.add(contact)
            contacts.append(contact)
    session.flush()
    logger.success(f"  ✓ Created {len(contacts)} contacts")

    # ========== ADDRESSES ==========
    addresses = []
    for company in companies[:40]:  # Primeras 40 empresas con direcciones
        num_addresses = random.randint(1, 2)
        for j in range(num_addresses):
            address = Address(
                address=fake.address(),
                city=random.choice(lookups["cities"]).name,
                postal_code=fake.postcode(),
                country=random.choice(lookups["countries"]).name,
                is_default=j == 0,
                address_type=random.choice(list(AddressType)),
                company_id=company.id,
            )
            session.add(address)
            addresses.append(address)
    session.flush()
    logger.success(f"  ✓ Created {len(addresses)} addresses")

    # ========== PRODUCTS ==========
    products = []

    # Crear ARTICLEs
    for i in range(int(count * 0.6)):  # 60% artículos
        product = Product(
            product_type=ProductType.ARTICLE,
            reference=f"ART-{i+1:04d}",
            designation_es=fake.catch_phrase(),
            designation_en=fake.bs(),
            short_designation=fake.word().upper(),
            revision="A",
            family_type_id=random.choice(lookups["family_types"]).id,
            matter_id=random.choice(lookups["matters"]).id,
            sales_type_id=random.choice(lookups["sales_types"]).id,
            company_id=random.choice(companies).id if random.random() > 0.3 else None,
            purchase_price=Decimal(str(round(random.uniform(10, 500), 2))),
            cost_price=Decimal(str(round(random.uniform(15, 600), 2))),
            sale_price=Decimal(str(round(random.uniform(20, 800), 2))),
            price_calculation_mode=PriceCalculationMode.MANUAL,
            margin_percentage=Decimal(str(round(random.uniform(15, 50), 2))),
            stock_quantity=Decimal(str(random.randint(0, 1000))),
            minimum_stock=Decimal(str(random.randint(10, 100))),
            stock_location=f"A{random.randint(1,10)}-{random.randint(1,20)}",
            net_weight=Decimal(str(round(random.uniform(0.1, 50), 3))),
            gross_weight=Decimal(str(round(random.uniform(0.2, 55), 3))),
            is_active=True,
        )
        session.add(product)
        products.append(product)

    # Crear SERVICEs
    for i in range(int(count * 0.2)):  # 20% servicios
        product = Product(
            product_type=ProductType.SERVICE,
            reference=f"SRV-{i+1:04d}",
            designation_es=f"Servicio de {fake.job()}",
            designation_en=f"{fake.job()} Service",
            short_designation=f"SRV-{fake.word().upper()}",
            family_type_id=lookups["family_types"][-1].id,  # Servicios
            sales_type_id=random.choice(lookups["sales_types"]).id,
            cost_price=Decimal(str(round(random.uniform(50, 500), 2))),
            sale_price=Decimal(str(round(random.uniform(80, 800), 2))),
            price_calculation_mode=PriceCalculationMode.MANUAL,
            stock_quantity=None,  # Servicios no tienen stock
            is_active=True,
        )
        session.add(product)
        products.append(product)

    # Crear NOMENCLATUREs
    for i in range(int(count * 0.2)):  # 20% nomenclaturas
        product = Product(
            product_type=ProductType.NOMENCLATURE,
            reference=f"NOM-{i+1:04d}",
            designation_es=f"Kit {fake.word().capitalize()}",
            designation_en=f"{fake.word().capitalize()} Kit",
            short_designation=f"KIT-{fake.word().upper()}",
            family_type_id=random.choice(lookups["family_types"]).id,
            sales_type_id=random.choice(lookups["sales_types"]).id,
            price_calculation_mode=PriceCalculationMode.FROM_COMPONENTS,
            is_active=True,
        )
        session.add(product)
        products.append(product)

    session.flush()
    logger.success(f"  ✓ Created {len(products)} products")

    # ========== PRODUCT COMPONENTS (BOM) ==========
    # Agregar componentes a algunas nomenclaturas
    nomenclatures = [p for p in products if p.product_type == ProductType.NOMENCLATURE]
    articles = [p for p in products if p.product_type == ProductType.ARTICLE]

    components = []
    for nomenclature in nomenclatures[:20]:  # Primeras 20 nomenclaturas
        num_components = random.randint(2, 5)
        used_components = set()

        for _ in range(num_components):
            component_product = random.choice(articles)
            if component_product.id not in used_components:
                component = ProductComponent(
                    parent_id=nomenclature.id,
                    component_id=component_product.id,
                    quantity=Decimal(str(random.randint(1, 10))),
                    notes=f"Componente para {nomenclature.reference}",
                )
                session.add(component)
                components.append(component)
                used_components.add(component_product.id)

    session.flush()
    logger.success(f"  ✓ Created {len(components)} product components (BOM)")

    # ========== NOTES ==========
    # SKIP notes for now - entity_type and entity_id need proper handling
    notes = []
    logger.success(f"  ✓ Skipped notes (requires polymorphic setup)")

    session.commit()

    return {
        "services": services,
        "staff": staff_list,
        "companies": companies,
        "ruts": ruts,
        "branches": branches,
        "contacts": contacts,
        "addresses": addresses,
        "products": products,
        "components": components,
        "notes": notes,
    }


def seed_business_models(session: Session, lookups: dict, core: dict, count: int = 30) -> dict:
    """
    Pobla los modelos de negocio (Quote, Order, Invoice, etc.).

    Args:
        session: Sesión de SQLAlchemy
        lookups: Dict con registros de lookups
        core: Dict con registros core
        count: Cantidad de registros a crear

    Returns:
        Dict con los registros creados
    """
    logger.info(f"💼 Seeding business models ({count} records)...")

    # Filtrar solo empresas clientes
    client_companies = [
        c
        for c in core["companies"]
        if c.company_type.name == CompanyTypeEnum.CLIENT.value
    ]

    if not client_companies:
        logger.warning("  ⚠ No client companies found, using all companies")
        client_companies = core["companies"]

    # ========== QUOTES ==========
    quotes = []
    year = pendulum.now().year

    for i in range(count):
        company = random.choice(client_companies)
        # Obtener contactos de la empresa
        company_contacts = [c for c in core["contacts"] if c.company_id == company.id]
        contact = random.choice(company_contacts) if company_contacts else None

        quote = Quote(
            quote_number=f"Q-{year}-{i+1:04d}",
            subject=fake.catch_phrase(),
            revision=random.choice(["A", "B", "C"]),
            company_id=company.id,
            contact_id=contact.id if contact else None,
            branch_id=None,
            staff_id=random.choice(core["staff"]).id,
            status_id=random.choice(lookups["quote_statuses"]).id,
            quote_date=fake.date_between(start_date="-6M", end_date="today"),
            valid_until=fake.date_between(start_date="today", end_date="+3M"),
            shipping_date=fake.date_between(start_date="+1M", end_date="+6M"),
            incoterm_id=random.choice(lookups["incoterms"]).id,
            currency_id=random.choice(lookups["currencies"]).id,
            exchange_rate=Decimal(str(round(random.uniform(700, 950), 2))),
            subtotal=Decimal("0.00"),
            tax_percentage=Decimal("19.00"),
            tax_amount=Decimal("0.00"),
            total=Decimal("0.00"),
            notes=fake.text(max_nb_chars=200) if random.random() > 0.5 else None,
            internal_notes=fake.text(max_nb_chars=100) if random.random() > 0.7 else None,
            is_active=True,
        )
        session.add(quote)
        quotes.append(quote)

    session.flush()

    # ========== QUOTE PRODUCTS ==========
    quote_products = []
    for quote in quotes:
        num_products = random.randint(1, 5)
        quote_subtotal = Decimal("0.00")

        for sequence in range(1, num_products + 1):
            product = random.choice(core["products"])
            quantity = Decimal(str(random.randint(1, 20)))
            unit_price = product.sale_price or Decimal(str(round(random.uniform(50, 500), 2)))
            discount_percentage = Decimal(str(random.choice([0, 5, 10, 15])))

            # Calcular discount_amount y subtotal
            line_amount = quantity * unit_price
            discount_amount = line_amount * discount_percentage / 100
            line_subtotal = line_amount - discount_amount

            quote_product = QuoteProduct(
                quote_id=quote.id,
                product_id=product.id,
                sequence=sequence,
                quantity=quantity,
                unit_price=unit_price,
                discount_percentage=discount_percentage,
                discount_amount=discount_amount,
                subtotal=line_subtotal,
                notes=None,
            )
            session.add(quote_product)
            quote_products.append(quote_product)

            quote_subtotal += line_subtotal

        # Actualizar totales de cotización
        quote.subtotal = quote_subtotal
        quote.tax_amount = quote_subtotal * quote.tax_percentage / 100
        quote.total = quote_subtotal + quote.tax_amount

    session.flush()
    logger.success(f"  ✓ Created {len(quotes)} quotes with {len(quote_products)} quote products")

    # ========== PAYMENT CONDITIONS ==========
    # SKIP payment conditions - need to review model fields
    payment_conditions = []
    logger.success(f"  ✓ Skipped payment conditions (need model review)")

    session.commit()

    return {
        "quotes": quotes,
        "quote_products": quote_products,
        "payment_conditions": payment_conditions,
    }


def _calculate_rut_dv(rut: int) -> str:
    """
    Calcula el dígito verificador de un RUT chileno.

    Args:
        rut: Número de RUT sin dígito verificador

    Returns:
        Dígito verificador (0-9 o K)
    """
    suma = 0
    multiplo = 2

    while rut > 0:
        suma += (rut % 10) * multiplo
        rut //= 10
        multiplo += 1
        if multiplo == 8:
            multiplo = 2

    resto = suma % 11
    dv = 11 - resto

    if dv == 11:
        return "0"
    elif dv == 10:
        return "K"
    else:
        return str(dv)


def seed_all(
    session: Optional[Session] = None,
    database_url: str = "sqlite:///app_akgroup.db",
    count: int = 50,
) -> None:
    """
    Pobla toda la base de datos con datos ficticios.

    Args:
        session: Sesión de SQLAlchemy existente (opcional)
        database_url: URL de la base de datos (usado si no se provee session)
        count: Cantidad de registros a crear por modelo (default: 50)

    Example:
        >>> seed_all(count=100)
        ✓ Database seeded successfully with 100 records!
    """
    # Crear sesión si no se proveyó una
    close_session = False
    if session is None:
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        close_session = True

    try:
        logger.info("=" * 60)
        logger.info("🌱 SEEDING DATABASE WITH FAKE DATA")
        logger.info("=" * 60)

        # Fase 1: Lookups
        lookups = seed_lookups(session)

        # Fase 2: Core Models
        core = seed_core_models(session, lookups, count=count)

        # Fase 3: Business Models
        business = seed_business_models(session, lookups, core, count=min(count, 30))

        logger.info("=" * 60)
        logger.success(f"✅ DATABASE SEEDED SUCCESSFULLY!")
        logger.info(f"   Total companies: {len(core['companies'])}")
        logger.info(f"   Total products: {len(core['products'])}")
        logger.info(f"   Total quotes: {len(business['quotes'])}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Error seeding database: {e}")
        session.rollback()
        raise

    finally:
        if close_session:
            session.close()


def main() -> None:
    """Función principal para ejecutar el script desde CLI."""
    # Configurar argumentos
    database_url = "sqlite:///app_akgroup.db"
    count = 20  # Default: 20 registros para evitar demoras

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        # Si el argumento es un número, es el count
        if arg.isdigit():
            count = int(arg)
        else:
            database_url = arg

    if len(sys.argv) > 2:
        count = int(sys.argv[2])

    logger.info(f"Using database: {database_url}")
    logger.info(f"Creating {count} records per model")

    seed_all(database_url=database_url, count=count)


if __name__ == "__main__":
    main()
