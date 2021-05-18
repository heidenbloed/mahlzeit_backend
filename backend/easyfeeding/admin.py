from django.contrib import admin

# Register your models here.
from .models import Ingredient, Category, Unit

admin.site.register(Ingredient)
admin.site.register(Category)
admin.site.register(Unit)
