from django.db import models

# Create your models here.
# Datei: garten/models.py

class Kategorie(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Kategorie'
        verbose_name_plural = 'Kategorien'
        ordering = ['name']

    def __str__(self):
        return self.name


class Art(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Art'
        verbose_name_plural = 'Arten'
        ordering = ['name']

    def __str__(self):
        return self.name


class Sorte(models.Model):
    EINHEITEN = [
        ('ANZ', 'Anzahl'),
        ('G', 'g'),
    ]

    name = models.CharField(max_length=200)
    kategorie = models.ForeignKey(Kategorie, on_delete=models.PROTECT, related_name='sorten', null=True, blank=True)
    art = models.ForeignKey(Art, on_delete=models.PROTECT, null=True, blank=True, related_name='sorten')
    aussaat_start_monat = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Monat (1–12)')
    aussaat_end_monat = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Monat (1–12)')
    info_url = models.URLField(blank=True)
    bestand = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    einheit = models.CharField(max_length=10, choices=EINHEITEN, default='ANZ')

    class Meta:
        verbose_name = 'Sorte'
        verbose_name_plural = 'Sorten'
        ordering = ['kategorie', 'name']

    def __str__(self):
        return f"{self.name} ({self.kategorie})"


class PflanzplanEintrag(models.Model):
    AUSSAAT_ART = [
        ('ANZUCHT', 'Anzucht'),
        ('FREILAND', 'Freiland'),
    ]

    sorte = models.ForeignKey(Sorte, on_delete=models.PROTECT, related_name='pflanzplaene')
    jahr = models.PositiveSmallIntegerField(editable=False)
    aussaatdatum = models.DateField()
    anzahl_samen = models.PositiveIntegerField()
    art_der_aussaat = models.CharField(max_length=20, choices=AUSSAAT_ART)
    anzuchtgefaess = models.CharField(max_length=100, blank=True)
    pikierdatum = models.DateField(null=True, blank=True)
    pflanzdatum = models.DateField(null=True, blank=True)
    beschreibung = models.TextField(blank=True)
    
    # GPS Tracking
    latitude = models.DecimalField('Breitengrad', max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField('Längengrad', max_digits=9, decimal_places=6, null=True, blank=True)
    gps_genauigkeit = models.DecimalField('Genauigkeit (m)', max_digits=5, decimal_places=1, null=True, blank=True)

    class Meta:
        verbose_name = 'Pflanzplan-Eintrag'
        verbose_name_plural = 'Pflanzplan-Einträge'
        ordering = ['-jahr', 'aussaatdatum']

    def save(self, *args, **kwargs):
        if self.aussaatdatum:
            self.jahr = self.aussaatdatum.year
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sorte.name} — {self.jahr} ({self.aussaatdatum})"
    