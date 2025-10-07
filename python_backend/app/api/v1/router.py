from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, services, invoices, tickets, orders, profile

api_router = APIRouter()

# Authentication routes (no /admin prefix)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Profile route
api_router.include_router(profile.router, prefix="/profile", tags=["Profile"])

# Admin routes
api_router.include_router(users.router, prefix="/admin/users", tags=["Admin - Users"])
api_router.include_router(orders.router, prefix="/admin/orders", tags=["Admin - Orders"])
api_router.include_router(services.router, prefix="/admin/services", tags=["Admin - Services"])
api_router.include_router(invoices.router, prefix="/admin/invoices", tags=["Admin - Invoices"])
api_router.include_router(tickets.router, prefix="/admin/tickets", tags=["Admin - Tickets"])
