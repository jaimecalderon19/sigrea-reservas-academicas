from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sigrea.infraestructura.modelos import Base


def crear_motor(url: str):
    argumentos = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=argumentos)


def preparar(url: str):
    motor = crear_motor(url)
    Base.metadata.create_all(motor)
    return sessionmaker(bind=motor, autoflush=False, autocommit=False)
