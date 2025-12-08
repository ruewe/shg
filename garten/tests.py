from django.test import TestCase, Client
from .models import Sorte, Kategorie, Art, PflanzplanEintrag
from datetime import date

class ModelTests(TestCase):

    def setUp(self):
        self.kategorie = Kategorie.objects.create(name="Gemüse")
        self.art = Art.objects.create(name="Tomate")
        self.sorte = Sorte.objects.create(
            name="Harzfeuer",
            kategorie=self.kategorie,
            art=self.art,
            bestand=10,
            einheit='ANZ'
        )

    def test_kategorie_creation(self):
        """Test Kategorie creation and string representation"""
        self.assertEqual(str(self.kategorie), "Gemüse")
        self.assertTrue(isinstance(self.kategorie, Kategorie))

    def test_art_creation(self):
        """Test Art creation and string representation"""
        self.assertEqual(str(self.art), "Tomate")
        self.assertTrue(isinstance(self.art, Art))

    def test_sorte_creation(self):
        """Test Sorte creation and string representation"""
        self.assertEqual(self.sorte.name, "Harzfeuer")
        self.assertEqual(self.sorte.kategorie, self.kategorie)
        self.assertEqual(self.sorte.art, self.art)
        self.assertEqual(str(self.sorte), "Harzfeuer (Gemüse)")

    def test_pflanzplan_eintrag_creation(self):
        """Test PflanzplanEintrag creation"""
        eintrag = PflanzplanEintrag.objects.create(
            sorte=self.sorte,
            jahr=2025,
            aussaatdatum=date(2025, 3, 15),
            anzahl_samen=5,
            art_der_aussaat='ANZUCHT'
        )
        self.assertEqual(eintrag.sorte, self.sorte)
        self.assertEqual(eintrag.jahr, 2025)
        self.assertEqual(str(eintrag), "Harzfeuer — 2025 (2025-03-15)")

class APITests(TestCase):
    def test_api_endpoints(self):
        """Test that API endpoints are reachable"""
        from rest_framework.test import APIClient
        client = APIClient()
        
        endpoints = ['/api/sorten/', '/api/kategorien/', '/api/arten/', '/api/pflanzplan/']
        for endpoint in endpoints:
            response = client.get(endpoint)
            self.assertEqual(response.status_code, 200, f"Endpoint {endpoint} failed")

class FrontendTests(TestCase):
    def test_frontend_pages(self):
        """Test that frontend pages are reachable"""
        from django.test import Client
        client = Client()
        
        pages = ['/', '/sorten/', '/pflanzplan/']
        for page in pages:
            response = client.get(page)
            self.assertEqual(response.status_code, 200, f"Page {page} failed")

class DataEntryTests(TestCase):
    def setUp(self):
        self.kategorie = Kategorie.objects.create(name="Gemüse")
        self.art = Art.objects.create(name="Tomate")
        self.sorte = Sorte.objects.create(
            name="Harzfeuer",
            kategorie=self.kategorie,
            art=self.art,
            bestand=10,
            einheit='ANZ'
        )

    def test_sorte_create_view(self):
        """Test creating a new Sorte via the view"""
        from django.test import Client
        client = Client()
        
        data = {
            'name': 'Neue Sorte',
            'kategorie': self.kategorie.id,
            'art': self.art.id,
            'bestand': 5,
            'einheit': 'ANZ'
        }
        response = client.post('/sorten/neu/', data)
        self.assertEqual(response.status_code, 302) # Redirect after success
        self.assertTrue(Sorte.objects.filter(name='Neue Sorte').exists())

    def test_pflanzplan_create_view(self):
        """Test creating a new PflanzplanEintrag via the view"""
        from django.test import Client
        client = Client()
        
        data = {
            'sorte': self.sorte.id,
            'jahr': 2026,
            'aussaatdatum': '2026-04-01',
            'anzahl_samen': 10,
            'art_der_aussaat': 'ANZUCHT',
            'anzuchtgefaess': 'Topf'
        }
        response = client.post('/pflanzplan/neu/', data)
        self.assertEqual(response.status_code, 302) # Redirect after success
        self.assertTrue(PflanzplanEintrag.objects.filter(jahr=2026).exists())

    def test_form_rendering(self):
        """Test that form labels are rendered correctly (not as {{ field.label }})"""
        from django.test import Client
        client = Client()
        
        response = client.get('/sorten/neu/')
        self.assertEqual(response.status_code, 200)
        # Check that the literal template tag is NOT present (this was the bug)
        self.assertNotContains(response, '{{ field.label }}')
        
        # Check that the label is rendered (allowing for potential whitespace or attributes)
        self.assertContains(response, 'Name')
        self.assertContains(response, '<label for="id_name"')

class FilterTests(TestCase):
    def setUp(self):
        self.kategorie_gemuese = Kategorie.objects.create(name="Gemüse")
        self.kategorie_obst = Kategorie.objects.create(name="Obst")
        
        self.art_tomate = Art.objects.create(name="Tomate")
        self.art_apfel = Art.objects.create(name="Apfel")
        
        self.sorte_harzfeuer = Sorte.objects.create(name="Harzfeuer", kategorie=self.kategorie_gemuese, art=self.art_tomate)
        self.sorte_boskoop = Sorte.objects.create(name="Boskoop", kategorie=self.kategorie_obst, art=self.art_apfel)
        
        PflanzplanEintrag.objects.create(sorte=self.sorte_harzfeuer, jahr=2025, aussaatdatum='2025-03-15', anzahl_samen=5, art_der_aussaat='ANZUCHT')
        PflanzplanEintrag.objects.create(sorte=self.sorte_boskoop, jahr=2024, aussaatdatum='2024-04-01', anzahl_samen=1, art_der_aussaat='FREILAND')

    def test_filter_jahr(self):
        client = Client()
        response = client.get('/pflanzplan/?jahr=2025')
        self.assertEqual(len(response.context['pflanzplaene']), 1)
        self.assertEqual(response.context['pflanzplaene'][0].sorte.name, 'Harzfeuer')

    def test_filter_kategorie(self):
        client = Client()
        response = client.get(f'/pflanzplan/?kategorie={self.kategorie_obst.id}')
        self.assertEqual(len(response.context['pflanzplaene']), 1)
        self.assertEqual(response.context['pflanzplaene'][0].sorte.name, 'Boskoop')

    def test_filter_sorte(self):
        client = Client()
        response = client.get(f'/pflanzplan/?sorte={self.sorte_harzfeuer.id}')
        self.assertEqual(len(response.context['pflanzplaene']), 1)
        self.assertEqual(response.context['pflanzplaene'][0].sorte.name, 'Harzfeuer')

class SorteFilterTests(TestCase):
    def setUp(self):
        self.kategorie_gemuese = Kategorie.objects.create(name="Gemüse")
        self.kategorie_obst = Kategorie.objects.create(name="Obst")
        
        self.art_tomate = Art.objects.create(name="Tomate")
        self.art_apfel = Art.objects.create(name="Apfel")
        
        self.sorte_harzfeuer = Sorte.objects.create(name="Harzfeuer", kategorie=self.kategorie_gemuese, art=self.art_tomate)
        self.sorte_boskoop = Sorte.objects.create(name="Boskoop", kategorie=self.kategorie_obst, art=self.art_apfel)

    def test_filter_sorte_by_kategorie(self):
        client = Client()
        response = client.get(f'/sorten/?kategorie={self.kategorie_gemuese.id}')
        self.assertEqual(len(response.context['sorten']), 1)
        self.assertEqual(response.context['sorten'][0].name, 'Harzfeuer')

        response = client.get(f'/sorten/?kategorie={self.kategorie_obst.id}')
        self.assertEqual(len(response.context['sorten']), 1)
        self.assertEqual(response.context['sorten'][0].name, 'Boskoop')
