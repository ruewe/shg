# ...existing code...
import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from garten.models import Sorte
import datetime
import locale
locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")

def extract_months(date_range_str: str):
    cleaned = date_range_str.strip()

    if "→" in cleaned:
        parts = [p.strip() for p in cleaned.split("→")]
        if len(parts) != 2:
            raise ValueError("Unerwartetes Format. Erwartet: 'Datum → Datum'.")
        start_str, end_str = parts
    else:
        start_str = cleaned
        end_str = cleaned

    def parse_date(date_str):
        try:
            return datetime.datetime.strptime(date_str, "%d. %B %Y")
        except ValueError:
            return datetime.datetime.strptime("31. Dezember 2000", "%d. %B %Y")

    start_date = parse_date(start_str)
    end_date = parse_date(end_str)

    return start_date.month, end_date.month

def parse_bestand(bestand_str):
    # Akzeptiert None, leere Strings, Zahlen, Strings mit Komma- oder Punkt-Trennungen
    if bestand_str is None or bestand_str == "":
        return 0.0
    if isinstance(bestand_str, (int, float)):
        return float(bestand_str)

    s = str(bestand_str).strip()
    # Entferne Leerzeichen und NBSP
    s = s.replace(" ", "").replace("\u00A0", "")

    # Umgang mit deutscher Schreibweise "1.234,56" oder "1,23"
    if "," in s:
        if "." in s:
            # Punkt als Tausendertrenner -> entfernen
            s = s.replace(".", "")
        # Komma als Dezimaltrenner -> ersetzen
        s = s.replace(",", ".")
    # Jetzt sollte s mit '.' als decimal sein
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0

def parse_einheit(einheit_str):
    if (einheit_str.strip() == "g"):
        einheit_str = "G"
    if (einheit_str.strip() == "k"):
        einheit_str = "ANZ"
    valid_units = ['ANZ', 'G']
    if einheit_str in valid_units:
        return einheit_str
    return 'ANZ'

def fix_info_url(url):
    if not url:
        return ""
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        return ""
    if len(url) > 200:
        return ""
    return url

class Command(BaseCommand):
    help = "Importiert Sorte.json in die DB"

    def handle(self, *args, **options):
        # Debug-Ausgaben, um sicherzustellen, dass handle() läuft
        self.stdout.write("json2dbjson: handle() gestartet")
        self.stdout.write(f"BASE_DIR={settings.BASE_DIR}")

        path = os.path.join(settings.BASE_DIR, "garten", "management", "commands", "Sorte.json")
        self.stdout.write(f"Verwender Pfad: {path}")

        if not os.path.exists(path):
            self.stderr.write(f"Sorte.json nicht gefunden: {path}")
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
            aussaat_start_monat, aussaat_end_monat = extract_months(item.get("Anzucht", ""))
            """
            self.stdout.write(f"Sorte: {name}")
            self.stdout.write(f"Kategorie: {item.get('Kategorie', '')}")
            self.stdout.write(f"Art: {item.get('Art', '')}")
            self.stdout.write(f"Aussaat Monate: {aussaat_start_monat} bis {aussaat_end_monat}")
            self.stdout.write(f"URL: {item.get('URL', '')}")
            self.stdout.write(f"Bestand: {item.get('Bestand', 0)}")
            self.stdout.write(f"Einheit: {item.get('Einheit', 'ANZ')}")
            self.stdout.write("----")
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
