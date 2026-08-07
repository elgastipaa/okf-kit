import tempfile
import time
import unittest
from pathlib import Path

from src.codes import decode
from src.store import connect, resolve, shorten


class TestStore(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "t.db"
        self.con = connect(self.tmp)

    def test_shorten_y_resolver(self):
        code = shorten(self.con, "https://example.com")
        target, expired = resolve(self.con, decode(code))
        self.assertEqual(target, "https://example.com")
        self.assertFalse(expired)

    def test_expirado_se_distingue_de_inexistente(self):
        code = shorten(self.con, "https://example.com", ttl_days=1)
        self.con.execute("UPDATE links SET expires = ?", (int(time.time()) - 10,))
        _, expired = resolve(self.con, decode(code))
        self.assertTrue(expired)
        self.assertIsNone(resolve(self.con, 999_999_999))


class TestPisoDeIds(unittest.TestCase):
    def test_el_primer_codigo_de_una_db_nueva_respeta_el_piso(self):
        """Antes se probaba `encode(FIRST_ID)`, que no es lo que hace el store.

        El test pasaba y el piso NO se aplicaba: en una base nueva el primer código era "1".
        """
        from src.codes import FIRST_ID
        tmp = Path(tempfile.mkdtemp()) / "nueva.db"
        con = connect(tmp)
        code = shorten(con, "https://example.com")
        self.assertGreaterEqual(decode(code), FIRST_ID)
        self.assertGreaterEqual(len(code), 3)
