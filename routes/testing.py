from math import log
import random
import base64
import os
from fastapi import Depends, Form, APIRouter, HTTPException, status, Request, Response, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from typing import Annotated
from config.db import get_session
from sqlalchemy import select, delete
from cryptography.fernet import Fernet
from middlewares.verify_token_route import VerifyTokenRoute
from routes.sign_login import get_current_user
from jose import JWTError, jwt
from config.load_env import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import datetime
import bcrypt
from model.db_model import (
    User,
    UserInfo,
    PSWRD,
    Location,
    Country,
    Stored,
    Folders,
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
from routes.files import hashbytes
test = APIRouter(tags=["Test"])
session = next(get_session())


@test.get("/favicon.ico")
def favicon():
    return Response(content=open("icon-willy.svg", "r").read(), media_type='image/svg+xml')


@test.post("/form")
async def postform(data: Request):
    return await data.form()


@test.get("/form")
def form():
    html = """
    <html>
 
    <form id="myForm" action="/form" method="post">
  <input type="hidden" name="Position" id="myInput">
  <button type="submit">Submit</button>
</form>

<script>
if ("geolocation" in navigator) {
  // Geolocation is supported
  navigator.geolocation.getCurrentPosition(
    function(position) {
      // Get latitude and longitude
      var latitude = position.coords.latitude;
      var longitude = position.coords.longitude;

      var a = "Latitude: " + latitude + ", Longitude: " + longitude ;
      var myVariable = a;
      document.getElementById("myInput").value = myVariable;
      // Use latitude and longitude as needed
      //console.log("Latitude: " + latitude + ", Longitude: " + longitude);
    },
    function(error) {
      // Handle error
      console.log("Error retrieving location: " + error.message);
    }
  );
} else {
  // Geolocation is not supported
  console.log("Geolocation is not supported by this browser.");
}



  // JavaScript code
  var myVariable = a;
  document.getElementById("myInput").value = myVariable;
</script>
    </html>
    """
    return HTMLResponse(content=html, status_code=status.HTTP_200_OK)


@test.post("/test")
def testpost(test: Testschema, test2: Testschema2):
    newtest1 = Testtable(**test.dict())
    newtest2 = Testtable2(**test2.dict())
    newtest1.padre = newtest2
    # session = next(get_session())
    session.add_all([newtest2, newtest1])
    session.commit()
    return "ok"


@test.get("/test")
async def testroute():
    # session = next(get_session())

    ret = session.execute(select(Testtable, Testtable2).join(Testtable2).where(
        Testtable.test2_id == Testtable2.id))
    # from model.db_model importprint(ret)
    # ret1 = []
    schema4 = {}
    for row in ret:
        schema1 = Testschema.from_orm(row.Testtable)
        schema2 = Testschema2.from_orm(row.Testtable2)
        schema3 = schema1.dict() | schema2.dict()
        schema4.update({f"Table {row.Testtable.id}": schema3})
    return schema4


@test.get("/test/{user}")
async def testidroute(user: int):
    # session = next(get_session())
    try:
        ret = session.scalars(
            select(Testtable).where(Testtable.id == user)).one()
    except:
        raise HTTPException(status_code=404, detail="user not found")
    ret.padre
    return ret


@test.delete("/test/{userid}")
async def deletetest(userid: int):
    session = next(get_session())
    session.execute(delete(Testtable2).where(Testtable2.id == userid))
    session.commit()
    return "ok"


@test.put("/test/{userid}")
async def updatetest(userid: int, schema: Testschema):
    # session = next(get_session())
    ret = session.scalars(select(Testtable).where(
        Testtable.id == userid)).one()
    ret.a = schema.a
    try:
        session.commit()
    except:
        HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="cannot update")
    return "ok"


@test.get("/template")
async def gethtml():
    f = open("html/test/index.html", "r")
    return HTMLResponse(content=f.read())


@test.get("/template/{folder}/{file}")
async def gethtmlcontent(file: str, folder: str):
    f = open(f"html/{folder}/{file}", "r")
    return HTMLResponse(content=f.read())

CHUNK_SIZE = 1048576
# STORED_SIZE = 1398200
# new lenght with base64 decode (1048649)b
STORED_SIZE = 1048649


class Sequence:
    def __init__(self, start_value):
        self.now = start_value

    def __next__(self):
        current_value = self.now
        self.now += 1
        return current_value


@test.get("/crazy")
async def testvideo():
    with open("testkey.txt", "rb") as okey:
        key = okey.read()
    x = open("encryptedfile.txt", "rb")
    # 1MB (1048576)B Chunk require (1398200)B to decrypt
    # new lenght with base64 decode (1048649)b
    seq = Sequence(0)
    chunk = iter(lambda: x.read(STORED_SIZE), b'')
    test = iter(lambda: Fernet(keysequence(key, seq.__next__())).decrypt(
        base64.urlsafe_b64encode(chunk.__next__())), b'')
    return StreamingResponse(test, media_type="video/mp4")


@test.post("/crazy")
async def postcrazy(file: UploadFile):
    with open("testkey.txt", "rb") as okey:
        key = okey.read()
    content = []
    while True:
        # 1MB (1048576)B Chunk require (1398200)B to decrypt
        content.append(file.file.read(CHUNK_SIZE))
        if content[-1] == b'':
            content.pop()
            break
    print(file.content_type)
    with open("encryptedfile.txt", "wb") as h:
        position = 0
        for row in content:
            # new lenght with base64 decode (1048649)b
            h.write(base64.urlsafe_b64decode(
                Fernet(keysequence(key, position)).encrypt(row)))
            position += 1
    okey.close()
    h.close()
    return Response(status_code=status.HTTP_200_OK)


def keysequence(password: bytes, position: int) -> bytes:
    result = base64.urlsafe_b64encode(
        (int.from_bytes(base64.urlsafe_b64decode(password)) + position).to_bytes(32))
    return result


def iteration(path: str, key: bytes):
    i = 0
    with open(path, "rb") as file:
        while (True):
            data = file.read(STORED_SIZE)
            if not data:
                break
            print(i)
            yield Fernet(keysequence(key, i)).decrypt(base64.urlsafe_b64encode(data))
            i += 1


async def tokenuser(data: Request) -> str:
    token = data.cookies.get("access_token")
    payload = jwt.decode(str(token), SECRET_KEY, algorithms=[ALGORITHM])
    username = str(payload.get("sub"))
    return username


def getranges(ranges: str, size: int) -> dict:
    start, end = ranges.replace("bytes=", "").split("-")
    start = int(start)
    position = (start/CHUNK_SIZE).__floor__()
    seek = (STORED_SIZE * position)
    delta = (CHUNK_SIZE * position)
    first = start - delta
    sum = seek + STORED_SIZE
    if (sum < size):
        chunk = STORED_SIZE
    else:
        chunk = (size - seek)
    return {"start": start, "seek": seek, "first": first, "chunk": chunk, "position": position}


@test.get("/test/file/{filetype}/{ext}/{filename}/")
async def getdata(filename: str, filetype: str, ext: str, data: Request):
    usernames = await tokenuser(data)
    path = f"./files/{usernames}/{filetype}/{ext}/{filename}"
    if not os.path.exists(path):
        return HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    meta = session.scalars(select(Stored).where(Stored.path == path)).one()
    if data.headers.get("Range"):
        start, seek, first, chunk, position = getranges(
            str(data.headers.get("Range")), meta.serversize).values()
        print(data.headers.get("Range"))
        print(first)
        print(CHUNK_SIZE)
    else:
        headers = {
            'Content-Length': f'{meta.filesize}',
            'Accept-Ranges': 'bytes',
            'Content-Disposition': f'filename={meta.filename}'
        }
        return StreamingResponse(iteration(meta.path, meta.keys), headers=headers, media_type=meta.filetype)

    with open(path, "rb") as video:
        video.seek(seek)
        file = Fernet(keysequence(meta.keys, position)
                      ).decrypt(base64.urlsafe_b64encode(video.read(chunk)))
    headers = {
        'Content-Length': f'{len(file[first:])}',
        'Accept-Ranges': 'bytes',
        'Content-Range': f'bytes {start}-{str((start + len(file[first:])) - 1)}/{meta.filesize}',
        'Content-Disposition': f'filename={meta.filename}'
    }
    print(headers.get("Content-Range"))
    print(headers.get("Content-Length"))
    return Response(file[first:], status_code=206, headers=headers, media_type=meta.filetype)


@test.get("/randombytes")
async def bytesrandom():
    key = Fernet.generate_key()
    keybytes = base64.urlsafe_b64decode(key)
    keyint = int.from_bytes(keybytes) + 1
    key = base64.urlsafe_b64encode(keyint.to_bytes(32))
    msg = random.randbytes(1024**2)
    try:
        send = base64.urlsafe_b64decode(Fernet(key).encrypt(msg)).__len__()
    except:
        send = "ERROR"
    return {"password": key, "msg": send, "lenght": msg.__len__()}


"""
async def dont():
    f = session.scalars(select(Stored.path)).all()
    l1 = session.scalars(select(Stored.serversize)).all()
    for i in f:
        key = session.scalars(
            select(Stored.keys).where(Stored.path == i)).all()
        a = bytearray()
        seq = Sequence(0)
        with open(i, 'rb') as file:
            new = iter(lambda: file.read(1398200), b'')
            newbytes = iter(lambda: Fernet(
                key[0]).decrypt(new.__next__()), b'')
            for row in newbytes:
                a.extend(base64.urlsafe_b64decode(
                    Fernet(keysequence(key[0], seq.__next__())).encrypt(row)))
        file.close()
        with open(i, 'wb') as file:
            file.write(a)
            file.close()
        size = int(os.path.getsize(i))
        ret = session.scalars(select(Stored).where(Stored.path == i)).one()
        ret.serversize = size
        session.commit()
    l2 = session.scalars(select(Stored.serversize)).all()
    return [l1, l2]
"""


@test.get("/folder")
def folder(data: Request):
    username = tokenuser(data)
    user = session.scalars(select(User).where(User.username == username)).one()
    newfolder = Folders()
    newfolder.user = user
    newfolder.userid = user.id
    newfolder.name = str(username)
    newfolder.parent = -1
    session.add(newfolder)
    try:
        session.commit()
    except:
        return "fail"
    return "ok"
