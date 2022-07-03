import os.path

from django.db import models
from django.dispatch import receiver


class Unit(models.Model):
    short_form = models.CharField(max_length=255)

    def __str__(self):
        return self.short_form


class IngredientCategory(models.Model):
    name = models.CharField(max_length=255)
    location_index = models.IntegerField()

    def __str__(self):
        return self.name


class Label(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, default="default")

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    default_unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    category = models.ForeignKey(IngredientCategory, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UnitConversion(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='unit_conversions')
    alternative_unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    alternative_conversion_factor = models.FloatField()
    default_conversion_factor = models.FloatField()

    def __str__(self):
        return f"{self.alternative_unit.short_form} to default unit conversion for {self.ingredient.name}"


class Recipe(models.Model):
    name = models.CharField(max_length=255)
    preparation_time = models.PositiveIntegerField()
    source = models.CharField(max_length=255, blank=True)
    num_servings = models.PositiveIntegerField()
    labels = models.ManyToManyField(Label, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def first_image(self):
        images = RecipeImage.objects.filter(recipe=self).order_by("order")
        if len(images) > 0:
            return images[0]
        else:
            return None

    def __str__(self):
        return self.name


class QuantifiedIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='quantified_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def unit_conversion_factor(self):
        if self.unit == self.ingredient.default_unit:
            return 1.0
        else:
            conversion = self.unit_conversion
            if conversion is not None:
                return conversion.default_conversion_factor / conversion.alternative_conversion_factor
            else:
                return None

    @property
    def unit_conversion(self):
        try:
            return UnitConversion.objects.get(ingredient=self.ingredient, alternative_unit=self.unit)
        except UnitConversion.DoesNotExist:
            return None

    def __str__(self):
        return f"{self.ingredient} in {self.recipe}"


class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_images')
    image = models.ImageField()
    order = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image of {self.recipe}"


@receiver(models.signals.post_delete, sender=RecipeImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=RecipeImage)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = RecipeImage.objects.get(pk=instance.pk).image
    except RecipeImage.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
