from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/test")
def test_route():
    return {"message": "API is working perfectly!"}
