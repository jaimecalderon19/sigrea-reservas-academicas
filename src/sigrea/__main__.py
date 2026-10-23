import os

import uvicorn

from sigrea.api.app import create_app
from sigrea.aplicacion.identidad import crear_cuenta
from sigrea.infraestructura.modelos import Usuario


def main() -> None:
    url = os.environ.get("SIGREA_DATABASE_URL", "sqlite:///./sigrea.db")
    app = create_app(url)
    db = app.state.fabrica()
    try:
        if db.query(Usuario).count() == 0:
            crear_cuenta(
                db,
                os.environ.get("SIGREA_ADMIN_NOMBRE", "Administrador"),
                os.environ.get("SIGREA_ADMIN_CORREO", "admin@uninpahu.edu.co"),
                os.environ.get("SIGREA_ADMIN_CLAVE", "cambiar-esta-clave"),
                "administrador",
            )
    finally:
        db.close()
    uvicorn.run(
        app,
        host=os.environ.get("SIGREA_HOST", "127.0.0.1"),
        port=int(os.environ.get("SIGREA_PORT", "8000")),
    )


if __name__ == "__main__":
    main()
