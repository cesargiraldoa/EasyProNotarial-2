from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.act_catalog.router import act_catalog_router
from app.modules.cases.router import router as cases_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.document_flow.router import router as document_flow_router
from app.modules.legal_entities.router import router as legal_entities_router
from app.modules.notaries.router import router as notaries_router
from app.modules.persons.router import router as persons_router
from app.modules.templates.router import router as templates_router
from app.modules.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(notaries_router)
api_router.include_router(users_router)
api_router.include_router(cases_router)
api_router.include_router(act_catalog_router)
api_router.include_router(templates_router)
api_router.include_router(persons_router)
api_router.include_router(document_flow_router)
api_router.include_router(legal_entities_router)
api_router.include_router(dashboard_router)
