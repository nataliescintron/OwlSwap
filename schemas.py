from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class Condition(str, Enum):
    NEW = "NEW"
    GOOD = "GOOD"
    FAIR = "FAIR"

class Status(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class user(BaseModel):
    userID: str
    fname: str
    lname: str
    email: str
    password: str

class book(BaseModel):
    isbn: str
    title: str
    author: str
    edition: str
    year: str

class listing(BaseModel):
    listingID: str
    ownerID: str
    bookISBN: str
    title: str
    description: str
    condition: Condition
    status: Status

class ContactSession(BaseModel):
    sessionID: str
    listingID: str
    ownerID: str
    requesterID: str
    channel: bool
