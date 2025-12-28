import os
import json
import datetime
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from garten.models import Sorte, PflanzplanEintrag

GERMAN_MONTHS = {
    "Januar": 1, "Februar": 2, "März": 3, "April": 4, "Mai": 5, "Juni": 6,
    "Juli": 7, "August": 8, "September": 9, "Oktober": 10, "November": 11, "Dezember": 12
}

def parse_german_date(date_str):
    """Parses '15. Februar 2025' manually."""
    if not date_str or not date_str.strip():
        return None
    try:
        parts = date_str.strip().split(" ")
        if len(parts) != 3:
            return None
        day = int(parts[0].replace(".", ""))
        month_name = parts[1]
        year = int(parts[2])
        month = GERMAN_MONTHS.get(month_name)
        if not month:
            return None
        return datetime.date(year, month, day)
    except (ValueError, IndexError):
        return None

def extract_sorte_name(sorte_raw_str):
    """
    Input: "Habanero (https://...)" or "Habanero"
    Output: "Habanero"
    """
    if not sorte_raw_str:
        return None
    # Suche nach Klammer auf
    if "(" in sorte_raw_str:
        return sorte_raw_str.split("(")[0].strip()
    return sorte_raw_str.strip()

class Command(BaseCommand):
    help = "Importiert Pflanzplan_2025.json"

    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, "garten", "management", "commands", "Pflanzplan_2025.json")
        
        if not os.path.exists(path):
            self.stderr.write(f"Datei nicht gefunden: {path}")
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        count_created = 0
        count_skipped = 0

        for item in data:
            # Sorte finden
            sorte_raw = item.get("Sorten", "")
            if not sorte_raw:
                self.stderr.write("Eintrag ohne Sorte übersprungen.")
                count_skipped += 1
                continue
            
            sorte_name = extract_sorte_name(sorte_raw)
            try:
                # Versuche exakten Match
                sorte = Sorte.objects.get(name__iexact=sorte_name)
            except Sorte.DoesNotExist:
                # Fallback: Vielleicht ist der Name Teil eines längeren Namens?
                # Oder wir loggen es nur
                self.stderr.write(f"Sorte nicht gefunden: '{sorte_name}' (Raw: {sorte_raw})")
                count_skipped += 1
                continue
            except Sorte.MultipleObjectsReturned:
                self.stderr.write(f"Mehrere Sorten für '{sorte_name}' gefunden. Nehme die erste.")
                sorte = Sorte.objects.filter(name__iexact=sorte_name).first()

            # Daten parsen
            aussaatdatum = parse_german_date(item.get("Aussaat"))
            # Fallback für Aussaatdatum: Wenn leer, Pflichtfeld -> überspringen?
            if not aussaatdatum:
                 self.stderr.write(f"Kein gültiges Aussaatdatum bei {sorte_name}. Überspringe.")
                 count_skipped += 1
                 continue

            jahr = aussaatdatum.year
            
            # Anzucht vs Freiland
            wie = item.get("wie?", "").lower()
            art_der_aussaat = 'ANZUCHT' # Default
            if 'freiland' in wie:
                art_der_aussaat = 'FREILAND'

            # Anzahl
            anz_str = str(item.get("Anzahl", "0")).strip()
            if not anz_str: anz_str = "0"
            try:
                anzahl = int(anz_str)
            except ValueError:
                anzahl = 0
            
            pikierdatum = parse_german_date(item.get("pikiert"))
            
            # Pflanzdatum haben wir im JSON nicht direkt, oder? 
            # Im JSON sehe ich kein 'gepflanzt' Feld im User snippet, nur 'pikiert'.
            # Wir lassen pflanzdatum None.

            # Create
            PflanzplanEintrag.objects.get_or_create(
                sorte=sorte,
                jahr=jahr,
                aussaatdatum=aussaatdatum,
                defaults={
                    'anzahl_samen': anzahl,
                    'art_der_aussaat': art_der_aussaat,
                    'anzuchtgefaess': item.get("wo?", "")[:100],
                    'pikierdatum': pikierdatum,
                    'beschreibung': f"Importiert aus JSON. ID: {item.get('ID')}"
                }
            )
            count_created += 1

        self.stdout.write(self.style.SUCCESS(f"Pflanzplan Import fertig: {count_created} Einträge erstellt. {count_skipped} übersprungen."))
