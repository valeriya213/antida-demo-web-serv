from fastapi import FastAPI
from fastapi import Form
from fastapi import Response
from passlib.hash import pbkdf2_sha256


from .models import GreetForm
from .database import Account
from .database import Session

app = FastAPI()


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
        session.commit()
    return Response()
