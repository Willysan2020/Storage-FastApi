from config.db import get_session
import uvicorn

session = next(get_session())


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000,
                log_level="info", reload=True)
