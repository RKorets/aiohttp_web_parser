from datetime import datetime
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class Site(Base):
    __tablename__ = 'site'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    domen = Column(String(150), nullable=False, unique=True)

    logging = relationship('Logging', back_populates='site')
    categories = relationship('Categories', back_populates='site')
    data = relationship('Data', back_populates='site')


class Categories(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    categories_name = Column(String(150), nullable=True)
    categories_url = Column(String(150), nullable=False)

    site_id = Column(Integer, ForeignKey('site.id'), nullable=True)
    site = relationship('Site', back_populates='categories')


class Logging(Base):
    __tablename__ = "logging"

    id = Column(Integer, primary_key=True)
    date_parse = Column(DateTime, default=datetime.now())
    categories_name = Column(String(150), nullable=False)

    site_id = Column(Integer, ForeignKey('site.id'), nullable=False)
    site = relationship('Site', back_populates='logging')


class Data(Base):
    __tablename__ = "data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(250), nullable=True)
    product_price = Column(Integer, nullable=True)
    product_url = Column(String(200), nullable=True)
    categories_name = Column(String(100), nullable=True)

    site_id = Column(Integer, ForeignKey('site.id'), nullable=True)
    site = relationship('Site', back_populates='data')


async def pg_context(app):
    conf = app['config']['mysql']
    url_db = f"mysql+pymysql://{conf['user']}:{conf['password']}@{conf['host']}/{conf['database']}"
    DBSession = sessionmaker(bind=create_engine(url_db))
    session = DBSession()
    app['db_session'] = session
    yield
    app['db_session'].close()
