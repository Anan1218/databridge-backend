from fastapi import APIRouter, Depends, HTTPException
from app.models.business import BusinessCreate, BusinessReport
from app.services.business_service import BusinessService
from app.api.dependencies import verify_token

router = APIRouter()
business_service = BusinessService()

@router.post("/business", response_model=dict)
async def create_business(
    business_data: BusinessCreate,
    token = Depends(verify_token)
):
    try:
        user_id = token.get('uid')
        result = await business_service.create_or_update_business(
            user_id,
            business_data.dict()
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/business/report", response_model=BusinessReport)
async def get_business_report(token = Depends(verify_token)):
    try:
        user_id = token.get('uid')
        report = await business_service.get_business_report(user_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 