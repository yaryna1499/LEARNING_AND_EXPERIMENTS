# https://medium.com/@kmuhsinn/the-repository-pattern-in-python-write-flexible-testable-code-with-fastapi-examples-aa0105e40776
"""
Repository Pattern — full self-contained demonstration.

Decouples business logic from data access behind an abstract interface.
Swap implementations (in-memory, SQLite, PostgreSQL, mock) without touching
service code.  Key benefit: business logic is unit-testable without a real DB.
"""

from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


# ── Domain model ──────────────────────────────────────────────────────────────

@dataclass
class Product:
    """Simple domain entity — no framework dependency."""
    name: str
    price: float
    id: Optional[int] = None


# ── Abstract repository (the contract) ────────────────────────────────────────

class ProductRepository(ABC):
    """Interface that service layer depends on, never on a concrete store."""

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        ...

    @abstractmethod
    def add(self, product: Product) -> Product:
        """Persist product; returns it with generated id populated."""
        ...

    @abstractmethod
    def list_all(self) -> list[Product]:
        ...

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """True if a product was actually removed."""
        ...


# ── In-memory implementation (fast tests / dev) ──────────────────────────────

class InMemoryProductRepository(ProductRepository):
    """Stores products in a dict.  Zero I/O, perfect for unit tests."""

    def __init__(self) -> None:
        self._store: dict[int, Product] = {}
        self._next_id = 1

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self._store.get(product_id)

    def add(self, product: Product) -> Product:
        new = Product(id=self._next_id, name=product.name, price=product.price)
        self._store[new.id] = new
        self._next_id += 1
        return new

    def list_all(self) -> list[Product]:
        return list(self._store.values())

    def delete(self, product_id: int) -> bool:
        if product_id in self._store:
            del self._store[product_id]
            return True
        return False


# ── SQLite implementation (real persistence) ─────────────────────────────────

class SqliteProductRepository(ProductRepository):
    """Stores products in a SQLite table.  Uses stdlib only — no ORM."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS products ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  name TEXT NOT NULL,"
            "  price REAL NOT NULL"
            ")"
        )

    def get_by_id(self, product_id: int) -> Optional[Product]:
        row = self._conn.execute(
            "SELECT id, name, price FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
        return Product(id=row[0], name=row[1], price=row[2]) if row else None

    def add(self, product: Product) -> Product:
        cur = self._conn.execute(
            "INSERT INTO products (name, price) VALUES (?, ?)",
            (product.name, product.price),
        )
        self._conn.commit()
        return Product(id=cur.lastrowid, name=product.name, price=product.price)

    def list_all(self) -> list[Product]:
        rows = self._conn.execute("SELECT id, name, price FROM products").fetchall()
        return [Product(id=r[0], name=r[1], price=r[2]) for r in rows]

    def delete(self, product_id: int) -> bool:
        cur = self._conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self._conn.commit()
        return cur.rowcount > 0

    def close(self) -> None:
        self._conn.close()


# ── Service layer (business logic, repository-agnostic) ──────────────────────

class ProductService:
    """Business logic depends on *the interface*, not a concrete store.

    Swap the repository at construction time — the service never knows
    whether data lives in memory, SQLite, or a cloud API.
    """

    def __init__(self, repo: ProductRepository) -> None:
        self._repo = repo

    def create(self, name: str, price: float) -> Product:
        return self._repo.add(Product(name=name, price=price))

    def get(self, product_id: int) -> Optional[Product]:
        return self._repo.get_by_id(product_id)

    def list(self) -> list[Product]:
        return self._repo.list_all()

    def delete(self, product_id: int) -> bool:
        return self._repo.delete(product_id)


# ── Usage / smoke test ───────────────────────────────────────────────────────

def _smoke_test(repo: ProductRepository, label: str) -> None:
    svc = ProductService(repo)

    # Create
    p1 = svc.create("Widget", 9.99)
    p2 = svc.create("Gadget", 24.99)
    assert p1.id is not None and p2.id is not None, "ids must be assigned"

    # Read
    fetched = svc.get(p1.id)
    assert fetched is not None and fetched.name == "Widget"

    # List
    assert len(svc.list()) == 2

    # Delete
    assert svc.delete(p1.id) is True
    assert svc.delete(p1.id) is False  # already gone
    assert len(svc.list()) == 1

    print(f"[OK] {label}")


if __name__ == "__main__":
    _smoke_test(InMemoryProductRepository(), "InMemoryProductRepository")
    _smoke_test(SqliteProductRepository(), "SqliteProductRepository")
    print("All repository implementations pass the same contract.")