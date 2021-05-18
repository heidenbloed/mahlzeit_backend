from django.db import models


class Unit(models.Model):
    name = models.CharField(max_length=50)
    short_form = models.CharField(max_length=5)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200)
    location_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name