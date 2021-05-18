from django.shortcuts import render
from rest_framework import viewsets
from .serializers import IngredientSerializer, UnitSerializer, CategorySerializer
from .models import Ingredient, Unit, Category


class IngredientView(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class UnitView(viewsets.ModelViewSet):
    serializer_class = UnitSerializer
    queryset = Unit.objects.all()


class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
