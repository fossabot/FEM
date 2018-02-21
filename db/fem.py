#! /Users/ewen/anaconda3/bin/python
# coding: utf-8

"""Class for fem.db ."""


from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Materials(Base):
    __tablename__ = 'Materials'
    Name = Column(String(50), primary_key=True)
    Description = Column(String(250))
    E = Column(Integer)


class Sections(Base):
    global h, b
    __tablename__ = 'Sections'
    Name = Column(String(50), primary_key=True)
    raw_S = Column(String(250))
    raw_IY = Column(String(250))
    raw_IZ = Column(String(250))
    raw_IG = Column(String(250))
    raw_Image = Column(LargeBinary)
    h = 10
    b = 10

    @property
    def S(self):
        return eval(self.raw_S)

    @property
    def I(self):
        return eval(self.raw_IG)
