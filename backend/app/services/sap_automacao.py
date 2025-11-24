from fastapi import APIRouter, Depends, Body
from app.services.sap_service import SAPService, SAPLogin

router = APIRouter()

# Instancia o serviço
sap_service = SAPService()

@router.post("/automar-sap", tags=["SAP"])
async def automar_sap(
    login_data: SAPLogin = Body(...)
):
    """
    Endpoint para iniciar uma automação SAP.
    Recebe login/senha no corpo da requisição.
    """
    return await sap_service.run_sap_automation(login_data)