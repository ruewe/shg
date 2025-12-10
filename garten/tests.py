from django.test import TestCase, Client
from django.urls import reverse
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
        response = self.client.post('/sorten/neu/', data)
        self.assertEqual(response.status_code, 302) # Redirect after success
        self.assertTrue(Sorte.objects.filter(name='Neue Sorte').exists())

    def test_pflanzplan_create_view(self):
        """Test creating a new PflanzplanEintrag via the view"""
        
        data = {
            'sorte': self.sorte.id,
            'jahr': 2026,
            'aussaatdatum': '2026-04-01',
            'anzahl_samen': 10,
            'art_der_aussaat': 'ANZUCHT',
            'anzuchtgefaess': 'Topf'
        }
        response = self.client.post('/pflanzplan/neu/', data)
        self.assertEqual(response.status_code, 302) # Redirect after success
        self.assertTrue(PflanzplanEintrag.objects.filter(jahr=2026).exists())

    def test_pflanzplan_create_post(self):
        sorte = Sorte.objects.create(name="TestSorte", kategorie=self.kategorie, art=self.art)
        response = self.client.post(reverse('pflanzplan_create'), {
            'sorte': sorte.id,
            'jahr': 2025,
            'aussaatdatum': '2025-03-15',
            'anzahl_samen': 10,
            'art_der_aussaat': 'ANZUCHT',
            'anzuchtgefaess': 'Topf'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PflanzplanEintrag.objects.count(), 1)

    def test_kategorie_create_post(self):
        response = self.client.post(reverse('kategorie_create'), {
            'name': 'Neue Kategorie'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Kategorie.objects.filter(name='Neue Kategorie').exists())

    def test_art_create_post(self):
        response = self.client.post(reverse('art_create'), {
            'name': 'Neue Art'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Art.objects.filter(name='Neue Art').exists())

    def test_form_rendering(self):
        """Test that form labels are rendered correctly (not as {{ field.label }})"""
        
        response = self.client.get('/sorten/neu/')
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

    def test_filter_sorte_by_art(self):
        client = Client()
        response = client.get(f'/sorten/?art={self.art_tomate.id}')
        self.assertEqual(len(response.context['sorten']), 1)
        self.assertEqual(response.context['sorten'][0].name, 'Harzfeuer')

        response = client.get(f'/sorten/?art={self.art_apfel.id}')
        self.assertEqual(len(response.context['sorten']), 1)
        self.assertEqual(response.context['sorten'][0].name, 'Boskoop')

class ManagementTests(TestCase):
    def setUp(self):
        self.kategorie = Kategorie.objects.create(name="Gemüse")
        self.art = Art.objects.create(name="Tomate")
        self.sorte = Sorte.objects.create(name="Harzfeuer", kategorie=self.kategorie, art=self.art)

    def test_kategorie_list(self):
        response = self.client.get(reverse('kategorie_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gemüse")

    def test_kategorie_update(self):
        response = self.client.post(reverse('kategorie_update', args=[self.kategorie.id]), {
            'name': 'Gemüse Updated'
        })
        self.assertEqual(response.status_code, 302)
        self.kategorie.refresh_from_db()
        self.assertEqual(self.kategorie.name, 'Gemüse Updated')

    def test_kategorie_delete(self):
        kategorie_to_delete = Kategorie.objects.create(name="To Delete")
        response = self.client.post(reverse('kategorie_delete', args=[kategorie_to_delete.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Kategorie.objects.filter(id=kategorie_to_delete.id).exists())

    def test_art_list(self):
        response = self.client.get(reverse('art_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tomate")

    def test_art_update(self):
        response = self.client.post(reverse('art_update', args=[self.art.id]), {
            'name': 'Tomate Updated'
        })
        self.assertEqual(response.status_code, 302)
        self.art.refresh_from_db()
        self.assertEqual(self.art.name, 'Tomate Updated')

    def test_art_delete(self):
        art_to_delete = Art.objects.create(name="To Delete")
        response = self.client.post(reverse('art_delete', args=[art_to_delete.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Art.objects.filter(id=art_to_delete.id).exists())

    def test_sorte_update(self):
        response = self.client.post(reverse('sorte_update', args=[self.sorte.id]), {
            'name': 'Harzfeuer Updated',
            'kategorie': self.kategorie.id,
            'art': self.art.id,
            'bestand': 20,
            'einheit': 'ANZ'
        })
        self.assertEqual(response.status_code, 302)
        self.sorte.refresh_from_db()
        self.assertEqual(self.sorte.name, 'Harzfeuer Updated')
        self.assertEqual(self.sorte.bestand, 20)

    def test_sorte_delete(self):
        response = self.client.post(reverse('sorte_delete', args=[self.sorte.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Sorte.objects.filter(id=self.sorte.id).exists())

    def test_pflanzplan_delete(self):
        eintrag = PflanzplanEintrag.objects.create(
            sorte=self.sorte,
            jahr=2025,
            aussaatdatum='2025-03-15',
            anzahl_samen=5,
            art_der_aussaat='ANZUCHT'
        )
        response = self.client.post(reverse('pflanzplan_delete', args=[eintrag.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PflanzplanEintrag.objects.filter(id=eintrag.id).exists())

    def test_navigation_links(self):
        """Test that navigation links are present in the response"""
        response = self.client.get('/')
        self.assertContains(response, 'href="/kategorien/"')
        self.assertContains(response, 'href="/arten/"')
