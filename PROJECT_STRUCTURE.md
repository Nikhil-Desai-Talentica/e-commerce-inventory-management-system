# Project Structure

```
.
├── README.md
├── pyproject.toml
├── uv.lock
├── CHAT_HISTORY.md
├── PROJECT_STRUCTURE.md
├── app/
│   ├── main.py
│   ├── __init__.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── product.py
│   │   └── sku.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── product.py
│   │   └── sku.py
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── product.py
│   │   └── sku.py
│   └── api/
│       ├── deps.py
│       └── v1/
│           ├── __init__.py
│           ├── api.py
│           └── endpoints/
│               ├── category.py
│               ├── product.py
│               └── sku.py
├── tests/
│   ├── conftest.py
│   ├── test_categories.py
│   ├── test_products.py
│   └── test_skus.py
└── app/__pycache__/ (ignored)
```

Notes:
- `app/models`, `app/schemas`, and `app/crud` define domain models, Pydantic schemas, and data operations for categories, products, and SKUs.
- `app/api/v1` exposes FastAPI routers for category, product, and SKU endpoints; `deps.py` holds shared dependencies.
- `app/main.py` boots the FastAPI app and auto-creates tables via SQLAlchemy metadata.
- `tests/` contains async API tests using httpx and pytest fixtures; `conftest.py` configures the in-memory SQLite test database.
