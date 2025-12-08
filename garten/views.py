from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import Sorte, Kategorie, Art, PflanzplanEintrag
from .serializers import SorteSerializer, KategorieSerializer, ArtSerializer, PflanzplanEintragSerializer
from .forms import SorteForm, PflanzplanForm

def index(request):
    context = {
        'sorten_count': Sorte.objects.count(),
        'pflanzplan_count': PflanzplanEintrag.objects.count(),
    }
    return render(request, 'garten/index.html', context)

def sorte_list(request):
    sorten = Sorte.objects.all().select_related('kategorie', 'art')
    return render(request, 'garten/sorte_list.html', {'sorten': sorten})

def sorte_create(request):
    if request.method == 'POST':
        form = SorteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sorte_list')
    else:
        form = SorteForm()
    return render(request, 'garten/sorte_form.html', {'form': form})

def pflanzplan_list(request):
    # Base QuerySet
    queryset = PflanzplanEintrag.objects.all().select_related('sorte', 'sorte__kategorie')

    # Filtering
    jahr = request.GET.get('jahr')
    kategorie_id = request.GET.get('kategorie')
    sorte_id = request.GET.get('sorte')

    if jahr:
        queryset = queryset.filter(jahr=jahr)
    if kategorie_id:
        queryset = queryset.filter(sorte__kategorie_id=kategorie_id)
    if sorte_id:
        queryset = queryset.filter(sorte_id=sorte_id)

    # Sorting
    sort_by = request.GET.get('sort', '-jahr') # Default sort
    if sort_by in ['jahr', '-jahr', 'sorte__name', '-sorte__name', 'sorte__kategorie__name', '-sorte__kategorie__name', 'aussaatdatum', '-aussaatdatum']:
        queryset = queryset.order_by(sort_by)
    else:
        queryset = queryset.order_by('-jahr', 'aussaatdatum')

    # Context Data for Filters
    jahre = PflanzplanEintrag.objects.values_list('jahr', flat=True).distinct().order_by('-jahr')
    kategorien = Kategorie.objects.all()
    sorten = Sorte.objects.all()

    context = {
        'pflanzplaene': queryset,
        'jahre': jahre,
        'kategorien': kategorien,
        'sorten': sorten,
        'selected_jahr': int(jahr) if jahr else None,
        'selected_kategorie': int(kategorie_id) if kategorie_id else None,
        'selected_sorte': int(sorte_id) if sorte_id else None,
    }
    return render(request, 'garten/pflanzplan_list.html', context)

def pflanzplan_create(request):
    if request.method == 'POST':
        form = PflanzplanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pflanzplan_list')
    else:
        form = PflanzplanForm()
    return render(request, 'garten/pflanzplan_form.html', {'form': form})

class KategorieViewSet(viewsets.ModelViewSet):
    queryset = Kategorie.objects.all()
    serializer_class = KategorieSerializer

class ArtViewSet(viewsets.ModelViewSet):
    queryset = Art.objects.all()
    serializer_class = ArtSerializer

class SorteViewSet(viewsets.ModelViewSet):
    queryset = Sorte.objects.all()
    serializer_class = SorteSerializer

class PflanzplanEintragViewSet(viewsets.ModelViewSet):
    queryset = PflanzplanEintrag.objects.all()
    serializer_class = PflanzplanEintragSerializer
