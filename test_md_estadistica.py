import unittest
from estadistica import MedidasDescriptivas

class TestMedidasDescrptivas(unittest.TestCase):
    def setUp(self):
        self.md = MedidasDescriptivas()
        for x in [1200,1500,1500,1800,2100,2400,2400,3000,3600,9000]:
            self.md.agregar(x)

    def test_conteo(self):
        self.assertEqual(self.md.conteo, 10)

    def test_suma(self):
        self.assertEqual(self.md.suma, 28500)

    def test_max(self):
        self.assertEqual(self.md.max, 9000)

    def test_min(self):
        self.assertEqual(self.md.min, 1200)

    def test_rango(self):
        self.assertEqual(self.md.rango(), 7800)

    def test_media(self):
        self.assertAlmostEqual(self.md.media(), 2850.00)

    def test_varianza(self):
        self.assertAlmostEqual(self.md.varianza(), 5205000.00)

    def test_desviación(self):
        self.assertAlmostEqual(self.md.desviación(), 2281.45, places= 2)

    def test_coef_variación(self):
        self.assertAlmostEqual(self.md.coef_variación(),0.8005, places= 3)
