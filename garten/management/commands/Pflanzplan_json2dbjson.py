# ...existing code...
import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from garten.models import Sorte, PflanzplanEintrag
import datetime
import locale
locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")

def parse_einheit(einheit_str):
    if (einheit_str.strip() == "g"):
        einheit_str = "G"
    if (einheit_str.strip() == "k"):
        einheit_str = "ANZ"
    valid_units = ['ANZ', 'G']
    if einheit_str in valid_units:
        return einheit_str
    return 'ANZ'

def query_sorte_by_name(name):
    try:
        return Sorte.objects.filter(name=name).first().id
        
    except Exception as e:
        return None

def extract_sorte(beschreibung: str):
    cleaned = beschreibung.strip()
    name = cleaned.split("(")[0].strip() 
    return name

def parse_art_der_aussaat(art_der_aussaat_str):
    if (art_der_aussaat_str.strip() == "Anzucht"):
        art_der_aussaat_str = "ANZUCHT"
    if (art_der_aussaat_str.strip() == "Freiland"):
        art_der_aussaat_str = "FREILAND"
    valid_units = ['ANZUCHT', 'FREILAND']
    if art_der_aussaat_str in valid_units:
        return art_der_aussaat_str
    return 'ANZUCHT'

class Command(BaseCommand):
    help = "Importiert Sorte.json in die DB"

    def handle(self, *args, **options):
        # Debug-Ausgaben, um sicherzustellen, dass handle() läuft
        self.stdout.write("json2dbjson: handle() gestartet")
        self.stdout.write(f"BASE_DIR={settings.BASE_DIR}")

        path = os.path.join(settings.BASE_DIR, "garten", "management", "commands", "Pflanzplan_2025.json")
        self.stdout.write(f"Verwender Pfad: {path}")

        if not os.path.exists(path):
            self.stderr.write(f"Pflanzplan_2025.json nicht gefunden: {path}")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(f"Fehler beim Laden der JSON-Datei: {e}")
            return

        for item in data:
            name = item.get("Name")
            if not name:
                self.stderr.write("Ein Eintrag ohne 'name' übersprungen")
                continue
            try:
                PflanzplanEintrag.objects.create(
                    sorte_id=query_sorte_by_name(extract_sorte(item.get("Sorten", ""))),
                    jahr=2025,
                    aussaatdatum=datetime.datetime.strptime(item.get("Aussaat", ""), "%d. %B %Y").date(),
                    anzahl_samen=int(item.get("Anzahl", "")) if item.get("Anzahl", "").isdigit() else 0,
                    art_der_aussaat=parse_art_der_aussaat(item.get("wie?", "")),
                    anzuchtgefaess=item.get("wo?", ""),
                    pikierdatum=datetime.datetime.strptime(item.get("pikiert", ""), "%d. %B %Y").date() if item.get("pikiert", "") else None,
                    beschreibung=item.get("Sorten", "")
                )
                self.stdout.write(f"PflanzplanEintrag für Sorte '{extract_sorte(item.get('Sorten'))}' erfolgreich erstellt.")

            except Exception as e:
                self.stderr.write(f"Fehler beim Verarbeiten des Eintrags '{extract_sorte(item.get('Sorten'))}': {e}")

            """
                self.stdout.write(f"sorte: {name}")
                self.stdout.write(f"id: {item.get('ID', '')}")
                self.stdout.write(f"jahr: 2025")
                self.stdout.write(f"aussaatdatum: {item.get('Aussaat', '')}")
                self.stdout.write(f"anzahl_samen: {item.get('Anzahl', '')}")
                self.stdout.write(f"art_der_aussaat: {item.get('wie?', '')}")
                self.stdout.write(f"anzuchtgefaess: {item.get('wo?', '')}")
                self.stdout.write(f"pikierdatum: {item.get('pikiert', '')}")
                #self.stdout.write(f"pflanzdatum: {item.get('Pflanzdatum', '')}")
                beschreibung = item.get("Sorten", "")
                self.stdout.write(f"beschreibung: {beschreibung}")
                self.stdout.write(extract_sorte(beschreibung))
                self.stdout.write(f'Sorte: {query_sorte_by_name(extract_sorte(beschreibung))}')
                self.stdout.write("----")
            """
            """    
            try:
                Sorte.objects.create(
                    name=name,
                    kategorie=item.get("Kategorie", ""),
                    art=item.get("Art", ""),
                    aussaat_start_monat=aussaat_start_monat,
                    aussaat_end_monat=aussaat_end_monat,
                    info_url=fix_info_url(item.get("URL", "")),
                    bestand=parse_bestand(item.get("Bestand", 0)),
                    einheit=parse_einheit(item.get("Einheit", "ANZ"))
                )
                self.stdout.write(f"Sorte '{name}' erfolgreich erstellt.")
            except Exception as e:
                self.stderr.write(f"Fehler beim Erstellen der Sorte '{name}': {e}")
            """
