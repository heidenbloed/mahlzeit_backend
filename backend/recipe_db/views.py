from django.shortcuts import render
from rest_framework import viewsets
from .serializers import IngredientSerializer, UnitSerializer, CategorySerializer
from .models import Ingredient, Unit, Category


class IngredientView(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        query_set = Ingredient.objects.filter(user=self.request.user)
        return query_set


class UnitView(viewsets.ModelViewSet):
    serializer_class = UnitSerializer
    queryset = Unit.objects.all()


class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
