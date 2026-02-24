from django import forms
from .models import Sorte, PflanzplanEintrag, Kategorie, Art

class KategorieForm(forms.ModelForm):
    class Meta:
        model = Kategorie
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ArtForm(forms.ModelForm):
    class Meta:
        model = Art
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SorteForm(forms.ModelForm):
    class Meta:
        model = Sorte
        fields = ['name', 'kategorie', 'art', 'bestand', 'einheit', 'info_url', 'aussaat_start_monat', 'aussaat_end_monat']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'kategorie': forms.Select(attrs={'class': 'form-control'}),
            'art': forms.Select(attrs={'class': 'form-control'}),
            'bestand': forms.NumberInput(attrs={'class': 'form-control'}),
            'einheit': forms.Select(attrs={'class': 'form-control'}),
            'info_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'aussaat_start_monat': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'aussaat_end_monat': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
        }

class PflanzplanForm(forms.ModelForm):
    class Meta:
        model = PflanzplanEintrag
        fields = ['sorte', 'aussaatdatum', 'anzahl_samen', 'art_der_aussaat', 'anzuchtgefaess']
        widgets = {
            'sorte': forms.Select(attrs={'class': 'form-control'}),
            'aussaatdatum': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'anzahl_samen': forms.NumberInput(attrs={'class': 'form-control'}),
            'art_der_aussaat': forms.Select(attrs={'class': 'form-control'}),
            'anzuchtgefaess': forms.TextInput(attrs={'class': 'form-control'}),
        }
