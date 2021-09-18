from pathlib import Path
import shutil
from typing import List
from fastapi import Depends
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import NoResultFound
from passlib.hash import pbkdf2_sha256

from ..config import get_settings
from ..database import get_session
from ..database import Session
from ..exceptions import EntityConflictError
from ..exceptions import EntiyDoesNotExistError
from .auth import create_token
from .models import Account, RefreshToken
from .schemas import AccountCreate, AccountUpdate, AccountLogin, Token


class AccountService:
    def __init__(
        self,
        session: Session = Depends(get_session),
        settings=Depends(get_settings),
    ):
        self.session = session
        self.settings = settings

    def create_account(self, account_create: AccountCreate):
        account = Account(
            email=account_create.email,
            username=account_create.username,
            password=pbkdf2_sha256.hash(account_create.password),
        )
        self.session.add(account)
        try:
            self.session.commit()
            return account
        except IntegrityError:
            raise EntityConflictError from None

    def authenticate_account(self, account_login: AccountLogin) -> Account:
        try:
            account = self.session.execute(
                select(Account)
                .where(Account.username == account_login.username)
            ).scalar_one()
        except NoResultFound:
            raise EntiyDoesNotExistError from None
        if not pbkdf2_sha256.verify(account_login.password, account.password):
            raise EntiyDoesNotExistError
        return account

    def create_tokens(self, account: Account) -> Token:
        access_token = create_token(account, self.settings.jwt_access_livetime)
        refresh_token = create_token(account, self.settings.jwt_refresh_lifetime)

        try:
            account_token = self.session.execute(
                select(RefreshToken)
                .where(RefreshToken.account_id == account.id)
            ).scalar_one()

            account_token.token = refresh_token
        except NoResultFound:
            self.session.add(
                RefreshToken(
                    account_id=account.id,
                    token=refresh_token,
                ),
            )
        self.session.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer',
        )

    def get_accounts(self) -> List[Account]:
        accounts = self.session.execute(
            select(Account),
        ).scalars().all()
        return accounts

    def get_account(self, account_id: int) -> Account:
        return self._get_account(account_id)

    def get_account_by_refresh_token(self, token: str) -> Account:
        try:
            account = self.session.execute(
                select(Account)
                .join_from(Account, RefreshToken)
                .where(RefreshToken.token == token)
            ).scalar_one()
            return account
        except NoResultFound:
            raise EntiyDoesNotExistError from None

    def get_account_by_username(self, username: str) -> Account:
        try:
            account = self.session.execute(
                select(Account)
                .where(Account.username == username)
            ).scalar_one()
            return account
        except NoResultFound:
            raise EntiyDoesNotExistError from None

    def update_account(self, account_id: int, account_update: AccountUpdate):
        account = self._get_account(account_id)

        for k, v in account_update.dict(exclude_unset=True):
            setattr(account, k, v)

        self.session.commit()
        return account

    def update_account_avatar(self, account_id: int, avatar: UploadFile):
        account = self._get_account(account_id)

        filepath = Path.cwd() / self.settings.static_directory / avatar.filename
        with filepath.open(mode='wb') as f:
            shutil.copyfileobj(avatar.file, f)
        file_url = f'{self.settings.static_url}/{avatar.filename}'
        account.avatar = file_url
        self.session.commit()
        return account

    def _get_account(self, account_id: int) -> Account:
        try:
            account = self.session.execute(
                select(Account)
                .where(Account.id == account_id)
            ).scalar_one()
            return account
        except NoResultFound:
            raise EntiyDoesNotExistError from None
