from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    backref,
)
from sqlalchemy import (
    Integer,
    String,
    DECIMAL,
    Boolean,
    DateTime,
    JSON,
    Date
)
from typing_extensions import Annotated
from sqlalchemy.schema import ForeignKey
from typing import List
import datetime as dt


intpk = Annotated[int, mapped_column(
    Integer(), primary_key=True, autoincrement=True)]
desc = Annotated[str, mapped_column(String(255), nullable=False)]
nick = Annotated[str, mapped_column(String(255), unique=True, nullable=False)]
comment = Annotated[str, mapped_column(String(1000), nullable=False)]
desc_unique = Annotated[str, mapped_column(
    String(255), nullable=False, unique=False)]
decimal_20_3 = Annotated[float, mapped_column(
    DECIMAL(precision=20, scale=10, asdecimal=True), nullable=True)]
code = Annotated[int, mapped_column(Integer(), unique=True, nullable=True)]
user = Annotated[str, mapped_column(String(70))]
intnull = Annotated[int, mapped_column(Integer(), nullable=True)]
units = Annotated[str, mapped_column(String(20), unique=True)]
names = Annotated[str, mapped_column(String(255), nullable=True)]
boolean = Annotated[bool, mapped_column(Boolean(), default=False)]
datetime = Annotated[dt.datetime, mapped_column(
    DateTime(), default=dt.datetime.now())]
date = Annotated[dt.date, mapped_column(
    Date(), default=dt.date.ctime
)]
on_update = Annotated[dt.datetime, mapped_column(
    DateTime(), default=dt.datetime.now(), onupdate=dt.datetime.now())]
jsonsql = Annotated[dict, mapped_column(JSON, nullable=True)]


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    username: Mapped[nick]

    location_id = mapped_column(ForeignKey("locations.id"))
    location: Mapped["Location"] = relationship(back_populates="user")

    pswrd_id = mapped_column(ForeignKey("passwords.id"))
    pswrd: Mapped["PSWRD"] = relationship(
        back_populates="user")

    userinfo_id = mapped_column(ForeignKey("userinfo.id"))
    userinfo: Mapped["UserInfo"] = relationship(
        back_populates="user")

    storedfiles: Mapped[List["Stored"]] = relationship(
        back_populates="user", single_parent=True, cascade="all, delete-orphan", passive_deletes=True)

    folders: Mapped[List["Folders"]] = relationship(
        back_populates="user", single_parent=True, cascade="all, delete-orphan", passive_deletes=True)


class UserInfo(Base):
    __tablename__ = "userinfo"

    id: Mapped[intpk]
    name: Mapped[desc]
    lastname: Mapped[desc]
    gender: Mapped[desc]
    email: Mapped[nick]
    age: Mapped[date]
    user: Mapped["User"] = relationship(
        back_populates="userinfo", single_parent=True, cascade="all, delete-orphan", passive_deletes=True)


class PSWRD(Base):
    __tablename__ = "passwords"

    id: Mapped[intpk]
    pswrd: Mapped[comment]
    lastupdate: Mapped[on_update]
    user: Mapped["User"] = relationship(
        back_populates="pswrd", single_parent=True, cascade="all, delete-orphan", passive_deletes=True)


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[intpk]
    city: Mapped[nick]
    user: Mapped[List["User"]] = relationship(
        back_populates="location", single_parent=True, cascade="all, delete-orphan", passive_deletes=True)
    country_id = mapped_column(ForeignKey("country.id"))
    country: Mapped["Country"] = relationship(back_populates="cities")


class Country(Base):
    __tablename__ = "country"

    id: Mapped[intpk]
    country: Mapped[nick]
    cities: Mapped[List["Location"]] = relationship(
        back_populates="country", single_parent=True, cascade="all, delete-orphan", passive_deletes=True)


class Stored(Base):
    __tablename__ = "storedfiles"
    id: Mapped[intpk]
    filename: Mapped[desc]
    filesize: Mapped[int]
    serversize: Mapped[int]
    filetype: Mapped[desc]
    hash: Mapped[desc]
    keys: Mapped[bytes]
    path: Mapped[nick]
    updated: Mapped[on_update]

    userid = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        back_populates="storedfiles")


class Folders(Base):
    __tablename__ = "folders"
    id: Mapped[intpk]
    name: Mapped[desc]
    parent: Mapped[int]

    userid = mapped_column(ForeignKey("users.username"))
    user: Mapped["User"] = relationship(back_populates="folders")


class Testtable(Base):
    __tablename__ = "testtable"

    id: Mapped[intpk]
    a: Mapped[desc]
    b: Mapped[desc]
    c: Mapped[desc]
    d: Mapped[desc]
    test2_id = mapped_column(ForeignKey('testtable2.id', ondelete="CASCADE"))
    padre: Mapped["Testtable2"] = relationship(
        back_populates="hijo")


class Testtable2(Base):
    __tablename__ = "testtable2"

    id: Mapped[intpk]

    e: Mapped[desc]
    f: Mapped[desc]
    g: Mapped[desc]
    hijo: Mapped["Testtable"] = relationship(
        back_populates="padre", single_parent=True, cascade="all, delete-orphan", passive_deletes=True)
    # test_id: Mapped[int] = mapped_column(ForeignKey('testtable.id'))
