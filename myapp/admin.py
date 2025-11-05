from django.contrib import admin

# Register your models here.
from .models import Sorte, Pflanzplan

class PflanzplanInline(admin.TabularInline):
    model = Pflanzplan
    extra = 1

@admin.register(Sorte)
class SorteAdmin(admin.ModelAdmin):
    list_display = ('name', 'kategorie', 'bestand_menge', 'bestand_einheit')
    search_fields = ('name', 'kategorie', 'art')
    inlines = [PflanzplanInline]

@admin.register(Pflanzplan)
class PflanzplanAdmin(admin.ModelAdmin):
    list_display = ('sorte', 'jahr', 'aussaat_datum', 'aussaat_anzahl', 'aussaat_art')
    list_filter = ('jahr','aussaat_art')
    search_fields = ('sorte__name',)