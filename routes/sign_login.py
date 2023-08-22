
from fastapi import Depends, APIRouter, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from typing import Annotated
from config.db import get_session
import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from config.load_env import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy import select
from datetime import datetime, timedelta

from model.db_model import (
    User,
    UserInfo,
    PSWRD,
    Location,
)
from schema.user import (
    Newuser,
    Newuserinfo,
    TokenData
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
loging = APIRouter(tags=["Sign And Login"])
session = next(get_session())


def get_user_password(username: str):
    try:
        ret = session.scalars(select(User).where(
            User.username == username)).one()
        ret.pswrd
        return ret
    except:
        return False


def authuser(username: str, password: str):
    if not get_user_password(username):
        return False
    if not bcrypt.checkpw(password.encode(), get_user_password(username).pswrd.pswrd.encode()):
        return False
    return get_user_password(username)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # async def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_password(token_data.username)
    if user is None:
        raise credentials_exception
    return user


@loging.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], data: Request
):
    user = authuser(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    useragent = data.headers.get("user-agent")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user-agent": useragent}, expires_delta=access_token_expires
    )
    # response = RedirectResponse(
    #    url=f"http://127.0.0.1:8000/user", status_code=status.HTTP_302_FOUND)
    response = RedirectResponse("/user", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        expires=access_token_expires,
        secure=False,  # Use 'secure=True' for HTTPS connections
        httponly=True,  # Use 'httponly=True' to prevent JavaScript access
    )
    return response
    # return {"access_token": access_token, "token_type": "bearer"}


@loging.get("/login")
async def logingui():
    with open("./html/login/main.html", "r") as f:
        return HTMLResponse(content=f.read())


@loging.get("/login/{file}")
async def loginfgui(file: str):
    return FileResponse(f"./html/login/{file}")


@loging.post("/login")
async def logpost(data: Request):
    ret = data.cookies.get("access_token")
    ret1 = await data.form()
    # ret1._dict.update({"cookie": ret})
    # ret2 = data.headers.get("user-agent")
    return ret
    # return RedirectResponse(url="http://127.0.0.1:8000/token")
    # ret1 = authuser(ret.get("username"), ret.get("password"))

    # return HTTPException(status_code=status.HTTP_202_ACCEPTED)
    # return RedirectResponse(url="http://127.0.0.1:8000/login", status_code=status.HTTP_302_FOUND)
    # return ret


@loging.get("/sign")
async def usersign():
    html = """
    <html>
    <head>
    <title>login</title>
    </head>
    <body>
    <h1>Data</h1>
    <form action="/sign" method="post">
        <label for="fname">Username:</label><br>
    <input type="text" id="fname" name="username" value="UserName"><br><br>
        <label for="lname">Password:</label><br>
    <input type="password" id="lname" name="pswrd" value="Password"><br><br>
        <label for="lname">Email:</label><br>
    <input type="email" id="lname" name="email" value="Email@gmail.com"><br><br>
        <label for="lname">Name:</label><br>
    <input type="text" id="lname" name="name" value="FirstName"><br><br>
        <label for="lname">LastName:</label><br>
    <input type="text" id="lname" name="lastname" value="LastName"><br><br>
        <label for="lname">Age:</label><br>
    <input type="date" id="lname" name="age" value="2000-06-02"><br><br>
        <label for="lname">Gender:</label><br>
    <input type="radio" id="male" name="gender" value="Male">
    <label for="male">Male:</label>
    <input type="radio" id="female" name="gender" value="Female">
    <label for="female">Female:</label>
    <br><br>
        <label for="lname">City:</label><br>
    <input type="text" id="lname" name="city" value="Caracas"><br><br>
        <label for="lname">Country:</label><br>
    <input type="text" id="lname" name="country" value="Venezuela"><br><br>
        
    
    <button type="submit">Login</button>
    
    </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=status.HTTP_200_OK)


@loging.post("/sign")
# def postuser(user: Newuser, userinfo: Newuserinfo, password: Newpassword, location: Newlocation, country: Newcountry):
async def postuser(data: Request):
    dataform = await data.form()
    # a = dict(dataform)
    # info = SignForm(**a)
    # session = next(get_session())
    new_user = User(**Newuser(**dict(dataform)).dict())
    new_password = PSWRD()
    new_userinfo = UserInfo(**Newuserinfo(**dict(dataform)).dict())
    new_user.userinfo = new_userinfo
    new_password.pswrd = bcrypt.hashpw(
        str(dataform.get("pswrd")).encode("utf-8"), bcrypt.gensalt()).decode()
    new_user.pswrd = new_password
    ret = session.scalars(select(Location).where(
        Location.city == str(dataform.get("city")))).one()
    new_user.location = ret
    session.add_all([new_password, new_userinfo, new_user])
    try:
        session.commit()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # return RedirectResponse(url="http://127.0.0.1:8000/login", status_code=status.HTTP_302_FOUND)
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


@loging.get("/auth")
async def auto(
    user: str, password: str
):
    return authuser(user, password)
