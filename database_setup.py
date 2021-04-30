import datetime
import hashlib
import os

from flask.cli import load_dotenv
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


load_dotenv()
Base = declarative_base()
engine = create_engine(os.getenv('DB_ENGINE'))


class UserNetology(Base):
    __tablename__ = 'usernetology'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(250))
    password_hash = Column(String(64), nullable=False)

    def hash_password(self, password):
        self.password_hash = hashlib.sha256(bytes(password, 'utf-8')).hexdigest()

    def verify_password(self, password):
        return self.password_hash == hashlib.sha256(bytes(password, 'utf-8')).hexdigest()


class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey(UserNetology.id))
    datetime_creation = Column(DateTime, default=datetime.datetime.utcnow)


Base.metadata.create_all(engine)
