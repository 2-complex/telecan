
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Model = declarative_base()

class Database():
    def __init__(self, databaseUrl):
        engine = create_engine(databaseUrl, convert_unicode=True)
        session = scoped_session(sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine))

        Model.query = session.query_property()

        # import all modules here that define models.
        import models
        Model.metadata.create_all(bind=engine)

        self.models = models
        self.session = session
        self.engine = engine
