"""
Tests para CompanyTypeEnum.

Verifica el funcionamiento del enum híbrido de tipos de empresa.
"""

import pytest

from src.models.core.companies import CompanyTypeEnum


class TestCompanyTypeEnum:
    """Tests para el CompanyTypeEnum."""

    def test_enum_values(self):
        """Test que los valores del enum son correctos."""
        assert CompanyTypeEnum.CLIENT.value == "CLIENT"
        assert CompanyTypeEnum.SUPPLIER.value == "SUPPLIER"

    def test_display_names(self):
        """Test que los display names son correctos."""
        assert CompanyTypeEnum.CLIENT.display_name == "Cliente"
        assert CompanyTypeEnum.SUPPLIER.display_name == "Proveedor"

    def test_descriptions(self):
        """Test que las descripciones existen."""
        assert len(CompanyTypeEnum.CLIENT.description) > 0
        assert len(CompanyTypeEnum.SUPPLIER.description) > 0
        assert "productos" in CompanyTypeEnum.CLIENT.description.lower()

    def test_enum_iteration(self):
        """Test que se puede iterar sobre el enum."""
        types = list(CompanyTypeEnum)
        assert len(types) == 2
        assert CompanyTypeEnum.CLIENT in types
        assert CompanyTypeEnum.SUPPLIER in types

    def test_enum_comparison(self):
        """Test que las comparaciones funcionan correctamente."""
        client = CompanyTypeEnum.CLIENT
        supplier = CompanyTypeEnum.SUPPLIER

        assert client == CompanyTypeEnum.CLIENT
        assert client != CompanyTypeEnum.SUPPLIER
        assert supplier == CompanyTypeEnum.SUPPLIER
        assert supplier != CompanyTypeEnum.CLIENT

    def test_enum_from_string(self):
        """Test que se puede crear enum desde string."""
        client = CompanyTypeEnum["CLIENT"]
        assert client == CompanyTypeEnum.CLIENT

        supplier = CompanyTypeEnum["SUPPLIER"]
        assert supplier == CompanyTypeEnum.SUPPLIER

    def test_enum_invalid_string(self):
        """Test que lanza error con string inválido."""
        with pytest.raises(KeyError):
            CompanyTypeEnum["INVALID"]

        with pytest.raises(KeyError):
            CompanyTypeEnum["cliente"]  # Case sensitive

    def test_enum_is_string(self):
        """Test que el enum es compatible con string."""
        assert isinstance(CompanyTypeEnum.CLIENT, str)
        assert CompanyTypeEnum.CLIENT == "CLIENT"

    def test_all_enums_have_display_names(self):
        """Test que todos los enums tienen display name."""
        for company_type in CompanyTypeEnum:
            display_name = company_type.display_name
            assert display_name is not None
            assert len(display_name) > 0
            assert display_name != company_type.value

    def test_all_enums_have_descriptions(self):
        """Test que todos los enums tienen descripción."""
        for company_type in CompanyTypeEnum:
            description = company_type.description
            assert description is not None
            assert len(description) > 0
