# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

水果蔬菜采购管理系统 (Fruit & Vegetable Procurement Management System) - A full-stack web application with Flask backend and vanilla HTML/CSS/JS frontend. Uses in-memory data storage (no database) with comprehensive test coverage.

## Development Commands

### Start Services
```bash
# Backend (Flask on port 5000) - creates venv automatically if needed
./start.sh
# or: cd backend && python app.py

# Frontend (HTTP server on port 8000)
./start_frontend.sh
# or: cd frontend && python3 -m http.server 8000 --bind 127.0.0.1
```

### Testing
```bash
# All tests
./run_tests.sh

# Backend only
cd backend && pytest test_api.py -v

# Frontend UI tests (requires services running)
cd frontend && pytest test_ui.py -v -s
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Backend (Flask 3.0.0)
- **File**: `backend/app.py` (~247 lines, single file)
- **Storage**: In-memory (`PURCHASE_ORDERS` list, `ORDER_COUNTER` for IDs)
- **CORS**: Enabled via `flask-cors`
- **Pattern**: RESTful API with consistent response format `{code, message, data}`

**API Endpoints:**
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/purchase/create` | Create purchase order (validates required fields) |
| GET | `/api/purchase/list` | List orders (optional `?category=` & `?status=` filters) |
| GET | `/api/purchase/<order_id>` | Get single order |
| PUT | `/api/purchase/<order_id>` | Update status/remark |
| GET | `/api/health` | Health check |

**Response Format:**
```python
{
    "code": 200,           # HTTP status code
    "message": "...",      # Descriptive message
    "data": {...}          # Response payload or None
}
```

### Frontend
- **Files**: `frontend/index.html` (main UI, ~700 lines with embedded CSS/JS), `frontend/purchase-list.html`
- **Tech**: Vanilla HTML5/CSS3/JS (no frameworks)
- **Pattern**: Mobile-first SPA with `fetch()` API calls
- **Design**: Max-width 480px container (mobile app style)

### Data Model
```python
{
    "id": "PO1001",                    # Auto-generated: PO + counter
    "supplier_name": "...",            # Required
    "product_name": "...",             # Required
    "quantity": 100,                   # Required, must be > 0
    "unit_price": 10.5,                # Required, must be >= 0
    "total_amount": 1050.00,           # Auto-calculated
    "category": "水果" or "蔬菜",       # Required
    "status": "待审批",                 # Default on create
    "created_at": "2024-01-01 10:00:00",
    "created_by": "系统",               # Default, overrideable
    "remark": ""                       # Optional
}
```

## Key Implementation Details

- **No database**: All data stored in `PURCHASE_ORDERS` list, lost on restart
- **ID generation**: Global `ORDER_COUNTER` incrementing from 1000, prefixed with "PO"
- **Validation**: Required fields checked, quantity/price validated on backend
- **Error handling**: Try-except on all routes, 404/500 handlers registered
- **Frontend routing**: Query param based (e.g., `?page=factory`)
