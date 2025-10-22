from fastapi import APIRouter

router = APIRouter(prefix="/students", tags=["students"])

@router.get("/")
async def get_students():
    return {"message": "Students API - coming soon"}
