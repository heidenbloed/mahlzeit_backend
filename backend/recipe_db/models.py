import io
import os.path
import uuid

from PIL import Image

from django.db import models
from django.dispatch import receiver
from django.core.files.base import ContentFile
from django.conf import settings
from .fields import WebPField


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


def generate_image_path(instance, filename):
    return os.path.join("recipe_images", f"{uuid.uuid4().hex}.webp")


class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_images')
    image = WebPField(upload_to=generate_image_path)
    thumbnail_card = models.ImageField(blank=True, null=True, editable=False)
    thumbnail_plan = models.ImageField(blank=True, null=True, editable=False)
    order = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def make_thumbnails(self):
        image_name = self.image.name
        image_name, _ = os.path.splitext(image_name)

        thumbnail_card_name = f"{image_name}_thumb_card.webp"
        thumbnail_plan_name = f"{image_name}_thumb_plan.webp"

        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, thumbnail_card_name)):
            thumbnail_card = Image.open(self.image.path)
            thumbnail_plan = thumbnail_card.copy()

            thumbnail_card = self.crop_image_to_aspect(thumbnail_card, 448. / 224.)
            thumbnail_card.thumbnail((448, 224), Image.BICUBIC)
            thumbnail_plan = self.crop_image_to_aspect(thumbnail_plan, 149. / 160.)
            thumbnail_plan.thumbnail((149, 160), Image.BICUBIC)

            thumbnail_card_io = io.BytesIO()
            thumbnail_card.save(thumbnail_card_io, "WEBP")
            thumbnail_card_io.seek(0)
            self.thumbnail_card.save(thumbnail_card_name, ContentFile(thumbnail_card_io.read()), save=True)
            thumbnail_card_io.close()

            thumbnail_plan_io = io.BytesIO()
            thumbnail_plan.save(thumbnail_plan_io, "WEBP")
            thumbnail_plan_io.seek(0)
            self.thumbnail_plan.save(thumbnail_plan_name, ContentFile(thumbnail_plan_io.read()), save=True)
            thumbnail_plan_io.close()

    @staticmethod
    def crop_image_to_aspect(image: Image, aspect: float) -> Image:
        if image.width / image.height > aspect:
            new_width = int(image.height * aspect)
            new_height = image.height
        else:
            new_width = image.width
            new_height = int(image.width / aspect)
        return image.crop((
            0.5 * (image.width - new_width),
            0.5 * (image.height - new_height),
            0.5 * (image.width - new_width) + new_width,
            0.5 * (image.height - new_height) + new_height)
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.make_thumbnails()

    def __str__(self):
        return f"Image of {self.recipe}"


@receiver(models.signals.post_delete, sender=RecipeImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    for image in [instance.image, instance.thumbnail_card, instance.thumbnail_plan]:
        if image:
            if os.path.isfile(image.path):
                os.remove(image.path)


@receiver(models.signals.pre_save, sender=RecipeImage)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_instance = RecipeImage.objects.get(pk=instance.pk)
    except RecipeImage.DoesNotExist:
        return False

    old_file = old_instance.image
    new_file = instance.image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
        if os.path.isfile(old_instance.thumbnail_card.path):
            os.remove(old_instance.thumbnail_card.path)
        if os.path.isfile(old_instance.thumbnail_plan.path):
            os.remove(old_instance.thumbnail_plan.path)
