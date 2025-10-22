from fastapi import APIRouter

router = APIRouter(prefix="/materials", tags=["materials"])

@router.get("/")
async def get_materials():
    return {"message": "Materials API - coming soon"}
