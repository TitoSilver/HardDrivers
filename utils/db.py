import os
from shutil import ExecError
from typing import Iterable
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models.car import Car
from models.base import Base
import sqlalchemy as sa

class SessionDB():
    def __init__(self) -> None:
        #mysql+mysqldb://scott:tiger@hostname/dbname
        try:
            adr = os.environ['ADDRESS']
            port = os.environ['PORT']
            db =  os.environ['MYSQL_DATABASE']
            usr = os.environ['MYSQL_USER']
            pasw = os.environ['MYSQL_PASSWORD']
        except ExecError as e:
            raise EnvironmentError('Missing envs')
        connection_url = sa.engine.URL.create(
            drivername="mysql",
            username=usr,
            password=pasw,
            host=adr,
            port=int(port),
            database=db,
            )

        #self.engine = create_engine(f"mysql+mysqldb://{adr}:{port}/{db}", echo=True)
        self.engine = create_engine(connection_url, echo=True)

        self.session = Session(self.engine)

        Base.metadata.create_all(self.engine)


    def __del__(self) -> None:
        self.session.close_all()

    def save_all(self, cars: Iterable[Car]) -> None:
        self.session.add_all(cars)
        self.session.commit()
