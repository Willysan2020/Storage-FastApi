
from fastapi import (Depends,  Form, File, APIRouter,
                     HTTPException, status, Request, Response, UploadFile)
from fastapi.responses import (
    HTMLResponse, RedirectResponse, StreamingResponse, FileResponse)
from middlewares.verify_token_route import VerifyTokenRoute
from jose import JWTError, jwt
from config.load_env import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import os
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from model.db_model import (User, Stored)
from config.db import get_session
from sqlalchemy import select, delete
from datetime import time
import base64
stored = APIRouter(route_class=VerifyTokenRoute, tags=["Files"])
session = next(get_session())

CHUNK_SIZE = 1048576
# STORED_SIZE = 1398200
# new lenght with base64 decode (1048649)b
STORED_SIZE = 1048649


def hashbytes(content: bytes):
    # Create a hash object
    hash_object = hashes.Hash(algorithm=hashes.SHA256())

    # Open the file in binary mode
    # with open(content, "rb") as f:

    # Read the file in chunks and update the hash object
    #    for chunk in f:
    #        hash_object.update(chunk)

    # Close the file
    # f.close()

    hash_object.update(content)
    # Get the hash digest
    hash_digest = hash_object.finalize().hex()
    return hash_digest


async def tokenuser(data: Request) -> str:
    token = data.cookies.get("access_token")
    payload = jwt.decode(str(token), SECRET_KEY, algorithms=[ALGORITHM])
    username = str(payload.get("sub"))
    return username


def keysequence(password: bytes, position: int):
    result = base64.urlsafe_b64encode(
        (int.from_bytes(base64.urlsafe_b64decode(password)) + position).to_bytes(32))
    return result


async def getfilefull(path: str, keys: bytes, filetype: str, hash: str, size: int):
    hash_object = hashes.Hash(algorithm=hashes.SHA256())
    filecontent = bytearray()
    seq = Sequence(0)
    with open(path, "rb") as f:
        # 1MB (1048576)B Chunk require (1398200)B to decrypt
        # new lenght with base64 decode (1048649)b
        read = iter(lambda: f.read(STORED_SIZE), b'')
        filebytes = iter(lambda: Fernet(keysequence(keys, seq.__next__())).decrypt(
            base64.urlsafe_b64encode(read.__next__())), b'')
        try:
            for row in filebytes:
                filecontent.extend(row)
                hash_object.update(row)
        except:
            return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="here")
    if hash == hash_object.finalize().hex():
        filecontent = bytes(filecontent)
        return Response(
            content=filecontent, media_type=filetype, headers={"Content-Length": f"{size}", "hash": f"{hash}"})
    return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
    # return FileResponse(path=f"Files/{username}/{filetype}/{ext}/{filepath}")


class Sequence:
    def __init__(self, start_value):
        self.now = start_value

    def __next__(self):
        current_value = self.now
        self.now += 1
        return current_value


def fileiteration(path: str, key: bytes):
    seq = Sequence(0)
    with open(path, "rb") as file:
        while (True):
            data = file.read(STORED_SIZE)
            if not data:
                break
            yield Fernet(keysequence(key, seq.__next__())).decrypt(base64.urlsafe_b64encode(data))


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


@stored.get("/file")
async def getfiles():
    html = """<html>

    <!-- HTML -->
<h2>Upload File</h2>
<form id="upload_form" enctype="multipart/form-data" method="post">
  <input type="file" name="file1" id="file1" onchange="uploadFile()"><br>
  <progress id="progressBar" value="0" max="100" style="width:300px;"></progress>
  <h3 id="status"></h3>
  <p id="loaded_n_total"></p>
</form>
<a id="link"></a>
<!-- JavaScript -->
<script>
function _(el) {
  return document.getElementById(el);
}

function uploadFile() {
  var file = _("file1").files[0];
  // alert(file.name+" | "+file.size+" | "+file.type);
  var formdata = new FormData();
  formdata.append("files", file);
  var ajax = new XMLHttpRequest();
  ajax.upload.addEventListener("progress", progressHandler, false);
  ajax.addEventListener("load", completeHandler, false);
  ajax.addEventListener("error", errorHandler, false);
  ajax.addEventListener("abort", abortHandler, false);
  ajax.open("POST", "file"); 
  ajax.send(formdata);
}

function progressHandler(event) {
  _("loaded_n_total").innerHTML = "Uploaded " + event.loaded + " bytes of " + event.total;
  var percent = (event.loaded / event.total) * 100;
  _("progressBar").value = Math.round(percent);
  _("status").innerHTML = Math.round(percent) + "% uploaded... please wait";
}

function completeHandler(event) {
    if (event.target.status === 200){
  _("status").innerHTML = "";
  _("link").innerHTML = event.target.responseText;
  _("link").href = event.target.responseText;
  _("progressBar").value = 0; //wil clear progress bar after successful upload
  }
  else { 
    _("status").innerHTML = event.target.responseText;
    _("progressBar").value = 0;
  }
}

function errorHandler(event) {
  _("status").innerHTML = "Upload Failed";
}

function abortHandler(event) {
  _("status").innerHTML = "Upload Aborted";
}

</script>
    </html>"""
    return HTMLResponse(content=html, status_code=status.HTTP_200_OK)


@stored.post("/filetest")
async def posttestfile(files: UploadFile):
    content = f"file/{files.content_type}/{files.filename}"
    return Response(content=content)


@stored.post("/multifile")
async def multifile(listfile: list[UploadFile], data: Request):
    a = []
    for file in listfile:
        b = await postimage(file, data)
        a.append(b)
    return a


@stored.get("/filetest/")
def getima():
    html = """<html><form action="/filetest" enctype="multipart/form-data" method="post"><input type="file" name="files"><button type="submit"> Enviar </button></form></html>"""
    return HTMLResponse(content=html, status_code=status.HTTP_200_OK)


@stored.post("/file")
async def postimage(files: UploadFile, data: Request):
    usernames = await tokenuser(data)

    if not os.path.exists(f"Files/{usernames}/{files.content_type}"):
        try:
            os.makedirs(f"Files/{usernames}/{files.content_type}")
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    path = f"./files/{usernames}/{files.content_type}/{files.filename}"
    if os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="This File Already Exist")

    """content = []
    while True:
        # 1MB (1048576)B Chunk require (1398200)B to decrypt
        content.append(files.file.read(1048576))
        if content[-1] == b'':
            content.pop()
            break"""
    # 1MB (1048576)B Chunk require (1398200)B to decrypt
    key = Fernet.generate_key()
    hash_object = hashes.Hash(algorithm=hashes.SHA256())
    content = iter(lambda: files.file.read(CHUNK_SIZE), b'')
    seq = Sequence(0)
    with open(path, "wb") as f:
        for row in content:
            f.write(base64.urlsafe_b64decode(
                Fernet(keysequence(key, seq.__next__())).encrypt(row)))
            hash_object.update(row)
        hash_digest = hash_object.finalize().hex()
    del hash_object
    del content
    user = session.scalars(select(User).where(
        User.username == usernames)).one()
    newstore = Stored()
    newstore.hash = hash_digest
    newstore.user = user
    newstore.userid = user.id
    newstore.filename = str(files.filename)
    newstore.filesize = int(str(files.size))
    newstore.serversize = int(os.path.getsize(path))
    newstore.filetype = str(files.content_type)
    newstore.path = path
    newstore.keys = key
    session.add(newstore)
    try:
        session.commit()
    except:
        os.remove(path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # return RedirectResponse(url=f"http://127.0.0.1:8000/file/{files.content_type}/{files.filename}/", status_code=status.HTTP_302_FOUND)
    # return RedirectResponse(f"/file/{files.content_type}/{files.filename}/", status_code=status.HTTP_302_FOUND)
    link = f"/file/{files.content_type}/{files.filename}/"
    return Response(content=link, status_code=status.HTTP_200_OK)


@stored.get("/file/{filetype}/{ext}/{filename}/")
async def getdata(filename: str, filetype: str, ext: str, data: Request):
    usernames = await tokenuser(data)
    path = f"./files/{usernames}/{filetype}/{ext}/{filename}"
    if not os.path.exists(path):
        return HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    meta = session.scalars(select(Stored).where(Stored.path == path)).one()
    if data.headers.get("Range"):
        start, seek, first, chunk, position = getranges(
            str(data.headers.get("Range")), meta.serversize
        ).values()
    else:
        headers = {
            'Content-Length': f'{meta.filesize}',
            'Accept-Ranges': 'bytes',
            'Content-Disposition': f'filename={meta.filename}'
        }
        return StreamingResponse(fileiteration(meta.path, meta.keys), headers=headers, media_type=meta.filetype)

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
    return Response(file[first:], status_code=206, headers=headers, media_type=meta.filetype)


@stored.delete("/file/{filetype}/{ext}/{filename}/")
async def delfile(filename: str, filetype: str, ext: str, data: Request):
    username = await tokenuser(data)
    if not os.path.exists(f"files/{username}/{filetype}/{ext}/{filename}"):
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File not found")
    try:
        session.execute(delete(Stored).where(
            Stored.path == f"./files/{username}/{filetype}/{ext}/{filename}"))
        session.commit()
    except:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File not found")
    os.remove(f"files/{username}/{filetype}/{ext}/{filename}")
    return HTTPException(status_code=status.HTTP_200_OK)


@stored.get("/video")
async def video():
    html = """
<html> 
<video id="myVideo" width=720 controls>
<source src="file/video/mp4/3799_1.mp4/" type="video/mp4">
</video>
<script>
</script>
</html>
"""
    return HTMLResponse(content=html)


@stored.get("/files/")
async def filegui():
    with open("./html/files/main.html", "r") as f:
        return HTMLResponse(content=f.read())


@stored.get("/files/{file}")
async def filesgui(file: str):
    return FileResponse(f"./html/files/{file}")
