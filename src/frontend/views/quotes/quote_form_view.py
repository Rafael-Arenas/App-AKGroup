import flet as ft
from datetime import date
from typing import Optional, Callable, Any, Dict
from loguru import logger

from src.frontend.services.api import (
    lookup_api,
    quote_api,
    contact_api,
    company_rut_api,
    plant_api,
    staff_api
)
from src.shared.schemas.business.quote import QuoteCreate, QuoteUpdate

class QuoteFormDialog(ft.AlertDialog):
    def __init__(
        self,
        page: ft.Page,
        company_id: int,
        quote: Optional[Dict[str, Any]] = None,
        on_save: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
    ):
        self.page_ref = page
        self.company_id = company_id
        self.quote = quote
        self.is_editing = quote is not None
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel

        # State for dropdowns
        self.statuses = []
        self.incoterms = []
        self.currencies = []
        self.contacts = []
        self.ruts = []
        self.plants = []
        self.staff_members = []

        # Form fields
        self.quote_number = ft.TextField(
            label="Número de Cotización",
            value=quote.get("quote_number", "") if quote else "",
            capitalization=ft.TextCapitalization.CHARACTERS,
            col={"sm": 6},
        )
        self.revision = ft.TextField(
            label="Revisión",
            value=quote.get("revision", "A") if quote else "A",
            capitalization=ft.TextCapitalization.CHARACTERS,
            col={"sm": 6},
        )
        self.subject = ft.TextField(
            label="Asunto",
            value=quote.get("subject", "") if quote else "",
            col={"sm": 12},
        )
        self.status = ft.Dropdown(
            label="Estado",
            options=[],
            col={"sm": 6},
        )
        self.date_picker = ft.DatePicker(
            on_change=self._on_date_change,
        )
        self.quote_date_btn = ft.ElevatedButton(
            "Fecha: " + (quote.get("quote_date", date.today().isoformat()) if quote else date.today().isoformat()),
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: self.page_ref.open(self.date_picker),
            col={"sm": 6},
        )
        # Store date value separately
        self.selected_date = date.fromisoformat(quote.get("quote_date")) if quote and quote.get("quote_date") else date.today()
        
        self.valid_until_picker = ft.DatePicker(
            on_change=self._on_valid_until_change,
        )
        self.valid_until_btn = ft.ElevatedButton(
            "Válido hasta: " + (quote.get("valid_until", "") if quote else "Seleccionar"),
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: self.page_ref.open(self.valid_until_picker),
            col={"sm": 6},
        )
        self.selected_valid_until = date.fromisoformat(quote.get("valid_until")) if quote and quote.get("valid_until") else None

        self.shipping_date_picker = ft.DatePicker(
            on_change=self._on_shipping_date_change,
        )
        self.shipping_date_btn = ft.ElevatedButton(
            "Envío estimado: " + (quote.get("shipping_date", "") if quote else "Seleccionar"),
            icon=ft.Icons.LOCAL_SHIPPING,
            on_click=lambda _: self.page_ref.open(self.shipping_date_picker),
            col={"sm": 6},
        )
        self.selected_shipping_date = date.fromisoformat(quote.get("shipping_date")) if quote and quote.get("shipping_date") else None

        self.incoterm = ft.Dropdown(
            label="Incoterm",
            options=[],
            col={"sm": 6},
        )
        
        self.currency = ft.Dropdown(
            label="Moneda",
            options=[],
            col={"sm": 6},
        )
        
        self.exchange_rate = ft.TextField(
            label="Tipo de Cambio",
            value=str(quote.get("exchange_rate", "1.0")) if quote else "1.0",
            keyboard_type=ft.KeyboardType.NUMBER,
            col={"sm": 6},
        )

        self.unit = ft.TextField(
            label="Unidad",
            value=quote.get("unit", "") if quote else "",
            col={"sm": 6},
        )

        self.contact = ft.Dropdown(
            label="Contacto",
            options=[],
            col={"sm": 6},
        )
        
        self.rut = ft.Dropdown(
            label="RUT Facturación",
            options=[],
            col={"sm": 6},
        )
        
        self.plant = ft.Dropdown(
            label="Planta / Sucursal",
            options=[],
            col={"sm": 6},
        )
        
        self.staff = ft.Dropdown(
            label="Vendedor (Staff)",
            options=[],
            col={"sm": 6},
        )
        
        self.notes = ft.TextField(
            label="Notas",
            value=quote.get("notes", "") if quote else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
            col={"sm": 12},
        )

        super().__init__(
            title=ft.Text("Editar Cotización" if self.is_editing else "Nueva Cotización"),
            content=ft.Column(
                controls=[
                    ft.ProgressBar(visible=True) # Loading initially
                ],
                width=700,
                scroll=ft.ScrollMode.AUTO,
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self._cancel),
                ft.ElevatedButton("Guardar", on_click=self._save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )

    def did_mount(self):
        # Trigger data loading when added to page
        self.page_ref.run_task(self._load_data)

    def _on_date_change(self, e):
        if self.date_picker.value:
            self.selected_date = self.date_picker.value.date()
            self.quote_date_btn.text = f"Fecha: {self.selected_date.isoformat()}"
            self.quote_date_btn.update()

    def _on_valid_until_change(self, e):
        if self.valid_until_picker.value:
            self.selected_valid_until = self.valid_until_picker.value.date()
            self.valid_until_btn.text = f"Válido hasta: {self.selected_valid_until.isoformat()}"
            self.valid_until_btn.update()

    def _on_shipping_date_change(self, e):
        if self.shipping_date_picker.value:
            self.selected_shipping_date = self.shipping_date_picker.value.date()
            self.shipping_date_btn.text = f"Envío estimado: {self.selected_shipping_date.isoformat()}"
            self.shipping_date_btn.update()

    async def _load_data(self):
        try:
            # Parallel loading of lookups
            results = await getattr(self.page_ref, 'run_task_group', lambda tasks: tasks)(
                [
                    lookup_api.get_quote_statuses(),
                    lookup_api.get_incoterms(),
                    lookup_api.get_currencies(),
                    contact_api.get_by_company(self.company_id),
                    company_rut_api.get_by_company(self.company_id),
                    plant_api.get_by_company(self.company_id),
                    staff_api.get_active()
                ]
            ) if hasattr(self.page_ref, 'run_task_group') else [
                await lookup_api.get_quote_statuses(),
                await lookup_api.get_incoterms(),
                await lookup_api.get_currencies(),
                await contact_api.get_by_company(self.company_id),
                await company_rut_api.get_by_company(self.company_id),
                await plant_api.get_by_company(self.company_id),
                await staff_api.get_active()
            ]
            
            self.statuses = results[0]
            self.incoterms = results[1]
            self.currencies = results[2]
            self.contacts = results[3]
            self.ruts = results[4]
            self.plants = results[5]
            self.staff_members = results[6]

            # Populate Dropdowns
            self.status.options = [ft.dropdown.Option(str(s["id"]), s["name"]) for s in self.statuses]
            self.incoterm.options = [ft.dropdown.Option(str(i["id"]), f"{i['code']} - {i['name']}") for i in self.incoterms]
            self.currency.options = [ft.dropdown.Option(str(c["id"]), f"{c['code']} - {c['name']}") for c in self.currencies]
            
            self.contact.options = [ft.dropdown.Option(str(c["id"]), f"{c['first_name']} {c['last_name']}") for c in self.contacts]
            # Add "No Contact" option
            self.contact.options.insert(0, ft.dropdown.Option("", "Sin Contacto"))
            
            self.rut.options = [ft.dropdown.Option(str(r["id"]), r["rut"]) for r in self.ruts]
             # Add "No RUT" option? Maybe usually required but for now allow empty
            self.rut.options.insert(0, ft.dropdown.Option("", "Sin RUT Específico"))

            self.plant.options = [ft.dropdown.Option(str(p["id"]), p["name"]) for p in self.plants]
            self.plant.options.insert(0, ft.dropdown.Option("", "Sin Planta"))

            self.staff.options = [ft.dropdown.Option(str(s["id"]), f"{s['first_name']} {s['last_name']}") for s in self.staff_members]

            # Set initial values
            if self.quote:
                self.status.value = str(self.quote.get("status_id", ""))
                self.incoterm.value = str(self.quote.get("incoterm_id", "")) if self.quote.get("incoterm_id") else None
                self.currency.value = str(self.quote.get("currency_id", ""))
                self.contact.value = str(self.quote.get("contact_id", "")) if self.quote.get("contact_id") else None
                self.rut.value = str(self.quote.get("company_rut_id", "")) if self.quote.get("company_rut_id") else None
                self.plant.value = str(self.quote.get("plant_id", "")) if self.quote.get("plant_id") else None
                self.staff.value = str(self.quote.get("staff_id", ""))
            else:
                # Defaults for new quote
                # Default status: Draft (usually id 1, need to check or assume)
                if self.statuses:
                    self.status.value = str(self.statuses[0]["id"])
                # Default currency: USD or CLP (check logic later, take first for now)
                if self.currencies:
                    self.currency.value = str(self.currencies[0]["id"])
                
                # Auto-select main RUT
                main_rut = next((r for r in self.ruts if r.get("is_main")), None)
                if main_rut:
                    self.rut.value = str(main_rut["id"])
            
            # Rebuild content
            self.content = ft.ResponsiveRow(
                controls=[
                    self.quote_number,
                    self.revision,
                    self.subject,
                    self.status,
                    self.quote_date_btn,
                    self.valid_until_btn,
                    self.shipping_date_btn,
                    self.unit,
                    self.incoterm,
                    self.currency,
                    self.exchange_rate,
                    ft.Divider(),
                    self.contact,
                    self.rut,
                    self.plant,
                    self.staff,
                    self.notes,
                ],
            )
            self.update()

        except Exception as e:
            logger.error(f"Error loading form data: {e}")
            self.content = ft.Text(f"Error cargando datos: {str(e)}", color="red")
            self.update()

    async def _save(self, e):
        if not self.quote_number.value:
            self.quote_number.error_text = "Requerido"
            self.quote_number.update()
            return
        if not self.subject.value:
            self.subject.error_text = "Requerido"
            self.subject.update()
            return
        if not self.status.value:
            self.status.error_text = "Requerido"
            self.status.update()
            return
        if not self.staff.value:
            self.staff.error_text = "Requerido"
            self.staff.update()
            return

        try:
            data = {
                "quote_number": self.quote_number.value,
                "revision": self.revision.value,
                "subject": self.subject.value,
                "company_id": self.company_id,
                "status_id": int(self.status.value),
                "quote_date": self.selected_date.isoformat(),
                "valid_until": self.selected_valid_until.isoformat() if self.selected_valid_until else None,
                "shipping_date": self.selected_shipping_date.isoformat() if self.selected_shipping_date else None,
                "unit": self.unit.value,
                "incoterm_id": int(self.incoterm.value) if self.incoterm.value else None,
                "currency_id": int(self.currency.value) if self.currency.value else None,
                "exchange_rate": float(self.exchange_rate.value) if self.exchange_rate.value else None,
                "contact_id": int(self.contact.value) if self.contact.value else None,
                "company_rut_id": int(self.rut.value) if self.rut.value else None,
                "plant_id": int(self.plant.value) if self.plant.value else None,
                "staff_id": int(self.staff.value) if self.staff.value else None,
                "notes": self.notes.value,
            }

            if self.is_editing:
                await quote_api.update(self.quote["id"], data)
                self.page_ref.show_snack_bar(ft.SnackBar(content=ft.Text("Cotización actualizada")))
            else:
                await quote_api.create(data)
                self.page_ref.show_snack_bar(ft.SnackBar(content=ft.Text("Cotización creada")))

            if self.on_save_callback:
                self.on_save_callback()
            
            self.open = False
            self.page_ref.update()

        except Exception as ex:
            logger.error(f"Error saving quote: {ex}")
            self.page_ref.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="error"))

    async def _cancel(self, e):
        self.open = False
        self.page_ref.update()
        if self.on_cancel_callback:
            self.on_cancel_callback()
