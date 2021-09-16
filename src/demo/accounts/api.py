from typing import List
from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi import status
from fastapi import Request

from .schemas import AccountUpdate, AccountCreate
from .schemas import Account as AccountSchema
from .services import AccountService


router = APIRouter(
    prefix='/accounts',
)


def initialize_app(app: FastAPI):
    app.include_router(router)


@router.post(
    '', 
    response_model=AccountSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_account(
    account_create: AccountCreate,
    service: AccountService = Depends(),
):
    account = service.create_account(account_create)
    return account


@router.get('', response_model=List[AccountSchema])
def get_accounts(
    service: AccountService = Depends(),
):
    return service.get_accounts()


@router.get('/{account_id}')
def get_account(
    account_id: int,
    request: Request,
    service: AccountService = Depends(),
):
    account = service.get_account(account_id)
    return {
        '_data': AccountSchema.from_orm(account),
        '_meta': {
            'self': request.url_for('get_account', account_id=account_id),
            'parent': request.url_for('get_accounts'),
        }
    }


@router.patch('/{account_id}', response_model=AccountSchema)
def edit_account(
    account_id: int,
    account_update: AccountUpdate,
    service: AccountService = Depends()
):
    account = service.update_account(
        account_id,
        account_update,
    )
    return account


@router.put(
    '/{account_id}/avatar',
    response_model=AccountSchema,
)
def update_account_avatar(
    account_id: int,
    avatar: UploadFile = File(...),
    service: AccountService = Depends()
):
    account = service.update_account_avatar(account_id, avatar)
    return account
