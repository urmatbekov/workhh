from django.contrib import admin

# Register your models here.
from image.models import Image, ImageHistory


@admin.register(ImageHistory)
class ImageHistoryAdminModel(admin.ModelAdmin):
    pass


class ImageHistoryInlineModel(admin.TabularInline):
    model = ImageHistory
    extra = 0


@admin.register(Image)
class ImageAdminModel(admin.ModelAdmin):
    inlines = [ImageHistoryInlineModel]
