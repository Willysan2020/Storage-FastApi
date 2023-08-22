from pydantic import BaseModel
from typing import Optional


class Newuser(BaseModel):
    username: str

    class Config:
        orm_mode = True


class Newpassword(BaseModel):
    pswrd: str

    class Config:
        orm_mode = True


class Newuserinfo(BaseModel):
    email: str
    name: str
    lastname: str
    age: str
    gender: str

    class Config:
        orm_mode = True


class Newlocation(BaseModel):
    city: str

    class Config:
        orm_mode = True


class Newcountry(BaseModel):
    country: str

    class Config:
        orm_mode = True


class Testschema(BaseModel):
    id: Optional[int]
    a: str
    b: str
    c: str
    d: str

    class Config:
        orm_mode = True


class Testschema2(BaseModel):
    id: Optional[int]
    e: str
    f: str
    g: str

    class Config:
        orm_mode = True


class SignForm(BaseModel):
    username: str
    pswrd: str
    name: str
    lastname: str
    age: str
    email: str
    gender: str
    city: str
    country: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
