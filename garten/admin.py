
# Register your models here.
# Datei: garten/admin.py
from django.contrib import admin
from .models import Sorte, PflanzplanEintrag, Kategorie, Art


@admin.register(Kategorie)
class KategorieAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Art)
class ArtAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Sorte)
class SorteAdmin(admin.ModelAdmin):
    list_display = ('name', 'kategorie', 'art', 'bestand', 'einheit', 'info_url')
    search_fields = ('name', 'kategorie__name', 'art__name')
    actions = ['duplicate_sorte']

    def duplicate_sorte(self, request, queryset):
        for obj in queryset:
            new_obj = Sorte.objects.get(pk=obj.pk)
            new_obj.pk = None
            new_obj.name = f"{obj.name} (Kopie)"
            new_obj.save()
        self.message_user(request, f"{queryset.count()} Sorte(n) dupliziert.")
    duplicate_sorte.short_description = "Ausgewählte Sorten duplizieren"

@admin.register(PflanzplanEintrag)
class PflanzplanEintragAdmin(admin.ModelAdmin):
    list_display = ('sorte', 'jahr', 'aussaatdatum', 'anzahl_samen', 'art_der_aussaat')
    list_filter = ('jahr', 'art_der_aussaat')
    search_fields = ('sorte__name',)
    readonly_fields = ('jahr',)
