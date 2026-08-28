from typing import Final
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import config

class MysqlDatabase: 
    BASE: Final = declarative_base()

    def __init__(self):
        ssl_args = {'ssl_ca': 'certs/root.crt'}
        self.__engine = create_engine(str(config.connection_mysql), connect_args=ssl_args)
        session = sessionmaker(autocommit=False, autoflush=False, bind=self.__engine)
        self.__session = session()

    @property 
    def session(self): 
        return self.__session

    @property
    def engine(self): 
        return self.__engine
