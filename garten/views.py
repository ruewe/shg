from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from .models import Sorte, Kategorie, Art, PflanzplanEintrag
from .serializers import SorteSerializer, KategorieSerializer, ArtSerializer, PflanzplanEintragSerializer
from .forms import SorteForm, PflanzplanForm, KategorieForm, ArtForm
import sys
import traceback

def index(request):
    context = {
        'sorten_count': Sorte.objects.count(),
        'pflanzplan_count': PflanzplanEintrag.objects.count(),
    }
    return render(request, 'garten/index.html', context)

def sorte_list(request):
    try:
        queryset = Sorte.objects.all().select_related('kategorie', 'art')
        
        kategorie_id = request.GET.get('kategorie')
        if kategorie_id:
            queryset = queryset.filter(kategorie_id=kategorie_id)

        art_id = request.GET.get('art')
        if art_id:
            queryset = queryset.filter(art_id=art_id)
            
        kategorien = Kategorie.objects.all()
        arten = Art.objects.all()
        
        context = {
            'sorten': queryset,
            'kategorien': kategorien,
            'arten': arten,
            'selected_kategorie': int(kategorie_id) if kategorie_id else None,
            'selected_art': int(art_id) if art_id else None,
        }
        return render(request, 'garten/sorte_list.html', context)
    except Exception:
        print("!!! CRITICAL ERROR IN SORTE_LIST !!!", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise

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

def kategorie_create(request):
    if request.method == 'POST':
        form = KategorieForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = KategorieForm()
    return render(request, 'garten/kategorie_form.html', {'form': form})

def art_create(request):
    if request.method == 'POST':
        form = ArtForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ArtForm()
    return render(request, 'garten/art_form.html', {'form': form})

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

def kategorie_list(request):
    kategorien = Kategorie.objects.all()
    return render(request, 'garten/kategorie_list.html', {'kategorien': kategorien})

def kategorie_update(request, pk):
    kategorie = get_object_or_404(Kategorie, pk=pk)
    if request.method == 'POST':
        form = KategorieForm(request.POST, instance=kategorie)
        if form.is_valid():
            form.save()
            return redirect('kategorie_list')
    else:
        form = KategorieForm(instance=kategorie)
    return render(request, 'garten/kategorie_form.html', {'form': form})

def kategorie_delete(request, pk):
    kategorie = get_object_or_404(Kategorie, pk=pk)
    if request.method == 'POST':
        kategorie.delete()
        return redirect('kategorie_list')
    return render(request, 'garten/confirm_delete.html', {'object': kategorie, 'type': 'Kategorie'})

def art_list(request):
    arten = Art.objects.all()
    return render(request, 'garten/art_list.html', {'arten': arten})

def art_update(request, pk):
    art = get_object_or_404(Art, pk=pk)
    if request.method == 'POST':
        form = ArtForm(request.POST, instance=art)
        if form.is_valid():
            form.save()
            return redirect('art_list')
    else:
        form = ArtForm(instance=art)
    return render(request, 'garten/art_form.html', {'form': form})

def art_delete(request, pk):
    art = get_object_or_404(Art, pk=pk)
    if request.method == 'POST':
        art.delete()
        return redirect('art_list')
    return render(request, 'garten/confirm_delete.html', {'object': art, 'type': 'Art'})

def sorte_update(request, pk):
    sorte = get_object_or_404(Sorte, pk=pk)
    if request.method == 'POST':
        form = SorteForm(request.POST, instance=sorte)
        if form.is_valid():
            form.save()
            return redirect('sorte_list')
    else:
        form = SorteForm(instance=sorte)
    return render(request, 'garten/sorte_form.html', {'form': form})

def sorte_delete(request, pk):
    sorte = get_object_or_404(Sorte, pk=pk)
    if request.method == 'POST':
        sorte.delete()
        return redirect('sorte_list')
    return render(request, 'garten/confirm_delete.html', {'object': sorte, 'type': 'Sorte'})

def pflanzplan_delete(request, pk):
    eintrag = get_object_or_404(PflanzplanEintrag, pk=pk)
    if request.method == 'POST':
        eintrag.delete()
        return redirect('pflanzplan_list')
    return render(request, 'garten/confirm_delete.html', {'object': eintrag, 'type': 'Pflanzplan-Eintrag'})
