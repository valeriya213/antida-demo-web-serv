from fastapi import FastAPI
from fastapi import Form
from fastapi import Response


from .models import GreetForm

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
