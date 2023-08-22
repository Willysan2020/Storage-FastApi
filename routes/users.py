from fastapi import Depends, Form, APIRouter, HTTPException, status, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from config.db import get_session
from sqlalchemy import select, delete, func
from cryptography.fernet import Fernet
from middlewares.verify_token_route import VerifyTokenRoute
from routes.sign_login import get_current_user
from jose import JWTError, jwt
from config.load_env import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import datetime
import bcrypt
from typing import Optional
from model.db_model import (
    User,
    UserInfo,
    PSWRD,
    Location,
    Country,
    Stored,
    Testtable,
    Testtable2
)
from schema.user import (
    Newuser,
    Newpassword,
    Newcountry,
    Newlocation,
    Newuserinfo,
    Testschema,
    Testschema2,
    SignForm,
    Token,
    TokenData
)

# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 10
PAGELIMIT = 20

user = APIRouter(route_class=VerifyTokenRoute, tags=["User"])
key = Fernet.generate_key()
f = Fernet(key)
session = next(get_session())


async def tokenuser(data: Request) -> str:
    token = data.cookies.get("access_token")
    payload = jwt.decode(str(token), SECRET_KEY, algorithms=[ALGORITHM])
    username = str(payload.get("sub"))
    return username


# @user.get("/users/me/", response_model=None)
# async def read_users_me(
#    current_user: Annotated[User, Depends(get_current_user)]
# ):
#    return current_user


@user.post("/country")
async def postcountry(data: Newcountry):
    new = Country()
    new.country = data.country
    # session = next(get_session())
    session.add(new)
    session.commit()
    return f"{new.country} added"


@user.get("/country/{id}")
async def getcountry(id: int):
    # session = next(get_session())
    ret = session.scalars(select(Country).where(Country.id == id)).one()
    ret.cities
    return ret


@user.post("/city")
async def postcity(data: Newlocation, data2: Newcountry):
    # session = next(get_session())
    new = Location()
    new.city = data.city
    ret = session.scalars(select(Country).where(
        Country.country == data2.country)).one()
    new.country_id = int(ret.id)
    new.country = ret
    session.add(new)
    session.commit()
    return f"{data.city} added"


@user.get("/city/{cityid}")
async def getcity(cityid: int):
    # session = next(get_session())
    ret = session.scalars(select(Location).where(Location.id == cityid)).one()
    ret.country
    ret.user
    return ret


@user.get("/user/{userid}/")
async def getuserid(userid: int, data: Request):
    username = await tokenuser(data)
    try:
        user = session.scalars(select(User).where(
            User.username == username)).one()
        if user.id is not userid:
            return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Autorization")
        user.pswrd
        user.userinfo
        user.location
        user.location.country
        user.storedfiles
        session.close()
        return user
    except:
        raise HTTPException(status_code=404, detail="user not found")


@user.get("/user")
async def getuser(data: Request):
    username = await tokenuser(data)
    user = session.scalars(select(User).where(User.username == username)).one()
    return user


@user.get("/user/files")
async def getuserfile(data: Request, page: Optional[int] = None):
    username = await tokenuser(data)
    if (page == None):
        files = session.scalars(select(Stored).join(
            User).where(User.username == username).order_by(Stored.filetype)).all()
    else:
        files = session.scalars(select(Stored).join(
            User).where(User.username == username).order_by(Stored.filetype).limit(PAGELIMIT).offset((page - 1)*PAGELIMIT)).all()
    filelist = []
    for row in files:
        file = {
            "fileid": row.id,
            "filename": row.filename,
            "filetype": row.filetype,
            "owner": row.user.username
        }
        filelist.append(file)
    return filelist


@user.get("/user/pages")
async def pages(data: Request):
    username = await tokenuser(data)
    totalpages = session.execute(select(func.count(Stored.id), func.sum(Stored.serversize)).join(
        User).where(User.username == username).select_from(Stored)).all()
    return {"files": int(totalpages[0][0]), "size": int(totalpages[0][1]), "pages": float(totalpages[0][0]/PAGELIMIT).__ceil__(), 'pagelimit': PAGELIMIT}


@user.get("/user/age")
async def edad(data: Request):
    username = await tokenuser(data)
    birth = session.scalars(select(UserInfo.age).join(
        User).where(User.username == username)).one()
    date = datetime.now()
    timedelta = date - birth
    age = timedelta.days/365.2425
    return {"UserName": username, "Age": age.__floor__()}


@user.get("/user/password")
def getpass():
    with open("html/user/password/index.html", "r") as html:
        content = html.read()
    return HTMLResponse(content=content, status_code=status.HTTP_200_OK)


@user.post("/user/password")
async def postpass(data: Request, password: Annotated[str, Form()]):
    username = await tokenuser(data)
    session = next(get_session())
    ret = session.scalars(select(PSWRD.pswrd).join(User).where(
        User.username == username)).one()
    state = bcrypt.checkpw(password.encode(), ret.encode())
    session.close()
    return state
