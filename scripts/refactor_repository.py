
import os

def replace_in_file(file_path, replacements):
    try:
        # Resolve absolute path if relative
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
            
        print(f"Processing {file_path}")
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        for old, new in replacements.items():
            new_content = new_content.replace(old, new)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {file_path}")
        else:
            print(f"No changes for {file_path}")
            
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

base_dir = r"c:\Users\raare\Documents\Personal\01Trabajo\AkGroup\App-AKGroup"

# 1. Update company_repository.py
repo_replacements = {
    "class BranchRepository(BaseRepository[Branch]):": "class PlantRepository(BaseRepository[Plant]):",
    "Repositorio para Branch (sucursales).": "Repositorio para Plant (plantas/sucursales).",
    "Maneja las sucursales de empresas.": "Maneja las plantas de empresas.",
    "repo = BranchRepository(session)": "repo = PlantRepository(session)",
    "branches = repo.get_by_company(company_id=1)": "plants = repo.get_by_company(company_id=1)",
    "super().__init__(session, Branch)": "super().__init__(session, Plant)",
    "def get_by_company(self, company_id: int) -> List[Branch]:": "def get_by_company(self, company_id: int) -> List[Plant]:",
    "Obtiene todas las sucursales de una empresa.": "Obtiene todas las plantas de una empresa.",
    "Lista de sucursales": "Lista de plantas",
    'logger.debug(f"Obteniendo sucursales de empresa id={company_id}")': 'logger.debug(f"Obteniendo plantas de empresa id={company_id}")',
    "branches = (": "plants = (",
    "self.session.query(Branch)": "self.session.query(Plant)",
    ".filter(Branch.company_id == company_id)": ".filter(Plant.company_id == company_id)",
    ".order_by(Branch.name)": ".order_by(Plant.name)",
    'logger.debug(f"Encontradas {len(branches)} sucursal(es)")': 'logger.debug(f"Encontradas {len(plants)} planta(s)")',
    "return branches": "return plants",
    "def get_active_branches(self, company_id: int) -> List[Branch]:": "def get_active_plants(self, company_id: int) -> List[Plant]:",
    "Obtiene solo las sucursales activas de una empresa.": "Obtiene solo las plantas activas de una empresa.",
    "Lista de sucursales activas": "Lista de plantas activas",
    'logger.debug(f"Obteniendo sucursales activas de empresa id={company_id}")': 'logger.debug(f"Obteniendo plantas activas de empresa id={company_id}")',
    "Branch.company_id == company_id,": "Plant.company_id == company_id,",
    "Branch.is_active == True": "Plant.is_active == True",
    'logger.debug(f"Encontradas {len(branches)} sucursal(es) activa(s)")': 'logger.debug(f"Encontradas {len(plants)} planta(s) activa(s)")',
    "def search_by_name(self, company_id: int, name: str) -> List[Branch]:": "def search_by_name(self, company_id: int, name: str) -> List[Plant]:",
    "Busca sucursales por nombre dentro de una empresa.": "Busca plantas por nombre dentro de una empresa.",
    "Lista de sucursales que coinciden": "Lista de plantas que coinciden",
    'logger.debug(f"Buscando sucursales de empresa id={company_id} por nombre: {name}")': 'logger.debug(f"Buscando plantas de empresa id={company_id} por nombre: {name}")',
    "Branch.name.ilike(search_pattern)": "Plant.name.ilike(search_pattern)",
}
replace_in_file(os.path.join(base_dir, "src/backend/repositories/core/company_repository.py"), repo_replacements)

# 2. Update orders.py
orders_replacements = {
    'branch_id = Column(': 'plant_id = Column(',
    'ForeignKey("branches.id", ondelete="SET NULL"),': 'ForeignKey("plants.id", ondelete="SET NULL"),',
    'comment="Company branch",': 'comment="Company plant",',
}
replace_in_file(os.path.join(base_dir, "src/backend/models/business/orders.py"), orders_replacements)

# 3. Update lookups.py
lookups_replacements = {
    'branches: Sucursales ubicadas en esta ciudad': 'plants: Plantas ubicadas en esta ciudad',
    'branches = relationship("Branch", back_populates="city", lazy="select")': 'plants = relationship("Plant", back_populates="city", lazy="select")',
}
replace_in_file(os.path.join(base_dir, "src/backend/models/lookups/lookups.py"), lookups_replacements)

# 4. Update invoices.py
invoices_replacements = {
    'branch_id: Foreign key to Branch': 'plant_id: Foreign key to Plant',
}
replace_in_file(os.path.join(base_dir, "src/backend/models/business/invoices.py"), invoices_replacements)

# 5. Update company_detail_view.py
view_replacements = {
    'ft.dropdown.Option("branch", t("companies.address_types.branch")),': 'ft.dropdown.Option("plant", t("companies.address_types.plant")),',
    'ft.dropdown.Option("branch", "Sucursal"),': 'ft.dropdown.Option("plant", "Planta"),',
}
replace_in_file(os.path.join(base_dir, "src/frontend/views/companies/company_detail_view.py"), view_replacements)

# 6. Update README.md
readme_replacements = {
    '- ✅ `core/companies.py` - Company, CompanyRut, Branch': '- ✅ `core/companies.py` - Company, CompanyRut, Plant',
    '5. **Branch** - Sucursales de empresas': '5. **Plant** - Sucursales/Plantas de empresas',
    '8. **Address** - Direcciones de empresas (con tipos: delivery, billing, headquarters, branch)': '8. **Address** - Direcciones de empresas (con tipos: delivery, billing, headquarters, plant)',
}
replace_in_file(os.path.join(base_dir, "src/backend/models/README.md"), readme_replacements)
