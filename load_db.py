from config.db import engine
from model.db_model import Base


def load_data():
    Base.metadata.create_all(engine)


def reset_db():
    Base.metadata.drop_all(engine)


if __name__ == "__main__":
    reset_db()
    load_data()
