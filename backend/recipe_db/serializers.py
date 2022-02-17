from rest_framework import serializers
from .models import Recipe, Ingredient, QuantifiedIngredient, IngredientCategory, Unit, Label, RecipeImage, UnitConversion


class TimestampField(serializers.FloatField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, read_only=True)

    def to_internal_value(self, data):
        raise NotImplementedError

    def to_representation(self, value):
        return value.timestamp()


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'
        read_only_fields = ('updated_at',)


class IngredientCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientCategory
        fields = '__all__'
        read_only_fields = ('updated_at',)


class UnitConversionSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()
    alternative_unit = UnitSerializer()

    class Meta:
        model = UnitConversion
        fields = ('id', 'alternative_unit', 'alternative_conversion_factor', 'default_conversion_factor', 'updated_at')
        read_only_fields = ('updated_at',)


class UnitConversionEditSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = UnitConversion
        fields = ('id', 'alternative_unit', 'alternative_conversion_factor', 'default_conversion_factor', 'updated_at',)
        read_only_fields = ('id', 'updated_at',)

    def validate_alternative_conversion_factor(self, data):
        if data <= 0.:
            raise serializers.ValidationError("Must be a positive value.")
        return data

    def validate_default_conversion_factor(self, data):
        if data <= 0.:
            raise serializers.ValidationError("Must be a positive value.")
        return data


class IngredientShortSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'updated_at')
        read_only_fields = ('updated_at',)


class IngredientFullSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()
    default_unit = UnitSerializer()
    category = IngredientCategorySerializer()
    unit_conversions = UnitConversionSerializer(many=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'default_unit', 'category', 'unit_conversions', 'updated_at')
        read_only_fields = ('updated_at',)


class IngredientEditSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()
    unit_conversions = UnitConversionEditSerializer(many=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'default_unit', 'category', 'unit_conversions', 'updated_at',)
        read_only_fields = ('id', 'updated_at',)

    def create(self, validated_data):
        unit_conversions_data = validated_data.pop("unit_conversions")
        ingredient = Ingredient.objects.create(**validated_data)
        for unit_conversion_data in unit_conversions_data:
            UnitConversion.objects.create(ingredient=ingredient, **unit_conversion_data)
        return ingredient

    def validate(self, data):
        print(data)
        units = {data.get("default_unit")}
        for unit_conversion in data.get("unit_conversions"):
            alternative_unit = unit_conversion.get("alternative_unit")
            if unit_conversion.get("alternative_unit") in units:
                raise serializers.ValidationError({"unit_conversions": [{"alternative_unit": "The alternative unit can not be the default unit or any other alternative unit of the ingredient."}]})
            units.add(alternative_unit)
        return data


class QuantifiedIngredientSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()
    ingredient = IngredientShortSerializer()
    unit = UnitSerializer()
    unit_conversion_factor = serializers.ReadOnlyField()

    class Meta:
        model = QuantifiedIngredient
        fields = ('id', 'ingredient', 'quantity', 'unit', 'unit_conversion_factor', 'updated_at')
        read_only_fields = ('unit_conversion_factor', 'updated_at')


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'


class RecipeImageFullSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = RecipeImage
        fields = '__all__'
        read_only_fields = ('updated_at',)


class RecipeImageSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = RecipeImage
        fields = ('id', 'image', 'updated_at')
        read_only_fields = ('updated_at',)


class RecipeImageShortSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = RecipeImage
        fields = ('id', 'image', 'updated_at')
        read_only_fields = ('updated_at',)


class RecipeShortSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()
    first_image = RecipeImageShortSerializer()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'first_image', 'updated_at')
        read_only_fields = ('first_image', 'updated_at',)


class RecipeFullSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()
    quantified_ingredients = QuantifiedIngredientSerializer(many=True)
    labels = LabelSerializer(many=True)
    recipe_images = RecipeImageSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'preparation_time', 'source', 'num_servings', 'labels', 'quantified_ingredients', 'recipe_images', 'updated_at')
        read_only_fields = ('updated_at',)
