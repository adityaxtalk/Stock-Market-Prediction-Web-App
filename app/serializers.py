from rest_framework import serializers
from app.models import Stock

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model= Stock
        fields=['id','title','start-date','end-date','position','profit']