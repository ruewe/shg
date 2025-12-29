from django.core.management.base import BaseCommand
from django.conf import settings
from garten.models import Sorte
import sys

class Command(BaseCommand):
    help = "Diagnose Script für Server Error"

    def handle(self, *args, **options):
        self.stdout.write(f"--- DIAGNOSE START ---")
        self.stdout.write(f"DEBUG Setting: {settings.DEBUG}")
        
        try:
            # 1. Check Count
            count = Sorte.objects.count()
            self.stdout.write(f"Anzahl Sorten: {count}")

            # 2. Check Data Access (specifically offending columns)
            if count > 0:
                s = Sorte.objects.first()
                self.stdout.write(f"Erste Sorte: {s.name}")
                self.stdout.write(f" - Kategorie: {s.kategorie}")
                self.stdout.write(f" - Info URL: {getattr(s, 'info_url', 'Nicht vorhanden')}")
            
            self.stdout.write(self.style.SUCCESS("Datenbank-Zugriff ERFOLGREICH!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"KRITISCHER FEHLER: {e}"))
            import traceback
            traceback.print_exc()
            
        self.stdout.write(f"--- DIAGNOSE ENDE ---")
