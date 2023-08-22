from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from .load_env import DB_NAME, DB_TYPE, HOST, DB_PASSWORD, HOST_PORT, DB_USER

url = f"{DB_TYPE}://{DB_USER}:{DB_PASSWORD}@{HOST}:{HOST_PORT}/{DB_NAME}"

engine = create_engine(url, echo=False)
meta = MetaData()
Session = sessionmaker(engine)


def get_session():
    with Session() as session:
        yield session
