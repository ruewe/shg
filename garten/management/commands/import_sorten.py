import os
import json
import datetime
import locale
from django.core.management.base import BaseCommand
from django.conf import settings
from garten.models import Sorte, Kategorie, Art

# Versuche Locale zu setzen, Fallback auf Dictionary falls nicht vorhanden
try:
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
except locale.Error:
    pass

GERMAN_MONTHS = {
    "Januar": 1, "Februar": 2, "März": 3, "April": 4, "Mai": 5, "Juni": 6,
    "Juli": 7, "August": 8, "September": 9, "Oktober": 10, "November": 11, "Dezember": 12
}

def parse_german_date(date_str):
    """Parses '15. Februar 2025' manually to avoid locale dependency issues."""
    try:
        parts = date_str.split(" ")
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

def extract_months(date_range_str: str):
    cleaned = date_range_str.strip()
    if not cleaned:
        return None, None

    if "→" in cleaned:
        parts = [p.strip() for p in cleaned.split("→")]
        if len(parts) != 2:
            return None, None
        start_str, end_str = parts
    else:
        start_str = cleaned
        end_str = cleaned

    start_date = parse_german_date(start_str)
    end_date = parse_german_date(end_str)

    s_mon = start_date.month if start_date else None
    e_mon = end_date.month if end_date else None
    return s_mon, e_mon

def parse_bestand(bestand_str):
    if bestand_str is None or bestand_str == "":
        return 0.0
    if isinstance(bestand_str, (int, float)):
        return float(bestand_str)

    s = str(bestand_str).strip()
    s = s.replace(" ", "").replace("\u00A0", "")
    if "," in s:
        if "." in s:
            s = s.replace(".", "")
        s = s.replace(",", ".")
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0

def parse_einheit(einheit_str):
    s = einheit_str.strip()
    if s == "g": return "G"
    if s == "k": return "ANZ" # Assuming 'k' meant Korn/Anzahl based on previous script context? Standard is usually ANZ
    valid_units = ['ANZ', 'G']
    if s in valid_units:
        return s
    return 'ANZ'

class Command(BaseCommand):
    help = "Importiert Sorte.json in die DB (Erstellt Kategorien und Arten automatisch)"

    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, "garten", "management", "commands", "Sorte.json")
        
        if not os.path.exists(path):
            self.stderr.write(f"Datei nicht gefunden: {path}")
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        count_created = 0
        count_updated = 0

        for item in data:
            name = item.get("Name")
            if not name:
                continue

            # 1. Kategorie behandeln
            kat_name = item.get("Kategorie", "").strip()
            kategorie = None
            if kat_name:
                kategorie, _ = Kategorie.objects.get_or_create(name=kat_name)

            # 2. Art behandeln
            art_name = item.get("Art", "").strip()
            art = None
            if art_name:
                art, _ = Art.objects.get_or_create(name=art_name)

            # 3. Restliche Daten parsen
            start_mon, end_mon = extract_months(item.get("Anzucht", ""))
            
            # Sorte erstellen oder aktualisieren
            # Wir nutzen Kategorie als Teil der Identität, falls Namen doppelt sind in versch. Kategorien?
            # Model Sorte: name is NOT unique. But usually name should be unique identifier.
            # We assume Name is unique enough for update lookup.
            
            # Falls Kategorie zwingend ist (Model: on_delete=PROTECT, null=False - laut models.py von user)
            if not kategorie:
                self.stderr.write(f"Überspringe '{name}': Keine Kategorie angegeben.")
                continue

            defaults = {
                'kategorie': kategorie,
                'art': art,
                'aussaat_start_monat': start_mon,
                'aussaat_end_monat': end_mon,
                'info_url': item.get("URL", "")[:200], # Truncate if too long
                'bestand': parse_bestand(item.get("Bestand", 0)),
                'einheit': parse_einheit(item.get("Einheit", "ANZ")),
            }

            obj, created = Sorte.objects.update_or_create(
                name=name,
                defaults=defaults
            )

            if created:
                count_created += 1
            else:
                count_updated += 1
                
        self.stdout.write(self.style.SUCCESS(f"Import fertig: {count_created} erstellt, {count_updated} aktualisiert."))
