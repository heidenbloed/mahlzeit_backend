import io

from django.core.files.base import ContentFile
from django.db import models
from django.db.models.fields.files import ImageFieldFile
from PIL import Image, ImageOps


class WebPFieldFile(ImageFieldFile):

    def save(self, name, content, save=True):
        content.file.seek(0)
        image = Image.open(content.file)
        image = ImageOps.exif_transpose(image)
        image_bytes = io.BytesIO()
        image.save(fp=image_bytes, format="WEBP")
        image_content_file = ContentFile(content=image_bytes.getvalue())
        super().save(name, image_content_file, save)


class WebPField(models.ImageField):
    attr_class = WebPFieldFile
