from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

from sqlalchemy import create_engine
from hichao.base.config import SQLALCHEMY_CONF_URL

engine = create_engine(SQLALCHEMY_CONF_URL)
DBSession.configure(bind=engine)
Base.metadata.bind = engine
