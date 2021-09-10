from pydantic import BaseModel


class GreetForm (BaseModel):
    name: str
