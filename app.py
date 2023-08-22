from fastapi import FastAPI
from routes.users import user
from routes.sign_login import loging
from routes.files import stored
from routes.testing import test

app = FastAPI()
app.include_router(user)
app.include_router(loging)
app.include_router(stored)
app.include_router(test)
