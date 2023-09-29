#!/usr/bin/python3
""" holds class User"""
import models
from models.base_model import BaseModel, Base
from os import getenv
import hashlib
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class User(BaseModel, Base):
    """Representation of a user """
    if models.storage_t == 'db':
        __tablename__ = 'users'
        email = Column(String(128), nullable=False)
        _password = Column("password", String(128), nullable=False)
        first_name = Column(String(128), nullable=True)
        last_name = Column(String(128), nullable=True)
        places = relationship("Place", backref="user",
                              cascade="all, delete-orphan")
        reviews = relationship("Review", backref="user",
                               cascade="all, delete-orphan")

    else:
        email = ""
        _password = ""
        first_name = ""
        last_name = ""

    def __init__(self, *args, **kwargs):
        """initializes user"""
        super().__init__(*args, **kwargs)

    @property
    def password(self):
        """The password property"""
        return self._password

    @password.setter
    def password(self, value):
        """Set password"""
        self._password = hashlib.md5(value.encode('utf8')).hexdigest()

    def to_dict(self):
        """returns a dictionary containing all keys/values of the instance"""
        new_dict = super().to_dict()
        if getenv("HBNB_TYPE_STORAGE", "fs") == "db":
            new_dict.pop("password", None)
        return new_dict
