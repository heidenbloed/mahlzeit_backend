from django import forms
from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm

# Register your models here.
from .models import (Ingredient, IngredientCategory, Label, PushSubscription,
                     QuantifiedIngredient, Recipe, RecipeImage, Unit,
                     UnitConversion)


class PushMessageForm(ActionForm):
    title = forms.CharField(required=True)
    body = forms.CharField(required=False)
    href = forms.CharField(required=False)
    image = forms.CharField(required=False)
    tag = forms.CharField(required=False)
    silent = forms.BooleanField(required=False, initial=True)


class PushSubscriptionAdmin(admin.ModelAdmin):
    actions = ["push_message_to_subscription"]
    action_form = PushMessageForm

    @admin.action
    def push_message_to_subscription(self, request, queryset):
        title = request.POST["title"]
        body = request.POST["body"] if "body" in request.POST else None
        href = request.POST["href"] if "href" in request.POST else None
        image = request.POST["image"] if "image" in request.POST else None
        tag = request.POST["tag"] if "tag" in request.POST else None
        silent = request.POST["silent"] == "on" if "silent" in request.POST else True
        for push_subscription in queryset:
            push_subscription.push_message(
                title=title, body=body, href=href, image=image, tag=tag, silent=silent
            )
        self.message_user(request, "Message was pushed successfully.", messages.SUCCESS)


admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(QuantifiedIngredient)
admin.site.register(IngredientCategory)
admin.site.register(Unit)
admin.site.register(Label)
admin.site.register(RecipeImage)
admin.site.register(UnitConversion)
admin.site.register(PushSubscription, PushSubscriptionAdmin)
