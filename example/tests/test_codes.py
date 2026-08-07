import unittest

from src.codes import decode, encode


class TestCodes(unittest.TestCase):
    def test_roundtrip(self):
        for n in (0, 1, 61, 62, 100_000, 999_999):
            self.assertEqual(decode(encode(n)), n)

    def test_codigo_invalido_no_explota_feo(self):
        with self.assertRaises(ValueError):
            decode("no-existe!")

    def test_ids_negativos_explotan(self):
        with self.assertRaises(ValueError):
            encode(-1)
