from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SorteViewSet, KategorieViewSet, ArtViewSet, PflanzplanEintragViewSet, index, sorte_list, pflanzplan_list, sorte_create, pflanzplan_create

router = DefaultRouter()
router.register(r'sorten', SorteViewSet)
router.register(r'kategorien', KategorieViewSet)
router.register(r'arten', ArtViewSet)
router.register(r'pflanzplan', PflanzplanEintragViewSet)

urlpatterns = [
    path('', index, name='index'),
    path('sorten/', sorte_list, name='sorte_list'),
    path('sorten/neu/', sorte_create, name='sorte_create'),
    path('pflanzplan/', pflanzplan_list, name='pflanzplan_list'),
    path('pflanzplan/neu/', pflanzplan_create, name='pflanzplan_create'),
    path('api/', include(router.urls)),
]
