import shutil

from pathlib import Path

from typing import List
from typing import Optional

from fastapi import FastAPI
from fastapi import File
from fastapi import UploadFile
from fastapi import Form
from fastapi import HTTPException
from fastapi import Response
from fastapi import status
from fastapi.staticfiles import StaticFiles

from passlib.hash import pbkdf2_sha256

from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select

from .config import settings
from .models import GreetForm
from .models import Account as AccountModel
from .database import Account
from .database import Session

app = FastAPI()
app.mount(settings.static_url, StaticFiles(directory=settings.static_directory), name='static')


@app.get('/')
def root():
    return 'Hello, World!'


@app.post('/greet')
def greet(form: GreetForm):
    # чтобы прочитать тело запроса в виде JSON, нужно описать модель
    # from .models import GreetForm
    # и указать в качестве типа параметра эту модельку:
    return Response(f'Hello, {form.name}')


@app.post('/greet2')
def greet2(name: str = Form(...)):
    # чтобы достать данные из формы, используется директива Form
    return Response(f'Hello, {name}!!')


@app.post('/create-account')
def create_account(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
):
    with Session() as session:
        account = Account(
            email=email,
            username=username,
            password=pbkdf2_sha256.hash(password),
        )
        session.add(account)
        try:
            session.commit()
        except IntegrityError:
            raise HTTPException(status.HTTP_409_CONFLICT) from None
    return Response()


@app.get(
    '/get-accounts',
    response_model=List[AccountModel],
 )
def get_accounts():
    with Session() as session:
        accounts = session.execute(
            select(Account),
        ).scalars().all()
        return accounts


@app.get(
    '/get-account/{account_id}',
    response_model=AccountModel,
)
def get_account(account_id: int):
    with Session() as session:   
        try:
            account = session.execute(
                select(Account)
                .where(Account.id == account_id)
            ).scalar_one()
            return account
        except NoResultFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND) from None


@app.patch('/edit-account/{account_id}')
def edit_account(
    account_id: int,
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),
):
    with Session() as session:
        try:
            account = session.execute(
                select(Account)
                .where(Account.id == account_id)
            ).scalar_one()
        except NoResultFound:
            raise HTTPException(status.HTTP_404_NOT_FOUND) from None

        if not first_name and not last_name and not avatar:
            return Response()
        
        account.first_name = first_name or account.first_name
        account.last_name = last_name or account.last_name

        if avatar:
            filepath = Path.cwd() / settings.static_directory / avatar.filename
            with filepath.open(mode='wb') as f:
                shutil.copyfileobj(avatar.file, f)
            file_url = f'{settings.static_url}/{avatar.filename}'
            account.avatar = file_url

        session.commit()
    return Response()
