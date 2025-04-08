from rest_framework import serializers
from .models import form
class formSerializer(serializers.ModelSerializer):
    class Meta:
        model = form
        fields = '__all__'
