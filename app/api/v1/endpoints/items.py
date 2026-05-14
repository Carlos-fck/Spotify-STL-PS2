from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_token_header

router = APIRouter()


@router.get("/")
def read_items():
    return [{"name": "Item Foo"}, {"name": "Item Bar"}]


@router.get("/protected", dependencies=[Depends(get_token_header)])
def read_protected_items():
    return [{"name": "Protected Item 1"}, {"name": "Protected Item 2"}]