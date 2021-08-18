from django.contrib import admin

# Register your models here.
from .models import Recipe, Ingredient, QuantifiedIngredient, IngredientCategory, Unit, Label, RecipeImage

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(QuantifiedIngredient)
admin.site.register(IngredientCategory)
admin.site.register(Unit)
admin.site.register(Label)
admin.site.register(RecipeImage)
