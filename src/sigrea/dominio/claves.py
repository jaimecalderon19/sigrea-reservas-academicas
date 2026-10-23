import hashlib
import secrets

ITERACIONES = 200_000


def normalizar_correo(correo: str) -> str:
    limpio = correo.strip().lower()
    if "@" not in limpio or limpio.startswith("@") or limpio.endswith("@"):
        raise ValueError("correo")
    return limpio


def hash_clave(clave: str) -> str:
    sal = secrets.token_bytes(16)
    derivado = hashlib.pbkdf2_hmac("sha256", clave.encode(), sal, ITERACIONES)
    return f"{sal.hex()}${derivado.hex()}"


def verificar_clave(clave: str, guardada: str) -> bool:
    sal, derivado = guardada.split("$", 1)
    calculado = hashlib.pbkdf2_hmac(
        "sha256", clave.encode(), bytes.fromhex(sal), ITERACIONES
    )
    return secrets.compare_digest(calculado.hex(), derivado)
