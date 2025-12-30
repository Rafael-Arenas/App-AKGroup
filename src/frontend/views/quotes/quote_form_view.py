import flet as ft
import asyncio
from datetime import date, datetime
from typing import Optional, Callable, Any, Dict
from loguru import logger
from decimal import Decimal

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import BaseCard, LoadingSpinner, ErrorDisplay
from src.frontend.services.api import (
    lookup_api,
    quote_api,
    contact_api,
    CompanyAPI,
    company_rut_api,
    plant_api,
    staff_api
)
from src.frontend.components.forms import (
    ValidatedTextField,
    DropdownField
)
from src.frontend.i18n.translation_manager import t
from src.frontend.utils.fake_data_generator import FakeDataGenerator

class QuoteFormView(ft.Column):
    def __init__(
        self,
        company_id: int,
        quote_id: Optional[int] = None,
        on_save: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
    ):
        super().__init__()
        self.company_id = company_id
        self.quote_id = quote_id
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel

        self.is_editing = quote_id is not None
        self._quote: Optional[Dict[str, Any]] = None
        self._selected_currency_id: Optional[int] = None
        self._is_loading = True
        self._is_saving = False
        self._error_message = ""

        # Layout setup
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = LayoutConstants.SPACING_MD

        # Form Fields
        self._init_form_fields()

        # Fake data button (only for creation mode)
        self._fake_data_button = ft.IconButton(
            icon=ft.Icons.CASINO,
            tooltip=t("quotes.form.generate_fake_data") if self.is_editing else "Generar datos ficticios",
            on_click=self._on_generate_fake_data,
            visible=not self.is_editing,
            disabled=True,
        )

        # Build initial layout (loading state)
        self.controls = [self._build_loading()]

    def _init_form_fields(self):
        self.quote_number = ValidatedTextField(
            label=t("quotes.fields.quote_number"),
            required=True,
            validators=["required"],
            prefix_icon=ft.Icons.NUMBERS,
            read_only=True, # Always read-only
        )
        
        self.revision = ValidatedTextField(
            label=t("quotes.fields.revision"),
            required=True,
            validators=["required"],
            prefix_icon=ft.Icons.HISTORY,
            max_length=10,
        )

        self.subject = ValidatedTextField(
            label=t("quotes.fields.subject"),
            required=True,
            validators=["required"],
            prefix_icon=ft.Icons.SUBJECT,
        )

        self.status = DropdownField(
            label=t("quotes.columns.status"),
            required=True,
            prefix_icon=ft.Icons.FLAG,
        )

        # Date Fields (Native Flet implementation)
        self.quote_date_picker = ft.DatePicker(
            on_change=self._on_quote_date_change,
            on_dismiss=lambda _: None,
        )
        self.quote_date = ft.TextField(
            label=t("quotes.fields.quote_date"),
            read_only=True,
            suffix_icon=ft.Icons.CALENDAR_TODAY,
            on_click=self._open_quote_date_picker,
        )

        self.valid_until_picker = ft.DatePicker(
            on_change=self._on_valid_until_change,
            on_dismiss=lambda _: None,
        )
        self.valid_until = ft.TextField(
            label=t("quotes.fields.valid_until"),
            read_only=True,
            suffix_icon=ft.Icons.CALENDAR_TODAY,
            on_click=self._open_valid_until_picker,
        )

        self.shipping_date_picker = ft.DatePicker(
            on_change=self._on_shipping_date_change,
            on_dismiss=lambda _: None,
        )
        self.shipping_date = ft.TextField(
            label=t("quotes.fields.shipping_date"),
            read_only=True,
            suffix_icon=ft.Icons.CALENDAR_TODAY,
            on_click=self._open_shipping_date_picker,
        )

        self.unit = ValidatedTextField(
            label=t("quotes.fields.unit"),
            prefix_icon=ft.Icons.SQUARE_FOOT,
        )

        self.incoterm = DropdownField(
            label=t("quotes.fields.incoterm"),
            prefix_icon=ft.Icons.LOCAL_SHIPPING,
        )

        self.contact = DropdownField(
            label=t("quotes.fields.contact"),
            prefix_icon=ft.Icons.PERSON,
        )

        self.rut = DropdownField(
            label=t("quotes.fields.rut"),
            prefix_icon=ft.Icons.RECEIPT,
        )

        self.plant = DropdownField(
            label=t("quotes.fields.plant"),
            prefix_icon=ft.Icons.FACTORY,
        )

        self.staff = DropdownField(
            label=t("quotes.fields.staff"),
            required=True,
            prefix_icon=ft.Icons.BADGE,
        )

        self.notes = ValidatedTextField(
            label=t("quotes.fields.notes"),
            multiline=True,
            prefix_icon=ft.Icons.NOTE,
        )

    def did_mount(self):
        if self.page:
            self.page.overlay.extend([
                self.quote_date_picker,
                self.valid_until_picker,
                self.shipping_date_picker
            ])
            self.page.run_task(self._load_data)

    # Date Picker Handlers
    def _open_quote_date_picker(self, e):
        self.quote_date_picker.open = True
        self.page.update()
        
    def _open_valid_until_picker(self, e):
        self.valid_until_picker.open = True
        self.page.update()
        
    def _open_shipping_date_picker(self, e):
        self.shipping_date_picker.open = True
        self.page.update()

    def _format_date_for_display(self, dt_value) -> str:
        if not dt_value:
            return ""
        # Handle string input if any
        if isinstance(dt_value, str):
            try:
                # Try parsing YYYY-MM-DD
                dt_value = datetime.strptime(dt_value, "%Y-%m-%d").date()
            except ValueError:
                return dt_value # Return as is if format unknown

        return f"{dt_value.day:02d}/{dt_value.month:02d}/{dt_value.year}"

    def _on_quote_date_change(self, e):
        if self.quote_date_picker.value:
            self.quote_date.value = self._format_date_for_display(self.quote_date_picker.value)
            self.quote_date.error_text = None
            self.update()

    def _on_valid_until_change(self, e):
        if self.valid_until_picker.value:
            self.valid_until.value = self._format_date_for_display(self.valid_until_picker.value)
            self.update()

    def _on_shipping_date_change(self, e):
        if self.shipping_date_picker.value:
            self.shipping_date.value = self._format_date_for_display(self.shipping_date_picker.value)
            self.update()

    def _set_date_value(self, text_field: ft.TextField, date_picker: ft.DatePicker, value: Any):
        if not value:
            text_field.value = ""
            date_picker.value = None
            return

        dt_val = None
        if isinstance(value, str):
            try:
                # Handle YYYY-MM-DD from API
                dt_val = datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                pass
        elif isinstance(value, (date, datetime)):
            dt_val = value

        if dt_val:
            # ft.DatePicker expects datetime
            if isinstance(dt_val, date) and not isinstance(dt_val, datetime):
                dt_val = datetime.combine(dt_val, datetime.min.time())
            
            date_picker.value = dt_val
            text_field.value = self._format_date_for_display(dt_val)

    def _get_api_date_string(self, text_value: str) -> Optional[str]:
        if not text_value:
            return None
        try:
            # Expecting DD/MM/YYYY from display
            dt = datetime.strptime(text_value, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    def _build_loading(self) -> ft.Control:
        return ft.Container(
            content=LoadingSpinner(message=t("common.loading")),
            alignment=ft.alignment.center,
            expand=True
        )

    def _build_error(self) -> ft.Control:
        return ft.Container(
            content=ErrorDisplay(
                message=self._error_message,
                on_retry=self._load_data
            ),
            alignment=ft.alignment.center,
            expand=True
        )

    def _build_content(self) -> list[ft.Control]:
        title_text = t("quotes.form.edit_title") if self.is_editing else t("quotes.form.create_title")
        
        # Header
        header_controls = [
            ft.Icon(ft.Icons.EDIT if self.is_editing else ft.Icons.ADD_CIRCLE_OUTLINE, size=32),
            ft.Text(
            title_text,
            size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
            weight=ft.FontWeight.BOLD,
            ),
            ft.Container(expand=True),
        ]
        if self._fake_data_button.visible:
            header_controls.append(self._fake_data_button)

        header = ft.Container(
            content=ft.Row(
                controls=header_controls,
                spacing=LayoutConstants.SPACING_SM,
            ),
            padding=LayoutConstants.PADDING_MD,
        )

        # Action Buttons
        save_btn = ft.ElevatedButton(
            text=t("common.save"),
            icon=ft.Icons.SAVE,
            on_click=self._save,
            disabled=self._is_saving
        )
        
        cancel_btn = ft.ElevatedButton(
            text=t("common.cancel"),
            on_click=self._cancel,
            disabled=self._is_saving
        )

        # General Info Card
        general_card = BaseCard(
            title=t("quotes.sections.general_info"),
            icon=ft.Icons.INFO_OUTLINE,
            content=ft.Column([
                ft.ResponsiveRow([
                    ft.Column([self.quote_number], col={"sm": 6}),
                    ft.Column([self.revision], col={"sm": 6}),
                ]),
                ft.ResponsiveRow([
                    ft.Column([self.subject], col={"sm": 12}),
                ]),
                ft.ResponsiveRow([
                    ft.Column([self.status], col={"sm": 6}),
                    ft.Column([self.quote_date], col={"sm": 6}),
                ]),
            ])
        )

        # Commercial & Dates Card
        commercial_card = BaseCard(
            title=t("quotes.sections.commercial_details"),
            icon=ft.Icons.ATTACH_MONEY,
            content=ft.Column([
                ft.ResponsiveRow([
                    ft.Column([self.incoterm], col={"sm": 6}),
                    ft.Column([self.unit], col={"sm": 6}),
                ]),
                ft.Divider(),
                ft.ResponsiveRow([
                    ft.Column([self.valid_until], col={"sm": 6}),
                    ft.Column([self.shipping_date], col={"sm": 6}),
                ]),
            ])
        )

        # Relations Card
        relations_card = BaseCard(
            title=t("quotes.sections.relations"),
            icon=ft.Icons.PEOPLE_OUTLINE,
            content=ft.Column([
                ft.ResponsiveRow([
                    ft.Column([self.contact], col={"sm": 6}),
                    ft.Column([self.staff], col={"sm": 6}),
                ]),
                ft.ResponsiveRow([
                    ft.Column([self.rut], col={"sm": 6}),
                    ft.Column([self.plant], col={"sm": 6}),
                ]),
            ])
        )
        
        # Notes Card
        notes_card = BaseCard(
            title=t("quotes.sections.additional_notes"),
            icon=ft.Icons.NOTE,
            content=ft.Column([
                self.notes
            ])
        )

        return [
            header,
            ft.Divider(height=1, opacity=0.2),
            ft.Container(
                content=ft.Column([
                    general_card,
                    commercial_card,
                    relations_card,
                    notes_card,
                    ft.Row([save_btn, cancel_btn], alignment=ft.MainAxisAlignment.END)
                ], spacing=LayoutConstants.SPACING_LG),
                padding=LayoutConstants.PADDING_LG,
                expand=True
            )
        ]

    async def _load_data(self):
        self._is_loading = True
        self.controls = [self._build_loading()]
        if self.page: self.update()

        try:
            try:
                company_api = CompanyAPI()
                company = await company_api.get_by_id(self.company_id)
                company_name = (company or {}).get("name")
                if company_name:
                    dashboard_route_prefix = f"/companies/dashboard/{self.company_id}/"
                    updated_path: list[dict[str, str | None]] = []
                    for item in app_state.navigation.breadcrumb_path:
                        route = item.get("route")
                        if (
                            isinstance(route, str)
                            and route.startswith(dashboard_route_prefix)
                            and route.count("/") == 4
                        ):
                            updated_path.append({"label": str(company_name), "route": route})
                        else:
                            updated_path.append(item)
                    app_state.navigation.set_breadcrumb(updated_path)
            except Exception as e:
                logger.warning(f"Could not update breadcrumb company name: {e}")

            # Load Quote if editing
            if self.is_editing and self.quote_id:
                self._quote = await quote_api.get_by_id(self.quote_id)

            # Parallel loading of lookups
            results = await asyncio.gather(
                lookup_api.get_quote_statuses(),
                lookup_api.get_incoterms(),
                lookup_api.get_currencies(),
                contact_api.get_by_company(self.company_id),
                company_rut_api.get_by_company(self.company_id),
                plant_api.get_by_company(self.company_id),
                staff_api.get_active()
            )

            statuses, incoterms, currencies, contacts, ruts, plants, staff_members = results

            # Populate Dropdowns
            self.status.set_options([
                {"value": str(s["id"]), "label": s["name"]} 
                for s in statuses
            ])
            
            self.incoterm.set_options([
                {"value": str(i["id"]), "label": f"{i['code']} - {i['name']}"} 
                for i in incoterms
            ])

            # Set default currency (first available or from quote)
            if self._quote and self._quote.get("currency_id"):
                self._selected_currency_id = self._quote.get("currency_id")
            elif currencies:
                self._selected_currency_id = currencies[0]["id"]

            contact_opts = [{"value": str(c["id"]), "label": f"{c['first_name']} {c['last_name']}"} for c in contacts]
            contact_opts.insert(0, {"value": "", "label": t("quotes.form.no_contact")})
            self.contact.set_options(contact_opts)
            
            rut_opts = [{"value": str(r["id"]), "label": r["rut"]} for r in ruts]
            rut_opts.insert(0, {"value": "", "label": t("quotes.form.no_rut")})
            self.rut.set_options(rut_opts)

            plant_opts = [{"value": str(p["id"]), "label": p["name"]} for p in plants]
            plant_opts.insert(0, {"value": "", "label": t("quotes.form.no_plant")})
            self.plant.set_options(plant_opts)

            self.staff.set_options([
                {"value": str(s["id"]), "label": f"{s['first_name']} {s['last_name']}"} 
                for s in staff_members
            ])

            # Set Values
            if self._quote:
                self.quote_number.set_value(self._quote.get("quote_number", ""))
                self.revision.set_value(self._quote.get("revision", "A"))
                self.subject.set_value(self._quote.get("subject", ""))
                self.unit.set_value(self._quote.get("unit", ""))
                self.notes.set_value(self._quote.get("notes", ""))

                # Date fields
                self._set_date_value(self.quote_date, self.quote_date_picker, self._quote.get("quote_date"))
                if not self.quote_date.value:
                    self._set_date_value(self.quote_date, self.quote_date_picker, date.today())

                self._set_date_value(self.valid_until, self.valid_until_picker, self._quote.get("valid_until"))
                self._set_date_value(self.shipping_date, self.shipping_date_picker, self._quote.get("shipping_date"))

                # Dropdowns
                if self._quote.get("status_id"):
                    self.status.set_value(str(self._quote.get("status_id")))
                
                if self._quote.get("incoterm_id"):
                    self.incoterm.set_value(str(self._quote.get("incoterm_id")))
                
                if self._quote.get("contact_id"):
                    self.contact.set_value(str(self._quote.get("contact_id")))
                
                if self._quote.get("company_rut_id"):
                    self.rut.set_value(str(self._quote.get("company_rut_id")))
                
                if self._quote.get("plant_id"):
                    self.plant.set_value(str(self._quote.get("plant_id")))
                
                if self._quote.get("staff_id"):
                    self.staff.set_value(str(self._quote.get("staff_id")))

            else:
                # Defaults for New Quote
                self.quote_number.set_value("[ ASIGNACIÓN AUTOMÁTICA ]")
                self.revision.set_value("A")

                self._set_date_value(self.quote_date, self.quote_date_picker, date.today())
                
                if statuses:
                    self.status.set_value(str(statuses[0]["id"]))
                
                if currencies:
                    # Currency already handled above in self._selected_currency_id
                    pass

                main_rut = next((r for r in ruts if r.get("is_main")), None)
                if main_rut:
                    self.rut.set_value(str(main_rut["id"]))

            self._is_loading = False
            self.controls = self._build_content()
            if self._fake_data_button and not self.is_editing:
                self._fake_data_button.disabled = False
            if self.page: self.update()

        except Exception as e:
            logger.error(f"Error loading quote form data: {e}")
            self._error_message = str(e)
            self.controls = [self._build_error()]
            if self._fake_data_button:
                self._fake_data_button.disabled = True
            if self.page: self.update()

    def _validate(self) -> bool:
        is_valid = True
        if not self.quote_number.validate(): is_valid = False
        if not self.revision.validate(): is_valid = False
        if not self.subject.validate(): is_valid = False
        if not self.status.validate(): is_valid = False
        
        if not self.quote_date.value:
            self.quote_date.error_text = t("common.required_field")
            self.quote_date.update()
            is_valid = False
        else:
            self.quote_date.error_text = None
            self.quote_date.update()
            
        if not self.staff.validate(): is_valid = False
        return is_valid

    async def _save(self, e):
        if not self._validate():
            return

        self._is_saving = True
        # Could show saving indicator here, but button disabled is decent start
        if self.page: self.update()

        try:
            # Prepare data
            qn_value = self.quote_number.get_value()
            if qn_value == "[ ASIGNACIÓN AUTOMÁTICA ]":
                qn_value = "STRING"
                
            data = {
                "quote_number": qn_value,
                "revision": self.revision.get_value(),
                "subject": self.subject.get_value(),
                "company_id": self.company_id,
                "status_id": int(self.status.get_value()),
                "quote_date": self._get_api_date_string(self.quote_date.value),
                "valid_until": self._get_api_date_string(self.valid_until.value),
                "shipping_date": self._get_api_date_string(self.shipping_date.value),
                "unit": self.unit.get_value() or None,
                "incoterm_id": int(self.incoterm.get_value()) if self.incoterm.get_value() else None,
                "currency_id": int(self._selected_currency_id) if self._selected_currency_id else 1,
                "exchange_rate": 1.0,
                "contact_id": int(self.contact.get_value()) if self.contact.get_value() and self.contact.get_value() != "" else None,
                "company_rut_id": int(self.rut.get_value()) if self.rut.get_value() else None,
                "plant_id": int(self.plant.get_value()) if self.plant.get_value() else None,
                "staff_id": int(self.staff.get_value()),
                "notes": self.notes.get_value(),
            }

            if self.is_editing and self.quote_id:
                await quote_api.update(self.quote_id, data)
                if self.page:
                    self.page.overlay.append(ft.SnackBar(content=ft.Text(t("quotes.messages.updated")), bgcolor=ft.Colors.GREEN))
                    self.page.overlay[-1].open = True
                    self.page.update()
            else:
                result = await quote_api.create(data)
                assigned_number = result.get("quote_number", "")
                if self.page:
                    # Show the actual assigned number in the success message
                    success_msg = f"Cotización {assigned_number} creada exitosamente"
                    self.page.overlay.append(ft.SnackBar(content=ft.Text(success_msg), bgcolor=ft.Colors.GREEN))
                    self.page.overlay[-1].open = True
                    self.page.update()


            if self.on_save_callback:
                self.on_save_callback()

        except Exception as ex:
            logger.error(f"Error saving quote: {ex}")
            if self.page:
                self.page.overlay.append(ft.SnackBar(content=ft.Text(t("quotes.messages.error_saving", {"error": str(ex)})), bgcolor=ft.Colors.ERROR))
                self.page.overlay[-1].open = True
                self.page.update()
        finally:
            self._is_saving = False
            if self.page: self.update()

    async def _cancel(self, e):
        if self.on_cancel_callback:
            self.on_cancel_callback()

    def _on_generate_fake_data(self, e):
        """Llena el formulario con datos ficticios para agilizar pruebas."""
        if self._is_loading or self.is_editing:
            return

        try:
            FakeDataGenerator.populate_quote_form(self)
            self._fake_data_button.disabled = True
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(t("quotes.form.fake_data_success")),
                    bgcolor=ft.Colors.GREEN,
                    duration=2000,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()
        except Exception as ex:
            logger.exception(f"Error generating fake quote data: {ex}")
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(t("quotes.form.fake_data_error", {"error": str(ex)})),
                    bgcolor=ft.Colors.RED,
                    duration=3000,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()
