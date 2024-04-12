import itertools

from rest_framework import serializers

from .models import (Ingredient, IngredientCategory, Label, PushSubscription,
                     QuantifiedIngredient, Recipe, RecipeImage, Unit,
                     UnitConversion)


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
        fields = "__all__"
        read_only_fields = ("updated_at",)


class IngredientCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientCategory
        fields = "__all__"
        read_only_fields = ("updated_at",)


class UnitConversionSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()
    alternative_unit = UnitSerializer()

    class Meta:
        model = UnitConversion
        fields = (
            "id",
            "alternative_unit",
            "alternative_conversion_factor",
            "default_conversion_factor",
            "updated_at",
        )
        read_only_fields = ("updated_at",)


class UnitConversionEditSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = UnitConversion
        fields = (
            "id",
            "alternative_unit",
            "alternative_conversion_factor",
            "default_conversion_factor",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "updated_at",
        )

    def validate_alternative_conversion_factor(self, data):
        if data <= 0.0:
            raise serializers.ValidationError("Must be a positive value.")
        return data

    def validate_default_conversion_factor(self, data):
        if data <= 0.0:
            raise serializers.ValidationError("Must be a positive value.")
        return data


class IngredientShortSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = Ingredient
        fields = ("id", "name", "updated_at")
        read_only_fields = ("updated_at",)


class IngredientFullSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()
    default_unit = UnitSerializer()
    category = IngredientCategorySerializer()
    unit_conversions = UnitConversionSerializer(many=True)

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "default_unit",
            "category",
            "unit_conversions",
            "updated_at",
        )
        read_only_fields = ("updated_at",)


class IngredientEditSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()
    unit_conversions = UnitConversionEditSerializer(many=True)

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "default_unit",
            "category",
            "unit_conversions",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "updated_at",
        )

    def create(self, validated_data):
        unit_conversions_data = validated_data.pop("unit_conversions")
        ingredient = Ingredient.objects.create(**validated_data)
        for unit_conversion_data in unit_conversions_data:
            UnitConversion.objects.create(ingredient=ingredient, **unit_conversion_data)
        return ingredient

    def validate(self, data):
        units = set()
        new_default_unit = data.get("default_unit")
        if new_default_unit is not None:
            units.add(new_default_unit)
        unit_conversions = data.get("unit_conversions")
        if unit_conversions is not None:
            for unit_conversion_data in unit_conversions:
                alternative_unit = unit_conversion_data.get("alternative_unit")
                if unit_conversion_data.get("alternative_unit") in units:
                    raise serializers.ValidationError(
                        {
                            "unit_conversions": [
                                {
                                    "alternative_unit": "The alternative unit can not be the default unit or any other alternative unit of the ingredient."
                                }
                            ]
                        }
                    )
                units.add(alternative_unit)

        if (
            new_default_unit is not None
            and self.instance is not None
            and new_default_unit != self.instance.default_unit.id
        ):
            if unit_conversions is None:
                raise serializers.ValidationError(
                    {
                        "unit_conversions": "Must be provided when the default unit is updated."
                    }
                )
            for unit_conversion_data in unit_conversions:
                if (
                    unit_conversion_data.get("alternative_unit")
                    == self.instance.default_unit
                ):
                    break
            else:
                raise serializers.ValidationError(
                    {
                        "unit_conversions": "Must contain the conversion from the old default unit to the new default unit."
                    }
                )
        return data

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.category = validated_data.get("category", instance.category)
        new_default_unit = validated_data.get("default_unit")
        unit_conversions = validated_data.get("unit_conversions")
        if new_default_unit is not None and new_default_unit != instance.default_unit:
            new_default_unit_conversion = next(
                unit_conv
                for unit_conv in unit_conversions
                if unit_conv["alternative_unit"] == instance.default_unit
            )
            new_default_unit_conversion_default_factor = new_default_unit_conversion[
                "default_conversion_factor"
            ]
            new_default_unit_conversion_alternative_factor = (
                new_default_unit_conversion["alternative_conversion_factor"]
            )
            for unit_conversion in UnitConversion.objects.filter(ingredient=instance):
                if unit_conversion.alternative_unit == new_default_unit:
                    unit_conversion.delete()
                else:
                    old_default_conv_factor = unit_conversion.default_conversion_factor
                    old_alternative_conv_factor = (
                        unit_conversion.alternative_conversion_factor
                    )
                    new_default_conversion_factor = (
                        old_default_conv_factor
                        * new_default_unit_conversion_default_factor
                    )
                    new_alternative_conversion_factor = (
                        old_alternative_conv_factor
                        * new_default_unit_conversion_alternative_factor
                    )
                    if (
                        abs(new_default_conversion_factor) > 1e-5
                        and abs(new_alternative_conversion_factor) > 1e-5
                    ):
                        for dec_power in itertools.count():
                            if (
                                abs(
                                    new_default_conversion_factor
                                    % (10 ** (dec_power + 1))
                                )
                                > 1e-5
                                or abs(
                                    new_alternative_conversion_factor
                                    % (10 ** (dec_power + 1))
                                )
                                > 1e-5
                            ):
                                new_default_conversion_factor *= 10**-dec_power
                                new_alternative_conversion_factor *= 10**-dec_power
                                break
                    unit_conversion.default_conversion_factor = (
                        new_default_conversion_factor
                    )
                    unit_conversion.alternative_conversion_factor = (
                        new_alternative_conversion_factor
                    )
                    unit_conversion.save()
            instance.default_unit = new_default_unit
        if unit_conversions is not None:
            for unit_conversion_data in unit_conversions:
                alternative_unit = unit_conversion_data["alternative_unit"]
                if alternative_unit != instance.default_unit:
                    try:
                        unit_conversion = UnitConversion.objects.get(
                            ingredient=instance, alternative_unit=alternative_unit
                        )
                        unit_conversion.default_conversion_factor = (
                            unit_conversion_data["default_conversion_factor"]
                        )
                        unit_conversion.alternative_conversion_factor = (
                            unit_conversion_data["alternative_conversion_factor"]
                        )
                        unit_conversion.save()
                    except UnitConversion.DoesNotExist:
                        UnitConversion.objects.create(
                            ingredient=instance, **unit_conversion_data
                        )
        instance.save()
        return instance


class QuantifiedIngredientSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()
    ingredient = IngredientShortSerializer()
    unit = UnitSerializer()

    class Meta:
        model = QuantifiedIngredient
        fields = ("id", "ingredient", "quantity", "unit", "updated_at")
        read_only_fields = (
            "id",
            "updated_at",
        )


class QuantifiedIngredientEditSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = QuantifiedIngredient
        fields = ("id", "ingredient", "quantity", "unit", "updated_at")
        read_only_fields = (
            "id",
            "updated_at",
        )


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = "__all__"


class RecipeImageFullSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = RecipeImage
        fields = "__all__"
        read_only_fields = (
            "id",
            "updated_at",
            "thumbnail_card",
            "thumbnail_plan",
            "image_width",
            "image_height",
            "thumbnail_card_width",
            "thumbnail_card_height",
            "thumbnail_plan_width",
            "thumbnail_plan_height",
        )


class RecipeImageSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = RecipeImage
        fields = (
            "id",
            "image",
            "thumbnail_card",
            "thumbnail_plan",
            "order",
            "updated_at",
            "image_width",
            "image_height",
            "thumbnail_card_width",
            "thumbnail_card_height",
            "thumbnail_plan_width",
            "thumbnail_plan_height",
        )
        read_only_fields = (
            "id",
            "updated_at",
            "thumbnail_plan",
            "thumbnail_card",
            "image_width",
            "image_height",
            "thumbnail_card_width",
            "thumbnail_card_height",
            "thumbnail_plan_width",
            "thumbnail_plan_height",
        )


class RecipeImageShortSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = RecipeImage
        fields = (
            "id",
            "image",
            "thumbnail_card",
            "thumbnail_plan",
            "updated_at",
            "image_width",
            "image_height",
            "thumbnail_card_width",
            "thumbnail_card_height",
            "thumbnail_plan_width",
            "thumbnail_plan_height",
        )
        read_only_fields = (
            "id",
            "thumbnail_card",
            "thumbnail_plan",
            "updated_at",
            "image_width",
            "image_height",
            "thumbnail_card_width",
            "thumbnail_card_height",
            "thumbnail_plan_width",
            "thumbnail_plan_height",
        )


class RecipeImageEditSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()

    class Meta:
        model = RecipeImage
        fields = ("id", "image", "order", "updated_at")
        read_only_fields = (
            "id",
            "updated_at",
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()
    first_image = RecipeImageShortSerializer(allow_null=True)

    class Meta:
        model = Recipe
        fields = ("id", "name", "preparation_time", "first_image", "updated_at")
        read_only_fields = (
            "id",
            "first_image",
            "updated_at",
        )


class RecipeFullSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()
    quantified_ingredients = QuantifiedIngredientSerializer(many=True)
    labels = LabelSerializer(many=True)
    recipe_images = RecipeImageSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "preparation_time",
            "source",
            "num_servings",
            "labels",
            "quantified_ingredients",
            "preparation_text",
            "recipe_images",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "updated_at",
        )


class RecipeEditSerializer(serializers.ModelSerializer):
    updated_at = TimestampField()
    quantified_ingredients = QuantifiedIngredientEditSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "preparation_time",
            "source",
            "num_servings",
            "labels",
            "quantified_ingredients",
            "preparation_text",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "updated_at",
        )

    def create(self, validated_data):
        labels_data = validated_data.pop("labels")
        quantified_ingredients_data = validated_data.pop("quantified_ingredients")
        recipe = Recipe.objects.create(
            **validated_data, request=self.context["request"]
        )
        for label_data in labels_data:
            recipe.labels.add(label_data)
        for quantified_ingredient_data in quantified_ingredients_data:
            QuantifiedIngredient.objects.create(
                recipe=recipe, **quantified_ingredient_data
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.preparation_time = validated_data.get(
            "preparation_time", instance.preparation_time
        )
        instance.source = validated_data.get("source", instance.source)
        instance.num_servings = validated_data.get(
            "num_servings", instance.num_servings
        )
        instance.preparation_text = validated_data.get(
            "preparation_text", instance.preparation_text
        )
        labels_data = validated_data.get("labels")
        if labels_data is not None:
            instance.labels.clear()
            for label_data in labels_data:
                instance.labels.add(label_data)
        quantified_ingredients_data = validated_data.get("quantified_ingredients")
        if quantified_ingredients_data is not None:
            for quantified_ingredient in instance.quantified_ingredients.all():
                quantified_ingredient.delete()
            QuantifiedIngredient.objects.bulk_create(
                [
                    QuantifiedIngredient(recipe=instance, **quantified_ingredient_data)
                    for quantified_ingredient_data in quantified_ingredients_data
                ]
            )
        instance.save()
        return instance


class PushSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PushSubscription
        fields = "__all__"


class PushSubscriptionEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = PushSubscription
        fields = "__all__"
        read_only_fields = ("endpoint",)
