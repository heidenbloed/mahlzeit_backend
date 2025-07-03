import urllib.parse

from django_filters.rest_framework import DjangoFilterBackend
from knox.views import LoginView as KnoxLoginView
from rest_framework import filters, mixins, parsers, viewsets
from rest_framework.authentication import BasicAuthentication

from .filters import RecipeFilter
from .models import (Ingredient, IngredientCategory, Label, PushSubscription,
                     QuantifiedIngredient, Recipe, RecipeImage, Unit)
from .serializers import *


class LoginView(KnoxLoginView):
    authentication_classes = [BasicAuthentication]


class RecipeView(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = RecipeFilter
    search_fields = ["name"]
    ordering_fields = ["name", "preparation_time", "updated_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "list":
            return RecipeShortSerializer
        if self.action == "retrieve":
            return RecipeFullSerializer
        else:
            return RecipeEditSerializer

    # def retrieve(self, request, *args, **kwargs):
    #     # time.sleep(1)
    #     return super().retrieve(request, *args, **kwargs)


class QuantifiedIngredientView(viewsets.ModelViewSet):
    serializer_class = QuantifiedIngredientSerializer
    queryset = QuantifiedIngredient.objects.all()
    pagination_class = None


class IngredientView(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = "__all__"
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "list":
            return IngredientShortSerializer
        if self.action == "retrieve":
            return IngredientFullSerializer
        else:
            return IngredientEditSerializer


class UnitView(viewsets.ReadOnlyModelViewSet):
    serializer_class = UnitSerializer
    queryset = Unit.objects.all()
    pagination_class = None


class IngredientCategoryView(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientCategorySerializer
    queryset = IngredientCategory.objects.all()
    pagination_class = None


class LabelView(viewsets.ReadOnlyModelViewSet):
    serializer_class = LabelSerializer
    queryset = Label.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = "__all__"
    ordering = ["name"]
    pagination_class = None


class RecipeImageView(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    parser_classes = (parsers.MultiPartParser,)
    serializer_class = RecipeImageFullSerializer
    queryset = RecipeImage.objects.all()


class RecipeImageViewDev(
    RecipeImageView, mixins.RetrieveModelMixin, mixins.ListModelMixin
):
    pagination_class = None


class PushSubscriptionView(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PushSubscriptionSerializer
    queryset = PushSubscription.objects.all()
    lookup_value_regex = r"[a-zA-Z0-9\-_.!~*'()%]+"

    def get_serializer_class(self):
        if self.action == "create":
            return PushSubscriptionSerializer
        else:
            return PushSubscriptionEditSerializer

    def get_object(self):
        if "pk" in self.kwargs or "endpoint" in self.kwargs:
            encoded_pk = self.kwargs.pop("pk", self.kwargs.pop("endpoint", None))
            decoded_pk = urllib.parse.unquote(encoded_pk)
            self.kwargs["pk"] = decoded_pk
        return super().get_object()


class PushSubscriptionViewDev(
    PushSubscriptionView, mixins.RetrieveModelMixin, mixins.ListModelMixin
):
    pass
