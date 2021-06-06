from django.db import models


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

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    category = models.ForeignKey(IngredientCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=255)
    preparation_time = models.IntegerField()
    source = models.CharField(max_length=255)
    labels = models.ManyToManyField(Label, blank=True)

    def __str__(self):
        return self.name


class QuantifiedIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='quantified_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()

    def __str__(self):
        return f"{self.ingredient} in {self.recipe}"
