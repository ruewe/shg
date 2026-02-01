from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from .models import Sorte, Kategorie, Art, PflanzplanEintrag
from .serializers import SorteSerializer, KategorieSerializer, ArtSerializer, PflanzplanEintragSerializer
from .forms import SorteForm, PflanzplanForm, KategorieForm, ArtForm

@login_required
def index(request):
    context = {
        'sorten_count': Sorte.objects.count(),
        'pflanzplan_count': PflanzplanEintrag.objects.count(),
    }
    return render(request, 'garten/index.html', context)

@login_required
def sorte_list(request):
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

@login_required
def sorte_create(request):
    if request.method == 'POST':
        form = SorteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sorte_list')
    else:
        form = SorteForm()
    return render(request, 'garten/sorte_form.html', {'form': form})

@login_required
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

@login_required
def pflanzplan_create(request):
    if request.method == 'POST':
        form = PflanzplanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pflanzplan_list')
    else:
        form = PflanzplanForm()
    return render(request, 'garten/pflanzplan_form.html', {'form': form})

@login_required
def kategorie_create(request):
    if request.method == 'POST':
        form = KategorieForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = KategorieForm()
    return render(request, 'garten/kategorie_form.html', {'form': form})

@login_required
def art_create(request):
    if request.method == 'POST':
        form = ArtForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ArtForm()
    return render(request, 'garten/art_form.html', {'form': form})

class KategorieViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Kategorie.objects.all()
    serializer_class = KategorieSerializer

class ArtViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Art.objects.all()
    serializer_class = ArtSerializer

class SorteViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Sorte.objects.all()
    serializer_class = SorteSerializer

class PflanzplanEintragViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = PflanzplanEintrag.objects.all()
    serializer_class = PflanzplanEintragSerializer

@login_required
def kategorie_list(request):
    kategorien = Kategorie.objects.all()
    return render(request, 'garten/kategorie_list.html', {'kategorien': kategorien})

@login_required
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

@login_required
def kategorie_delete(request, pk):
    kategorie = get_object_or_404(Kategorie, pk=pk)
    if request.method == 'POST':
        kategorie.delete()
        return redirect('kategorie_list')
    return render(request, 'garten/confirm_delete.html', {'object': kategorie, 'type': 'Kategorie'})

@login_required
def art_list(request):
    arten = Art.objects.all()
    return render(request, 'garten/art_list.html', {'arten': arten})

@login_required
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

@login_required
def art_delete(request, pk):
    art = get_object_or_404(Art, pk=pk)
    if request.method == 'POST':
        art.delete()
        return redirect('art_list')
    return render(request, 'garten/confirm_delete.html', {'object': art, 'type': 'Art'})

@login_required
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

@login_required
def sorte_delete(request, pk):
    sorte = get_object_or_404(Sorte, pk=pk)
    if request.method == 'POST':
        sorte.delete()
        return redirect('sorte_list')
    return render(request, 'garten/confirm_delete.html', {'object': sorte, 'type': 'Sorte'})

@login_required
def pflanzplan_delete(request, pk):
    eintrag = get_object_or_404(PflanzplanEintrag, pk=pk)
    if request.method == 'POST':
        eintrag.delete()
        return redirect('pflanzplan_list')
    return render(request, 'garten/confirm_delete.html', {'object': eintrag, 'type': 'Pflanzplan-Eintrag'})

@login_required
def sorte_analyse(request):
    sorte_query = request.GET.get('lookup_id', '')
    jahr_filter = request.GET.get('jahr', '')
    
    # All varieties for the datalist / dropdown
    alle_sorten = Sorte.objects.all().order_by('name')
    
    # Available years for filtering
    jahre = PflanzplanEintrag.objects.values_list('jahr', flat=True).distinct().order_by('-jahr')
    
    eintraege = []
    selected_sorte = None
    
    if sorte_query:
        # Try to find the exact variety by name
        selected_sorte = Sorte.objects.filter(name=sorte_query).first()
        
        if selected_sorte:
            eintraege = PflanzplanEintrag.objects.filter(sorte=selected_sorte).select_related('sorte', 'sorte__kategorie')
            if jahr_filter:
                eintraege = eintraege.filter(jahr=jahr_filter)
            eintraege = eintraege.order_by('-jahr', '-aussaatdatum')

    context = {
        'alle_sorten': alle_sorten,
        'jahre': jahre,
        'eintraege': eintraege,
        'selected_sorte': selected_sorte,
        'sorte_query': sorte_query,
        'selected_jahr': int(jahr_filter) if jahr_filter else None,
    }
    return render(request, 'garten/sorte_analyse.html', context)
