from fastapi import APIRouter

receipt_router = APIRouter()


@receipt_router.post("/receipts")
def create_receipt(receipt_uid: str):
    return {"message": f"Receipt <{receipt_uid}> created successfully"}