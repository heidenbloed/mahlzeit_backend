from rest_framework import serializers
from .models import Recipe, Ingredient, QuantifiedIngredient, IngredientCategory, Unit, Label, RecipeImage


class TimestampField(serializers.FloatField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, read_only=True)

    def to_internal_value(self, data):
        raise NotImplementedError

    def to_representation(self, value):
        return value.timestamp()


class RecipeFullSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'preparation_time', 'source', 'labels', 'quantified_ingredients', 'recipe_images', 'updated_at')
        read_only_fields = ('updated_at',)


class RecipeNameSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'updated_at')
        read_only_fields = ('updated_at',)


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'


class IngredientCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientCategory
        fields = '__all__'


class IngredientNameSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'updated_at')
        read_only_fields = ('updated_at',)


class IngredientFullSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('updated_at',)


class QuantifiedIngredientSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = QuantifiedIngredient
        fields = '__all__'
        read_only_fields = ('updated_at',)


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'


class RecipeImageSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = RecipeImage
        fields = '__all__'
        read_only_fields = ('updated_at',)
