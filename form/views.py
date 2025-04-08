from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import form
from .serializers import formSerializer

# List all bookings and create a new booking
class formListCreateView(generics.ListCreateAPIView):
    queryset = form.objects.all()
    serializer_class = formSerializer

# Retrieve, update, or delete a specific booking
class formDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = form.objects.all()
    serializer_class = formSerializer
