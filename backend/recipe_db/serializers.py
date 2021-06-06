from rest_framework import serializers
from .models import Recipe, Ingredient, QuantifiedIngredient, IngredientCategory, Unit, Label


class RecipeFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'preparation_time', 'source', 'labels', 'quantified_ingredients')


class RecipeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name')


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'


class IngredientCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientCategory
        fields = '__all__'


class IngredientNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name')


class IngredientFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class QuantifiedIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuantifiedIngredient
        fields = '__all__'


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'
