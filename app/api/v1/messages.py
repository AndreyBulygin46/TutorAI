from fastapi import APIRouter

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("/")
async def get_messages():
    return {"message": "Messages API - coming soon"}
