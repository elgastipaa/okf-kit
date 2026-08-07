"""Generación de códigos cortos."""
import string

ALPHABET = string.digits + string.ascii_letters  # base62
FIRST_ID = 100_000


def encode(n: int) -> str:
    """Convierte un id incremental en su código base62."""
    if n < 0:
        raise ValueError("los ids son positivos")
    out = ""
    while True:
        n, rem = divmod(n, len(ALPHABET))
        out = ALPHABET[rem] + out
        if n == 0:
            return out


def decode(code: str) -> int:
    """Inverso de `encode`. Lanza ValueError si el código no es base62.

    Antes usaba `ALPHABET.index`, que tira `ValueError: substring not found` — un mensaje
    que no dice nada— y el servidor devolvía 500 ante cualquier path raro. Lo encontró
    okf-init leyendo el código.
    """
    n = 0
    for ch in code:
        i = ALPHABET.find(ch)
        if i < 0:
            raise ValueError(f"'{code}' no es un código válido")
        n = n * len(ALPHABET) + i
    return n
