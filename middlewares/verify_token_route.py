from fastapi import Request, HTTPException, status
from fastapi.routing import APIRoute
from fastapi.responses import RedirectResponse
# from routes.users import get_user_password
from schema.user import TokenData
from jose import JWTError, jwt
from config.load_env import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# ALGORITHM = "HS256"


async def verifytoken(token: str, data: Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        useragent = payload.get("user-agent")
        if username is None or useragent != data.headers.get("user-agent"):
            return False
    except JWTError:
        # raise credentials_exception
        return False
    return True


class VerifyTokenRoute(APIRoute):

    def get_route_handler(self):
        original_route = super().get_route_handler()

        async def verify_token_midleware(data: Request):
            token = data.cookies.get("access_token")
            if not token:
                # return RedirectResponse(url="http://127.0.0.1:8000/login")
                return RedirectResponse("/login")

            user = await verifytoken(token, data)

            if user is True:
                return await original_route(data)
            else:
                # return RedirectResponse(url="http://127.0.0.1:8000/login")
                return RedirectResponse("/login")

        return verify_token_midleware
