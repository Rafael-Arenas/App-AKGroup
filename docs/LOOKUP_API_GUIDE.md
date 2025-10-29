# Lookup API Quick Reference Guide

## Base URL
```
http://localhost:8000/api/v1/lookups
```

## Authentication
Currently using mock user_id=1. Real authentication to be implemented.

---

## 1. Countries API

### Endpoints
```
GET    /api/v1/lookups/countries           # List all countries
GET    /api/v1/lookups/countries/{id}      # Get country by ID
POST   /api/v1/lookups/countries           # Create country
PUT    /api/v1/lookups/countries/{id}      # Update country
DELETE /api/v1/lookups/countries/{id}      # Delete country
```

### Examples
```bash
# Create Country
curl -X POST http://localhost:8000/api/v1/lookups/countries \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Colombia",
    "iso_code_alpha2": "CO",
    "iso_code_alpha3": "COL"
  }'

# List Countries (paginated)
curl http://localhost:8000/api/v1/lookups/countries?skip=0&limit=50

# Get Country by ID
curl http://localhost:8000/api/v1/lookups/countries/1

# Update Country
curl -X PUT http://localhost:8000/api/v1/lookups/countries/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "República de Colombia"
  }'

# Delete Country
curl -X DELETE http://localhost:8000/api/v1/lookups/countries/1
```

---

## 2. Cities API

### Endpoints
```
GET    /api/v1/lookups/cities                # List all cities (filterable by country)
GET    /api/v1/lookups/cities/{id}           # Get city by ID
POST   /api/v1/lookups/cities                # Create city
PUT    /api/v1/lookups/cities/{id}           # Update city
DELETE /api/v1/lookups/cities/{id}           # Delete city
```

### Examples
```bash
# Create City
curl -X POST http://localhost:8000/api/v1/lookups/cities \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bogotá",
    "country_id": 1
  }'

# List Cities by Country
curl http://localhost:8000/api/v1/lookups/cities?country_id=1

# List All Cities
curl http://localhost:8000/api/v1/lookups/cities?skip=0&limit=100
```

---

## 3. Company Types API

### Endpoints
```
GET    /api/v1/lookups/company-types
GET    /api/v1/lookups/company-types/{id}
POST   /api/v1/lookups/company-types
PUT    /api/v1/lookups/company-types/{id}
DELETE /api/v1/lookups/company-types/{id}
```

### Examples
```bash
# Create Company Type
curl -X POST http://localhost:8000/api/v1/lookups/company-types \
  -H "Content-Type: application/json" \
  -d '{
    "name": "S.A.S.",
    "description": "Sociedad por Acciones Simplificada"
  }'
```

---

## 4. Incoterms API

### Endpoints
```
GET    /api/v1/lookups/incoterms
GET    /api/v1/lookups/incoterms/{id}
POST   /api/v1/lookups/incoterms
PUT    /api/v1/lookups/incoterms/{id}
DELETE /api/v1/lookups/incoterms/{id}
```

### Examples
```bash
# Create Incoterm
curl -X POST http://localhost:8000/api/v1/lookups/incoterms \
  -H "Content-Type: application/json" \
  -d '{
    "code": "FOB",
    "name": "Free On Board",
    "description": "Seller delivers goods on board vessel nominated by buyer"
  }'

# Common Incoterms to Create
# FOB - Free On Board
# CIF - Cost, Insurance and Freight
# EXW - Ex Works
# DDP - Delivered Duty Paid
# FCA - Free Carrier
```

---

## 5. Currencies API

### Endpoints
```
GET    /api/v1/lookups/currencies
GET    /api/v1/lookups/currencies/{id}
POST   /api/v1/lookups/currencies
PUT    /api/v1/lookups/currencies/{id}
DELETE /api/v1/lookups/currencies/{id}
```

### Examples
```bash
# Create Currency
curl -X POST http://localhost:8000/api/v1/lookups/currencies \
  -H "Content-Type: application/json" \
  -d '{
    "code": "USD",
    "name": "US Dollar",
    "symbol": "$"
  }'

# Common Currencies to Create
# USD - US Dollar - $
# EUR - Euro - €
# COP - Colombian Peso - $
# GBP - British Pound - £
# JPY - Japanese Yen - ¥
```

---

## 6. Units API

### Endpoints
```
GET    /api/v1/lookups/units
GET    /api/v1/lookups/units/{id}
POST   /api/v1/lookups/units
PUT    /api/v1/lookups/units/{id}
DELETE /api/v1/lookups/units/{id}
```

### Examples
```bash
# Create Unit
curl -X POST http://localhost:8000/api/v1/lookups/units \
  -H "Content-Type: application/json" \
  -d '{
    "code": "kg",
    "name": "Kilogram",
    "description": "Unit of mass"
  }'

# Common Units to Create
# kg - Kilogram
# g - Gram
# m - Meter
# cm - Centimeter
# L - Liter
# pcs - Pieces
# box - Box
# pallet - Pallet
```

---

## 7. Family Types API

### Endpoints
```
GET    /api/v1/lookups/family-types
GET    /api/v1/lookups/family-types/{id}
POST   /api/v1/lookups/family-types
PUT    /api/v1/lookups/family-types/{id}
DELETE /api/v1/lookups/family-types/{id}
```

### Examples
```bash
# Create Family Type
curl -X POST http://localhost:8000/api/v1/lookups/family-types \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electronics",
    "description": "Electronic components and devices"
  }'
```

---

## 8. Matters API

### Endpoints
```
GET    /api/v1/lookups/matters
GET    /api/v1/lookups/matters/{id}
POST   /api/v1/lookups/matters
PUT    /api/v1/lookups/matters/{id}
DELETE /api/v1/lookups/matters/{id}
```

### Examples
```bash
# Create Matter
curl -X POST http://localhost:8000/api/v1/lookups/matters \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Plastic",
    "description": "Plastic materials"
  }'

# Common Matters
# Steel
# Aluminum
# Plastic
# Wood
# Glass
# Rubber
```

---

## 9. Sales Types API

### Endpoints
```
GET    /api/v1/lookups/sales-types
GET    /api/v1/lookups/sales-types/{id}
POST   /api/v1/lookups/sales-types
PUT    /api/v1/lookups/sales-types/{id}
DELETE /api/v1/lookups/sales-types/{id}
```

### Examples
```bash
# Create Sales Type
curl -X POST http://localhost:8000/api/v1/lookups/sales-types \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Retail",
    "description": "Direct sales to end consumers"
  }'

# Common Sales Types
# Retail - Direct to consumer
# Wholesale - Bulk sales
# B2B - Business to business
# Export - International sales
# Consignment - Consignment sales
```

---

## 10. Quote Statuses API

### Endpoints
```
GET    /api/v1/lookups/quote-statuses
GET    /api/v1/lookups/quote-statuses/{id}
POST   /api/v1/lookups/quote-statuses
PUT    /api/v1/lookups/quote-statuses/{id}
DELETE /api/v1/lookups/quote-statuses/{id}
```

### Examples
```bash
# Create Quote Status
curl -X POST http://localhost:8000/api/v1/lookups/quote-statuses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Draft",
    "description": "Quote is being prepared"
  }'

# Common Quote Statuses
# Draft - Being prepared
# Sent - Sent to customer
# Accepted - Customer accepted
# Rejected - Customer rejected
# Expired - Quote expired
# Converted - Converted to order
```

---

## 11. Order Statuses API

### Endpoints
```
GET    /api/v1/lookups/order-statuses
GET    /api/v1/lookups/order-statuses/{id}
POST   /api/v1/lookups/order-statuses
PUT    /api/v1/lookups/order-statuses/{id}
DELETE /api/v1/lookups/order-statuses/{id}
```

### Examples
```bash
# Create Order Status
curl -X POST http://localhost:8000/api/v1/lookups/order-statuses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pending",
    "description": "Order received, awaiting processing"
  }'

# Common Order Statuses
# Pending - Awaiting processing
# Processing - Being processed
# Shipped - In transit
# Delivered - Delivered to customer
# Cancelled - Order cancelled
# On Hold - Temporarily on hold
```

---

## 12. Payment Statuses API

### Endpoints
```
GET    /api/v1/lookups/payment-statuses
GET    /api/v1/lookups/payment-statuses/{id}
POST   /api/v1/lookups/payment-statuses
PUT    /api/v1/lookups/payment-statuses/{id}
DELETE /api/v1/lookups/payment-statuses/{id}
```

### Examples
```bash
# Create Payment Status
curl -X POST http://localhost:8000/api/v1/lookups/payment-statuses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pending",
    "description": "Payment not yet received"
  }'

# Common Payment Statuses
# Pending - Not yet paid
# Partial - Partially paid
# Paid - Fully paid
# Overdue - Payment overdue
# Refunded - Payment refunded
# Failed - Payment failed
```

---

## Common Query Parameters

All list endpoints support pagination:

```
?skip=0      # Number of records to skip (default: 0)
?limit=100   # Maximum records to return (default: 100, max: 1000)
```

Example:
```bash
# Get second page of 50 countries
curl http://localhost:8000/api/v1/lookups/countries?skip=50&limit=50
```

---

## Response Format

### Success Response (List)
```json
[
  {
    "id": 1,
    "name": "Colombia",
    "iso_code_alpha2": "CO",
    "iso_code_alpha3": "COL"
  }
]
```

### Success Response (Single)
```json
{
  "id": 1,
  "name": "Colombia",
  "iso_code_alpha2": "CO",
  "iso_code_alpha3": "COL"
}
```

### Delete Success Response
```json
{
  "message": "Country deleted successfully",
  "details": {
    "country_id": 1
  }
}
```

### Error Response
```json
{
  "error": "ValidationException",
  "message": "Country already exists: Colombia",
  "details": {
    "name": "Colombia",
    "existing_id": 1
  }
}
```

---

## HTTP Status Codes

- `200 OK` - Successful GET, PUT
- `201 Created` - Successful POST
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate resource
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## Testing with Swagger UI

Access interactive API documentation:
```
http://localhost:8000/docs
```

Features:
- Test all endpoints directly from browser
- View request/response schemas
- See validation rules
- Execute requests with authentication

---

## Seeding Initial Data

Create a Python script to seed common lookup data:

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/lookups"

# Seed Countries
countries = [
    {"name": "Colombia", "iso_code_alpha2": "CO", "iso_code_alpha3": "COL"},
    {"name": "United States", "iso_code_alpha2": "US", "iso_code_alpha3": "USA"},
    {"name": "Mexico", "iso_code_alpha2": "MX", "iso_code_alpha3": "MEX"},
]

for country in countries:
    response = requests.post(f"{BASE_URL}/countries", json=country)
    print(f"Created country: {response.json()}")

# Seed Currencies
currencies = [
    {"code": "USD", "name": "US Dollar", "symbol": "$"},
    {"code": "COP", "name": "Colombian Peso", "symbol": "$"},
    {"code": "EUR", "name": "Euro", "symbol": "€"},
]

for currency in currencies:
    response = requests.post(f"{BASE_URL}/currencies", json=currency)
    print(f"Created currency: {response.json()}")
```

---

## Best Practices

1. **Create Core Lookups First**: Countries, currencies, units
2. **Use Consistent Naming**: Keep names concise and clear
3. **Add Descriptions**: Help users understand each lookup value
4. **Validate Before Delete**: Ensure no foreign key constraints
5. **Cache Lookups**: Lookups change infrequently, cache them client-side
6. **Use ISO Codes**: Follow international standards for countries, currencies

---

## Next Steps

1. **Seed Initial Data**: Create common lookup values
2. **Test Endpoints**: Use Swagger UI or curl
3. **Integrate with Business Logic**: Use lookups in quotes, orders, invoices
4. **Add Frontend**: Create UI for lookup management
5. **Add Caching**: Implement Redis caching for frequently accessed lookups

---

Happy Coding! 🚀
