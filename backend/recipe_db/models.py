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
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    category = models.ForeignKey(IngredientCategory, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=255)
    preparation_time = models.IntegerField()
    source = models.CharField(max_length=255)
    labels = models.ManyToManyField(Label, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class QuantifiedIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='quantified_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ingredient} in {self.recipe}"


class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_images')
    image = models.ImageField()
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
