from typing import List
from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi import status
from fastapi import Request
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from .schemas import AccountUpdate, AccountCreate, AccountLogin, Token
from .schemas import Account as AccountSchema
from .schemas import RefreshToken as RefreshTokenSchema
from .services import AccountService
from .auth import Account as AccountAuth
from .auth import get_current_user
from ..exceptions import EntityConflictError
from ..exceptions import EntiyDoesNotExistError


router = APIRouter(
    prefix='/accounts',
)


def initialize_app(app: FastAPI):
    app.include_router(router)


@router.post('/login', response_model=Token)
def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    service: AccountService = Depends(),
):
    account_login = AccountLogin(
        username=credentials.username,
        password=credentials.password,
    )
    account = service.authenticate_account(account_login)
    return service.create_tokens(account)


@router.post('/refresh-token', response_model=Token)
def refresh_token(
    old_token: RefreshTokenSchema,
    service: AccountService = Depends(),
):
    try:
        account = service.get_account_by_refresh_token(old_token.token)
        return service.create_tokens(account)
    except EntiyDoesNotExistError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)



@router.post(
    '',
    response_model=AccountSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_account(
    account_create: AccountCreate,
    service: AccountService = Depends(),
):
    try:
        account = service.create_account(account_create)
        return account
    except EntityConflictError:
        raise HTTPException(status.HTTP_409_CONFLICT) from None


@router.get('', response_model=List[AccountSchema])
def get_accounts(
    current_account: AccountAuth = Depends(get_current_user),
    service: AccountService = Depends(),
):
    try:
        return service.get_accounts()
    except EntiyDoesNotExistError():
        raise HTTPException(status.HTTP_404_NOT_FOUND) from None


@router.get('/{account_id}')
def get_account(
    account_id: int,
    request: Request,
    service: AccountService = Depends(),
):
    try:
        account = service.get_account(account_id)
    except EntiyDoesNotExistError():
        raise HTTPException(status.HTTP_404_NOT_FOUND) from None
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
    try:
        account = service.update_account(
            account_id,
            account_update,
        )
        return account
    except EntiyDoesNotExistError():
        raise HTTPException(status.HTTP_404_NOT_FOUND) from None


@router.put(
    '/{account_id}/avatar',
    response_model=AccountSchema,
)
def update_account_avatar(
    account_id: int,
    avatar: UploadFile = File(...),
    service: AccountService = Depends()
):
    try:
        account = service.update_account_avatar(account_id, avatar)
        return account
    except EntiyDoesNotExistError():
        raise HTTPException(status.HTTP_404_NOT_FOUND) from None
