from __future__ import absolute_import, division, print_function, unicode_literals
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from db.config import *

db_engine = create_engine('postgresql+pg8000://' + POSTGRE_USERNAME + ':' + POSTGRE_PASSWORD + '@127.0.0.1/' + POSTGRE_DB,
                          convert_unicode=True, pool_size=20, max_overflow=0)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=db_engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import db.models
    #print Base.metadata.tables
    Base.metadata.create_all(bind=db_engine)
    print('db_connected')
