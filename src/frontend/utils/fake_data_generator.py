"""
Utilidad para generar datos ficticios aleatorios para los formularios.

Esta clase proporciona métodos para generar datos realistas para pruebas
y desarrollo en las vistas de creación del frontend.
"""
import random
import string
from typing import Dict, Any, List
from loguru import logger


class FakeDataGenerator:
    """Generador de datos ficticios para formularios."""

    # Listas de datos para generar valores realistas
    SPANISH_NAMES = [
        "García", "Rodríguez", "López", "Martínez", "Sánchez", "Pérez", "Gómez", 
        "Martín", "Jiménez", "Fernández", "Moreno", "Muñoz", "Álvarez", "Díaz",
        "Hernández", "Castro", "Flores", "Vargas", "Mendoza", "Cruz"
    ]
    
    SPANISH_ADJECTIVES = [
        "Digital", "Innovador", "Global", "Moderno", "Eficiente", "Rápido", 
        "Inteligente", "Profesional", "Calidad", "Premium", "Tecnológico",
        "Avanzado", "Integral", "Sostenible", "Ecológico", "Seguro"
    ]
    
    BUSINESS_TYPES = [
        "Soluciones", "Servicios", "Tecnología", "Consultoría", "Distribuidora",
        "Industrial", "Comercial", "Exportaciones", "Importaciones", "Logística"
    ]
    
    PRODUCT_NAMES = [
        "Componente", "Pieza", "Elemento", "Artículo", "Producto", "Material",
        "Dispositivo", "Mecanismo", "Estructura", "Soporte", "Conector",
        "Accesorio", "Herramienta", "Equipo", "Sistema"
    ]
    
    PRODUCT_ADJECTIVES = [
        "Estándar", "Premium", "Básico", "Avanzado", "Profesional", "Industrial",
        "Doméstico", "Comercial", "Técnico", "Especializado", "Universal",
        "Personalizado", "Adaptable", "Modular", "Compacto"
    ]
    
    MATERIALS = [
        "Acero", "Aluminio", "Plástico", "Hierro", "Cobre", "Titanio",
        "Madera", "Vidrio", "Cerámica", "Goma", "Silicona", "Fibra"
    ]
    
    COUNTRIES = ["CL", "AR", "ES", "MX", "PE", "CO"]
    
    CHILEAN_CITIES = [
        "Santiago", "Valparaíso", "Concepción", "La Serena", "Antofagasta",
        "Temuco", "Rancagua", "Talca", "Arica", "Chillán", "Iquique", "Puerto Montt"
    ]

    @classmethod
    def generate_company_data(cls, company_type: str = "CLIENT") -> Dict[str, Any]:
        """
        Genera datos ficticios para una empresa.
        
        Args:
            company_type: "CLIENT" o "SUPPLIER"
            
        Returns:
            Diccionario con los datos generados
        """
        logger.debug(f"Generating fake {company_type} data")
        
        # Generar nombre de empresa
        name_parts = [
            random.choice(cls.BUSINESS_TYPES),
            random.choice(cls.SPANISH_NAMES),
            random.choice(["& CIA", "S.A.", "Ltda.", "S.L.", ""])
        ]
        name = " ".join([part for part in name_parts if part])
        
        # Generar trigram (3 letras mayúsculas)
        trigram = ''.join(random.choices(string.ascii_uppercase, k=3))
        
        # Generar teléfono (formato chileno)
        phone = f"+56 9 {random.randint(10000000, 99999999)}"
        
        # Generar website
        website_name = name.lower().replace(" ", "").replace("&", "").replace(".", "")
        website = f"https://www.{website_name[:15]}.cl"
        
        # Generar número intracomunitario (formato europeo)
        intracommunity = f"ES{random.randint(100000000, 999999999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
        
        return {
            "name": name,
            "trigram": trigram,
            "phone": phone,
            "website": website,
            "intracommunity_number": intracommunity,
            "country": random.choice(cls.COUNTRIES),
            "city": random.choice(cls.CHILEAN_CITIES),
            "is_active": True
        }
    
    @classmethod
    def generate_article_data(cls) -> Dict[str, Any]:
        """
        Genera datos ficticios para un artículo.
        
        Returns:
            Diccionario con los datos generados
        """
        logger.debug("Generating fake article data")
        
        # Generar código de referencia
        prefix = random.choice(["ART", "PROD", "COMP", "REF"])
        number = random.randint(10000, 99999)
        reference = f"{prefix}-{number}"
        
        # Generar designación en español
        product = random.choice(cls.PRODUCT_NAMES)
        adjective = random.choice(cls.PRODUCT_ADJECTIVES)
        material = random.choice(cls.MATERIALS)
        designation_es = f"{product} {adjective} {material}"
        
        # Generar designación en inglés e inglés
        designation_en = f"{adjective} {product} {material}"
        designation_fr = f"{product} {adjective} {material}"
        
        # Generar descripción corta
        description = f"Artículo de alta calidad para uso {adjective.lower()}. Fabricado con {material.lower()} de primera."
        
        # Generar precios
        base_price = random.uniform(10, 1000)
        cost_price = round(base_price * 0.7, 2)
        sale_price = round(base_price, 2)
        purchase_price = round(base_price * 0.8, 2)
        sale_price_eur = round(base_price * 0.85, 2)
        
        # Generar stock
        stock_quantity = round(random.uniform(0, 1000), 3)
        min_stock = round(random.uniform(0, 100), 3)
        
        # Generar dimensiones (en mm)
        length = round(random.uniform(10, 2000), 1)
        width = round(random.uniform(10, 1000), 1)
        height = round(random.uniform(10, 500), 1)
        volume = round((length * width * height) / 1000000000, 3)  # Convertir a m³
        
        # Generar peso (en kg)
        net_weight = round(random.uniform(0.1, 100), 2)
        gross_weight = round(net_weight * random.uniform(1.1, 1.3), 2)
        
        # Generar ubicación de stock
        stock_location = f"Bodega {random.choice(['A', 'B', 'C'])}-Estantería {random.randint(1, 20)}-{random.randint(1, 5)}"
        
        # Generar referencias
        supplier_reference = f"SUP-{random.randint(100000, 999999)}"
        customs_number = f"{random.randint(100000000, 999999999)}-{random.randint(1, 9)}"
        
        # Generar URLs
        image_url = f"https://picsum.photos/seed/{reference}/400/300.jpg"
        plan_url = f"https://example.com/plans/{reference}.pdf"
        
        # Generar revisión
        revision = f"v{random.randint(1, 5)}.{random.randint(0, 9)}"
        
        # Generar notas
        notes = f"Notas del artículo {reference}. Revisar especificaciones técnicas antes de uso."
        
        return {
            "reference": reference,
            "designation_es": designation_es,
            "designation_en": designation_en,
            "designation_fr": designation_fr,
            "description": description,
            "cost_price": str(cost_price),
            "sale_price": str(sale_price),
            "purchase_price": str(purchase_price),
            "sale_price_eur": str(sale_price_eur),
            "stock_quantity": str(stock_quantity),
            "min_stock": str(min_stock),
            "stock_location": stock_location,
            "length": str(length),
            "width": str(width),
            "height": str(height),
            "volume": str(volume),
            "net_weight": str(net_weight),
            "gross_weight": str(gross_weight),
            "country_of_origin": random.choice(cls.COUNTRIES),
            "supplier_reference": supplier_reference,
            "customs_number": customs_number,
            "image_url": image_url,
            "plan_url": plan_url,
            "revision": revision,
            "notes": notes,
            "is_active": True
        }
    
    @classmethod
    def generate_nomenclature_data(cls) -> Dict[str, Any]:
        """
        Genera datos ficticios para una nomenclatura.
        
        Returns:
            Diccionario con los datos generados
        """
        logger.debug("Generating fake nomenclature data")
        
        # Generar código de referencia
        prefix = random.choice(["NOM", "BOM", "ASM", "KIT"])
        number = random.randint(10000, 99999)
        reference = f"{prefix}-{number}"
        
        # Generar designación
        base_product = random.choice(cls.PRODUCT_NAMES)
        adjective = random.choice(cls.PRODUCT_ADJECTIVES)
        designation_es = f"Nomenclatura {base_product} {adjective}"
        designation_en = f"{adjective} {base_product} Nomenclature"
        designation_fr = f"Nomenclature {base_product} {adjective}"
        
        # Generar precios
        base_price = random.uniform(50, 2000)
        purchase_price = round(base_price * 0.75, 2)
        cost_price = round(base_price * 0.8, 2)
        sale_price = round(base_price, 2)
        sale_price_eur = round(base_price * 0.85, 2)
        
        # Generar dimensiones (en mm)
        length = round(random.uniform(100, 3000), 1)
        width = round(random.uniform(100, 2000), 1)
        height = round(random.uniform(100, 1000), 1)
        volume = round((length * width * height) / 1000000000, 3)  # Convertir a m³
        
        # Generar peso (en kg)
        net_weight = round(random.uniform(1, 500), 2)
        gross_weight = round(net_weight * random.uniform(1.1, 1.3), 2)
        
        # Generar stock
        stock_quantity = round(random.uniform(0, 100), 3)
        minimum_stock = round(random.uniform(0, 10), 3)
        
        # Generar URLs
        image_url = f"https://picsum.photos/seed/{reference}/600/400.jpg"
        plan_url = f"https://example.com/nomenclatures/{reference}.pdf"
        
        # Generar revisión
        revision = f"R{random.randint(1, 9)}"
        
        return {
            "revision": revision,
            "reference": reference,
            "designation_es": designation_es,
            "designation_en": designation_en,
            "designation_fr": designation_fr,
            "purchase_price": str(purchase_price),
            "cost_price": str(cost_price),
            "sale_price": str(sale_price),
            "sale_price_eur": str(sale_price_eur),
            "length": str(length),
            "width": str(width),
            "height": str(height),
            "volume": str(volume),
            "net_weight": str(net_weight),
            "gross_weight": str(gross_weight),
            "stock_quantity": str(stock_quantity),
            "minimum_stock": str(minimum_stock),
            "image_url": image_url,
            "plan_url": plan_url,
            "is_active": True
        }
    
    @classmethod
    def populate_company_form(cls, form_view, company_type: str = "CLIENT") -> None:
        """
        Pobla un formulario de empresa con datos ficticios.
        
        Args:
            form_view: Instancia de CompanyFormView
            company_type: "CLIENT" o "SUPPLIER"
        """
        try:
            data = cls.generate_company_data(company_type)
            
            # Poblar campos básicos
            form_view._name_field.set_value(data["name"])
            form_view._trigram_field.set_value(data["trigram"])
            
            # Poblar contacto
            form_view._phone_field.set_value(data["phone"])
            form_view._website_field.set_value(data["website"])
            form_view._intracommunity_number_field.set_value(data["intracommunity_number"])
            
            # Poblar ubicación (si los lookups están cargados)
            if hasattr(form_view, '_countries') and form_view._countries:
                # Buscar país por nombre
                country = next((c for c in form_view._countries if c["name"] == data["country"]), None)
                if country:
                    form_view._country_field.set_value(str(country["id"]))
                    # Filtrar ciudades
                    form_view._on_country_change(str(country["id"]))
                    
                    # Buscar ciudad
                    if hasattr(form_view, '_cities') and form_view._cities:
                        city = next((c for c in form_view._cities if c["name"] == data["city"]), None)
                        if city:
                            form_view._city_field.set_value(str(city["id"]))
            
            # Mantener el estado activo
            form_view._is_active_switch.value = data["is_active"]
            
            logger.success(f"Company form populated with fake data: {data['name']}")
            
        except Exception as e:
            logger.exception(f"Error populating company form: {e}")
    
    @classmethod
    def populate_article_form(cls, form_view) -> None:
        """
        Pobla un formulario de artículo con datos ficticios.
        
        Args:
            form_view: Instancia de ArticleFormView
        """
        try:
            data = cls.generate_article_data()
            
            # Poblar campos básicos
            form_view._code_field.set_value(data["reference"])
            form_view._name_field.set_value(data["designation_es"])
            form_view._description_field.set_value(data["description"])
            
            # Poblar precios
            form_view._cost_price_field.set_value(data["cost_price"])
            form_view._sale_price_field.set_value(data["sale_price"])
            form_view._purchase_price_field.set_value(data["purchase_price"])
            form_view._sale_price_eur_field.set_value(data["sale_price_eur"])
            
            # Poblar stock
            form_view._stock_quantity_field.set_value(data["stock_quantity"])
            form_view._min_stock_field.set_value(data["min_stock"])
            form_view._stock_location_field.set_value(data["stock_location"])
            
            # Poblar dimensiones
            form_view._length_field.set_value(data["length"])
            form_view._width_field.set_value(data["width"])
            form_view._height_field.set_value(data["height"])
            form_view._volume_field.set_value(data["volume"])
            
            # Poblar peso
            form_view._net_weight_field.set_value(data["net_weight"])
            form_view._gross_weight_field.set_value(data["gross_weight"])
            
            # Poblar logística y aduanas
            form_view._country_of_origin_field.set_value(data["country_of_origin"])
            form_view._supplier_reference_field.set_value(data["supplier_reference"])
            form_view._customs_number_field.set_value(data["customs_number"])
            
            # Poblar recursos (URLs)
            if hasattr(form_view, '_image_url_field'):
                form_view._image_url_field.set_value(data["image_url"])
            if hasattr(form_view, '_plan_url_field'):
                form_view._plan_url_field.set_value(data["plan_url"])
            
            # Poblar campos adicionales
            form_view._designation_fr_field.set_value(data["designation_fr"])
            form_view._designation_en_field.set_value(data["designation_en"])
            form_view._revision_field.set_value(data["revision"])
            form_view._notes_field.set_value(data["notes"])
            
            # Mantener el estado activo
            form_view._is_active_switch.value = data["is_active"]
            
            logger.success(f"Article form populated with fake data: {data['reference']}")
            
        except Exception as e:
            logger.exception(f"Error populating article form: {e}")
    
    @classmethod
    def populate_nomenclature_form(cls, form_view) -> None:
        """
        Pobla un formulario de nomenclatura con datos ficticios.
        
        Args:
            form_view: Instancia de NomenclatureFormView
        """
        try:
            data = cls.generate_nomenclature_data()
            
            # Poblar campos básicos
            form_view._revision_field.set_value(data["revision"])
            form_view._reference_field.set_value(data["reference"])
            form_view._designation_es_field.set_value(data["designation_es"])
            form_view._designation_en_field.set_value(data["designation_en"])
            form_view._designation_fr_field.set_value(data["designation_fr"])
            
            # Poblar precios
            form_view._purchase_price_field.set_value(data["purchase_price"])
            form_view._cost_price_field.set_value(data["cost_price"])
            form_view._sale_price_field.set_value(data["sale_price"])
            form_view._sale_price_eur_field.set_value(data["sale_price_eur"])
            
            # Poblar dimensiones
            form_view._length_field.set_value(data["length"])
            form_view._width_field.set_value(data["width"])
            form_view._height_field.set_value(data["height"])
            form_view._volume_field.set_value(data["volume"])
            
            # Poblar peso
            form_view._net_weight_field.set_value(data["net_weight"])
            form_view._gross_weight_field.set_value(data["gross_weight"])
            
            # Poblar stock
            form_view._stock_quantity_field.set_value(data["stock_quantity"])
            form_view._minimum_stock_field.set_value(data["minimum_stock"])
            
            # Poblar URLs
            form_view._image_url_field.set_value(data["image_url"])
            form_view._plan_url_field.set_value(data["plan_url"])
            
            # Mantener el estado activo
            form_view._is_active_switch.value = data["is_active"]
            
            logger.success(f"Nomenclature form populated with fake data: {data['reference']}")
            
        except Exception as e:
            logger.exception(f"Error populating nomenclature form: {e}")
