from rest_framework import serializers
from .models import Sorte, Kategorie, Art, PflanzplanEintrag

class KategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kategorie
        fields = '__all__'

class ArtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Art
        fields = '__all__'

class SorteSerializer(serializers.ModelSerializer):
    kategorie_name = serializers.ReadOnlyField(source='kategorie.name')
    art_name = serializers.ReadOnlyField(source='art.name')

    class Meta:
        model = Sorte
        fields = '__all__'

class PflanzplanEintragSerializer(serializers.ModelSerializer):
    sorte_name = serializers.ReadOnlyField(source='sorte.name')

    class Meta:
        model = PflanzplanEintrag
        fields = '__all__'
