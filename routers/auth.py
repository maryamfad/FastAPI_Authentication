from fastapi import APIRouter

router = APIRouter()


@router.get("/auth/")
async def authenticate():
    return {"message": "Authenticated"}
