from django.db import models

# Create your models here.

UNIT_CHOICES = [
    ('pcs', 'Stück'),
    ('g', 'g'),
    ('kg', 'kg'),
]

AUSSAAT_ART = [
    ('anzucht', 'Anzucht'),
    ('freiland', 'Freiland'),
    ('direktsaat', 'Direktsaat'),
]

class Sorte(models.Model):
    name = models.CharField(max_length=200)
    kategorie = models.CharField(max_length=100, blank=True)
    art = models.CharField(max_length=100, blank=True)
    aussaatzeitraum = models.CharField(max_length=100, blank=True)  # z.B. "März-April"
    beschreibung_url = models.URLField(blank=True, null=True)
    bestand_menge = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    bestand_einheit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    notizen = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.kategorie})"

class Pflanzplan(models.Model):
    sorte = models.ForeignKey(Sorte, on_delete=models.CASCADE, related_name='pflanzplaene')
    jahr = models.PositiveSmallIntegerField()
    aussaat_datum = models.DateField(null=True, blank=True)
    aussaat_anzahl = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    aussaat_einheit = models.CharField(max_length=10, choices=UNIT_CHOICES, blank=True)
    aussaat_art = models.CharField(max_length=20, choices=AUSSAAT_ART, blank=True)
    anzuchtgefaess = models.CharField(max_length=100, blank=True)
    pikiert_datum = models.DateField(null=True, blank=True)
    pflanz_datum = models.DateField(null=True, blank=True)
    ernte_beschreibung = models.TextField(blank=True)
    erstellt_am = models.DateTimeField(auto_now_add=True)
    aktualisiert_am = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['jahr']),
        ]

    def __str__(self):
        return f"{self.sorte.name} {self.jahr} {self.aussaat_datum or ''}"
