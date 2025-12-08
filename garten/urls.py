from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SorteViewSet, KategorieViewSet, ArtViewSet, PflanzplanEintragViewSet, 
    index, sorte_list, pflanzplan_list, sorte_create, pflanzplan_create, 
    kategorie_create, art_create,
    kategorie_list, kategorie_update, kategorie_delete,
    art_list, art_update, art_delete,
    sorte_update, sorte_delete,
    pflanzplan_delete
)

router = DefaultRouter()
router.register(r'sorten', SorteViewSet)
router.register(r'kategorien', KategorieViewSet)
router.register(r'arten', ArtViewSet)
router.register(r'pflanzplan', PflanzplanEintragViewSet)

urlpatterns = [
    path('', index, name='index'),
    
    path('sorten/', sorte_list, name='sorte_list'),
    path('sorten/neu/', sorte_create, name='sorte_create'),
    path('sorten/<int:pk>/bearbeiten/', sorte_update, name='sorte_update'),
    path('sorten/<int:pk>/loeschen/', sorte_delete, name='sorte_delete'),
    
    path('kategorien/', kategorie_list, name='kategorie_list'),
    path('kategorien/neu/', kategorie_create, name='kategorie_create'),
    path('kategorien/<int:pk>/bearbeiten/', kategorie_update, name='kategorie_update'),
    path('kategorien/<int:pk>/loeschen/', kategorie_delete, name='kategorie_delete'),
    
    path('arten/', art_list, name='art_list'),
    path('arten/neu/', art_create, name='art_create'),
    path('arten/<int:pk>/bearbeiten/', art_update, name='art_update'),
    path('arten/<int:pk>/loeschen/', art_delete, name='art_delete'),
    
    path('pflanzplan/', pflanzplan_list, name='pflanzplan_list'),
    path('pflanzplan/neu/', pflanzplan_create, name='pflanzplan_create'),
    path('pflanzplan/<int:pk>/loeschen/', pflanzplan_delete, name='pflanzplan_delete'),
    
    path('api/', include(router.urls)),
]
